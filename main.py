import os
import sys
import faulthandler

# Set stability/env flags BEFORE any heavy ML/DB imports
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # Load global light stylesheet if present
    try:
        with open("styles.qss", "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except Exception:
        pass
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
