import os
import sys
import faulthandler
import json

from backend_api import DEFAULT_API_BASE_URL, resolve_api_base_url

# Limit native-library worker threads before document-processing imports.
os.environ.setdefault("OMP_NUM_THREADS", "1")

try:
    if getattr(sys, "stderr", None):
        faulthandler.enable()
    else:
        log_dir = os.path.join(os.getenv("APPDATA") or os.getcwd(), "AI Document Analyzer")
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            pass
        log_path = os.path.join(log_dir, "app.log")
        try:
            log_file = open(log_path, "a", encoding="utf-8", buffering=1)
            sys.stderr = log_file
            sys.stdout = log_file
            faulthandler.enable(file=log_file)
        except Exception:
            pass
except Exception:
    pass

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QFile
from PyQt6.QtGui import QIcon
from main_window import MainWindow
from auth import refresh as auth_refresh, get_stored_refresh_token

def _asset_path(*parts) -> str:
    """Resolve a path under the bundled assets dir for both source runs and PyInstaller EXEs."""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def _load_api_base_url() -> str:
    """Compatibility wrapper over the shared backend URL resolver."""
    return resolve_api_base_url()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(_asset_path("assets", "app-icon-logo.jpeg")))

    # Resolve API base URL and attempt silent sign-in via refresh token
    api_base = _load_api_base_url()
    signed_in = False
    try:
        if get_stored_refresh_token():
            auth_refresh(api_base)
            signed_in = True
    except Exception:
        signed_in = False

    window = MainWindow()
    window.show()
    if not signed_in:
        try:
            window.show_login_overlay(api_base)
        except Exception:
            pass
    sys.exit(app.exec())
