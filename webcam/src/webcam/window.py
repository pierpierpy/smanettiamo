"""Open the camera page in its own window (a Chrome-style app window, falling back to the default browser)."""
import shutil
import subprocess
import sys
import webbrowser
from pathlib import Path

MAC_BROWSERS = ["Google Chrome", "Brave Browser", "Microsoft Edge", "Chromium"]
LINUX_BROWSERS = ["google-chrome", "chromium", "chromium-browser", "brave-browser", "microsoft-edge"]


def app_window_command(url: str, size: str = "960,720"):
    """Command that opens `url` as a chrome-less app window, or None if no Chromium-based browser is found."""
    args = [f"--app={url}", f"--window-size={size}"]
    if sys.platform == "darwin":
        for name in MAC_BROWSERS:
            if Path(f"/Applications/{name}.app").exists():
                return ["open", "-na", name, "--args", *args]
    else:
        for exe in LINUX_BROWSERS:
            if shutil.which(exe):
                return [exe, *args]
    return None


def open_window(url: str):
    cmd = app_window_command(url)
    if cmd:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        webbrowser.open(url)
