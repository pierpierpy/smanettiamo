"""Webcam server: reads frames from a camera source and serves them over HTTP on localhost.

    uv run webcam                       # default source from webcam/webcam.toml, opens the window
    uv run webcam --source mac          # a named source from webcam.toml
    uv run webcam --url http://<phone-ip>:4747/video
    uv run webcam --device 0            # built-in / USB camera through OpenCV

Endpoints:
    /            a page with only the video (cam.html), also usable inside a notebook
    /frame.jpg   the latest frame (what notebooks read, see webcam.grab_frame)
    /stream      multipart MJPEG stream
"""
import argparse
import errno
import threading
import time
import tomllib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .sources import make_source
from .window import open_window

HERE = Path(__file__).parent
DEFAULT_CONFIG = HERE.parents[1] / "webcam.toml"      # webcam/webcam.toml, next to pyproject.toml
PAGE = HERE / "cam.html"


class FrameStore:
    """Latest frame, shared between the camera thread and the HTTP handlers."""

    def __init__(self):
        self.jpg = None
        self.n = 0
        self.error = None
        self.cond = threading.Condition()

    def publish(self, jpg: bytes):
        with self.cond:
            self.jpg, self.n, self.error = jpg, self.n + 1, None
            self.cond.notify_all()


def read_camera(source, store: FrameStore):
    """Feed the store forever; if the camera drops, wait and reconnect."""
    while True:
        try:
            for jpg in source.frames():
                store.publish(jpg)
        except Exception as e:  # noqa: BLE001 - any camera failure means: retry
            store.error = f"{type(e).__name__}: {e}"
        time.sleep(2)


def make_handler(store: FrameStore):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            url = urlparse(self.path)
            if url.path in ("/", "/cam.html"):                       # the page
                self.reply(PAGE.read_bytes(), "text/html; charset=utf-8")
            elif url.path.startswith("/frame"):                      # one frame
                self.reply(store.jpg, "image/jpeg")
            elif url.path == "/stream":                              # streaming: each frame once
                self.stream()
            else:
                self.send_error(404)

        def reply(self, body: bytes, content_type: str):
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def stream(self):
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=f")
            self.end_headers()
            n = 0
            try:
                while True:
                    with store.cond:
                        store.cond.wait_for(lambda: store.n != n)
                        jpg, n = store.jpg, store.n
                    self.wfile.write(b"--f\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n" % len(jpg) + jpg + b"\r\n")
            except (BrokenPipeError, ConnectionResetError):
                pass

        def log_message(self, *a):
            pass

    return Handler


def load_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def pick_source(args, cfg: dict):
    """Command line first (--url, --device, --source), then the default in the config file."""
    if args.url:
        return {"type": "mjpeg", "url": args.url}
    if args.device is not None:
        return {"type": "opencv", "device": args.device}
    sources = cfg.get("sources", {})
    name = args.source or cfg.get("default")
    if not name:
        raise SystemExit(f"no source chosen: pass --source/--url/--device or set `default` in {args.config}")
    if name not in sources:
        raise SystemExit(f"source {name!r} is not defined in {args.config} (available: {', '.join(sources) or 'none'})")
    return sources[name]


def main():
    ap = argparse.ArgumentParser(description="Serve a camera over HTTP on localhost.")
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="config file (default: webcam/webcam.toml)")
    ap.add_argument("--source", help="name of a source defined in the config file")
    ap.add_argument("--url", help="MJPEG url, e.g. the DroidCam address")
    ap.add_argument("--device", type=lambda s: int(s) if s.isdigit() else s, help="OpenCV device index or path, e.g. 0")
    ap.add_argument("--port", type=int, help="default 8090")
    ap.add_argument("--no-window", action="store_true", help="do not open the window")
    args = ap.parse_args()

    cfg = load_config(args.config)
    source = make_source(pick_source(args, cfg))
    port = args.port or cfg.get("port", 8090)

    store = FrameStore()
    try:                                                   # bind first: fail fast if the port is taken
        server = ThreadingHTTPServer(("127.0.0.1", port), make_handler(store))
    except OSError as e:
        if e.errno != errno.EADDRINUSE:
            raise
        raise SystemExit(
            f"port {port} is already in use: another webcam server (or the old cam.py) is probably still running.\n"
            f"  see who: lsof -nP -iTCP:{port} -sTCP:LISTEN\n"
            f"  then stop it (kill <PID>), or use another port: webcam --port {port + 1}"
        )

    threading.Thread(target=read_camera, args=(source, store), daemon=True).start()
    print(f"waiting for the first frame from {source} ...")
    deadline = time.time() + 20
    try:
        with store.cond:
            while store.jpg is None and time.time() < deadline:
                store.cond.wait(timeout=1)
    except KeyboardInterrupt:
        raise SystemExit("\nstopped")
    if store.jpg is None:
        server.server_close()
        raise SystemExit(f"no frame from {source} after 20 s ({store.error or 'no answer'})")

    url = f"http://localhost:{port}/"
    print(f"camera on {url}  (Ctrl+C to stop)")
    if not args.no_window and cfg.get("window", True):
        open_window(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()


if __name__ == "__main__":
    main()
