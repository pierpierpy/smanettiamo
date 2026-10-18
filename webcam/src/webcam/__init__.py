"""Generic webcam: a server that shows a camera, and a small client for notebooks.

From a notebook (the normal way, no terminal needed):
    from webcam import start, show, grab_frame
    start()                  # starts the server: webcam/webcam.toml if it exists, else the built-in camera
    start(device=0)          # built-in / USB camera
    start(url="http://<phone-ip>:4747/video")      # DroidCam
    show()                   # the live video, as HTML inside the notebook
    grab_frame()             # one frame, as a PIL image
    stop()                   # stops the server (it also stops when the kernel ends)

From a terminal (same server, optional):
    uv run webcam --device 0        # also: --source <name from webcam.toml>, --url <mjpeg url>, --port <n>

Two addresses, because two different programs talk to the server:
    URL          used by the kernel (grab_frame). Default http://localhost:8090, override with WEBCAM_URL.
    BROWSER_URL  used by the browser (show). Default /proxy/<port>, i.e. through JupyterLab itself
                 (jupyter-server-proxy), so it also works when the browser is on another machine and only
                 reaches JupyterLab (e.g. an SSH tunnel on port 8888).
                 Override with WEBCAM_BROWSER_URL, e.g. http://localhost:8090 when the browser is on the same machine.
"""
import atexit
import io
import os
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlparse

URL = os.environ.get("WEBCAM_URL", "http://localhost:8090").rstrip("/")
BROWSER_URL = os.environ.get("WEBCAM_BROWSER_URL", f"/proxy/{urlparse(URL).port or 80}").rstrip("/")

_proc = None          # the server started by start(), if any


def grab_frame(url: str = URL):
    """The latest frame of the camera, as an RGB PIL image."""
    from PIL import Image

    with urllib.request.urlopen(f"{url}/frame.jpg", timeout=10) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGB")


def show(width: int = 640, height: int = 480, url: str = BROWSER_URL):
    """The live video as an HTML page inside the notebook (return value of the cell, or use display())."""
    from IPython.display import IFrame

    return IFrame(f"{url}/", width=width, height=height)


def _is_up(url: str) -> bool:
    try:
        grab_frame(url)
        return True
    except Exception:  # noqa: BLE001 - not reachable, or no frame yet
        return False


def start(source: str = None, url: str = None, device=None, timeout: float = 40):
    """Start the camera server in the background and wait for the first frame.

    Pick the camera with one of: source (a name in webcam/webcam.toml), url (MJPEG, e.g. DroidCam),
    device (OpenCV index, 0 = built-in camera). With nothing given: the default in webcam/webcam.toml,
    or the built-in camera if that file does not exist.
    Does nothing if a server already answers on URL.
    """
    global _proc
    if _is_up(URL):
        print(f"camera already running on {URL}")
        return
    if _proc is not None and _proc.poll() is None:
        stop()

    from .cam import DEFAULT_CONFIG

    args = []
    if url:
        args += ["--url", url]
    elif device is not None:
        args += ["--device", str(device)]
    elif source:
        args += ["--source", source]
    elif not DEFAULT_CONFIG.exists():
        args += ["--device", "0"]

    port = urlparse(URL).port or 80
    log = tempfile.NamedTemporaryFile("w+", prefix="webcam-", suffix=".log", delete=False)
    _proc = subprocess.Popen(
        [sys.executable, "-m", "webcam", "--no-window", "--port", str(port), *args],
        stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
    )
    atexit.register(stop)

    deadline = time.time() + timeout
    while time.time() < deadline:
        if _proc.poll() is not None:                     # the server stopped: show why
            break
        if _is_up(URL):
            print(f"camera on {URL}  (stop it with webcam.stop())")
            return
        time.sleep(0.5)

    log.flush()
    lines = list(dict.fromkeys(Path(log.name).read_text().strip().splitlines()))     # drop repeated lines
    text = "\n".join(lines[-8:])
    stop()
    hint = ("\nOn macOS: allow the camera for the app that runs Jupyter (System Settings > Privacy & Security > Camera), "
            "then run start() again.")
    raise RuntimeError(f"the camera did not start:\n{text or '(no output)'}{hint}")


def stop():
    """Stop the server started by start()."""
    global _proc
    if _proc is not None and _proc.poll() is None:
        _proc.terminate()
        try:
            _proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _proc.kill()
    _proc = None
