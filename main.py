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

faulthandler.enable()

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
