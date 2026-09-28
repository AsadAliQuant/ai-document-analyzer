import os
import sys
import faulthandler
import json

# Set stability/env flags BEFORE any heavy ML/DB imports
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
# Never allow background model downloads in packaged builds
if getattr(sys, "frozen", False):
    os.environ["AIDA_RUNTIME_PREFETCH"] = "0"
# Strongly prefer Local (Python) Chroma API over Rust backend on Windows
os.environ.setdefault("CHROMA_DISABLE_TELEMETRY", "true")
os.environ.setdefault("POSTHOG_DISABLED", "1")

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

DEFAULT_API_BASE_URL = "https://ssma.sa/console/api"


def _asset_path(*parts) -> str:
    """Resolve a path under the bundled assets dir for both source runs and PyInstaller EXEs."""
    if getattr(sys, "frozen", False):
        base_dir = getattr(sys, "_MEIPASS", None) or os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)


def _load_api_base_url() -> str:
    # 1. Prefer user-specific config in %APPDATA% if present
    try:
        appdata = os.getenv("APPDATA") or os.path.expanduser("~")
        cfg_dir = os.path.join(appdata, "AI Document Analyzer")
        cfg_path = os.path.join(cfg_dir, "config.json")
        if os.path.exists(cfg_path):
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            base = cfg.get("API_BASE_URL")
            if base:
                return str(base).rstrip("/")
    except Exception:
        pass
    # 2. Check bundled config.json inside PyInstaller _MEIPASS (--onefile extracts here)
    try:
        bundled_cfg = _asset_path("config.json")
        if os.path.exists(bundled_cfg):
            with open(bundled_cfg, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            base = cfg.get("API_BASE_URL")
            if base:
                return str(base).rstrip("/")
    except Exception:
        pass
    # 3. Fallback to config.json in CWD (development runs)
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            cfg = json.load(f)
        base = cfg.get("API_BASE_URL") or DEFAULT_API_BASE_URL
        return str(base).rstrip("/")
    except Exception:
        return DEFAULT_API_BASE_URL


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon(_asset_path("assets", "app-icon-logo.jpeg")))
    # Load global light stylesheet if present
    try:
        with open("styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass
    
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
