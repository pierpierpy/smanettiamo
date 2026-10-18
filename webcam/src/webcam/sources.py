"""Camera sources. Each source yields JPEG frames (bytes) from `frames()`.

Add a new camera type by writing a class with a `frames()` generator and
registering it in SOURCES.
"""
import urllib.request
from typing import Iterator


class MjpegSource:
    """An MJPEG stream over HTTP (DroidCam, IP cameras, ...)."""

    def __init__(self, url: str):
        self.url = url

    def __str__(self):
        return f"mjpeg {self.url}"

    def frames(self) -> Iterator[bytes]:
        buf = b""
        with urllib.request.urlopen(self.url, timeout=10) as r:
            while True:
                chunk = r.read1(65536)
                if not chunk:
                    raise ConnectionError("stream closed by the camera")
                buf += chunk
                start = buf.find(b"\xff\xd8")                              # start of a JPEG
                end = buf.find(b"\xff\xd9", start + 2) if start != -1 else -1  # end of the JPEG
                if end != -1:
                    yield buf[start:end + 2]
                    buf = buf[end + 2:]


class OpenCVSource:
    """Any device or file OpenCV can open: the built-in webcam (device=0), USB cameras, RTSP urls, video files."""

    def __init__(self, device=0, quality: int = 90):
        self.device = device
        self.quality = quality

    def __str__(self):
        return f"opencv {self.device}"

    def frames(self) -> Iterator[bytes]:
        import cv2  # imported here so the mjpeg source works without OpenCV

        cap = cv2.VideoCapture(self.device)
        try:
            if not cap.isOpened():
                raise ConnectionError(f"cannot open camera {self.device!r}")
            while True:
                ok, frame = cap.read()
                if not ok:
                    raise ConnectionError(f"camera {self.device!r} stopped delivering frames")
                ok, jpg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
                if ok:
                    yield jpg.tobytes()
        finally:
            cap.release()


SOURCES = {"mjpeg": MjpegSource, "opencv": OpenCVSource}


def make_source(cfg: dict):
    """Build a source from a config table, e.g. {"type": "mjpeg", "url": "http://..."}."""
    cfg = dict(cfg)
    kind = cfg.pop("type", None)
    if kind not in SOURCES:
        raise SystemExit(f"unknown source type {kind!r}, choose one of: {', '.join(SOURCES)}")
    return SOURCES[kind](**cfg)
