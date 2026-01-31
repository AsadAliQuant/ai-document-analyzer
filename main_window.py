from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, QThread, QObject, pyqtSignal, pyqtSlot, QTimer, Qt, QRect, QRectF, QMarginsF, QSize
from PyQt6.QtGui import QIcon, QImage, QPainter, QPdfWriter, QPageSize, QTextDocument
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QGroupBox,
    QHBoxLayout,
    QLineEdit,
    QGraphicsOpacityEffect,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSystemTrayIcon,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
import json
import re
import os
import shutil
import math
import hashlib
import sys
from ui_main_window import Ui_MainWindow
from settings_window import SettingsWindow
from typing import Optional, List
import base64
import mimetypes
import locale
from startup_helper import InitializationWorker, LoadingOverlayMixin
from lock_manager import LockManager
from lock_overlay import LockOverlay
from login_overlay import LoginOverlay
from auth import AuthState, clear_tokens

# Windows theme detection
def is_windows_dark_mode() -> bool:
    """Detect if Windows is in dark mode via registry."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return value == 0  # 0 = dark mode, 1 = light mode
    except Exception:
        return False  # Default to light mode if detection fails

# Optional imports for file text extraction
try:
    from PyPDF2 import PdfReader  # type: ignore
except ImportError:
    PdfReader = None  # type: ignore

try:
    from docx import Document  # type: ignore
except Exception:
    Document = None  # type: ignore

try:
    import google.generativeai as genai  # type: ignore
except Exception:
    genai = None  # type: ignore

try:
    import ollama as ollama_client  # Python client
except Exception:
    ollama_client = None

try:
    from PIL import Image  # type: ignore
    _ocr_available = True
except Exception:
    Image = None  # type: ignore
    _ocr_available = False


class MainWindow(LoadingOverlayMixin, QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self._selected_file_path: str = ""
        
        # Create loading overlay
        self._loading_overlay = None
        self._loading_label = None
        self._loading_timer = None
        self._loading_dots = 0
        self._init_in_progress = True
        self._login_overlay = None
        
        # Show loading overlay immediately
        self._keep_loading_message_constant = True
        loading_text = "Loading AI Document Analyzer"
        self._create_loading_overlay()
        self._show_loading_overlay(loading_text)
        
        # Disable all UI during loading
        self.setEnabled(False)
        
        # Initialize lock system
        self.lock_manager = LockManager(
            csv_url="https://docs.google.com/spreadsheets/d/e/2PACX-1vRaSrw4NtfrP1soUfYrAVGv7WtJp8jEaG77LNgOGyW9pBNE4xyqioEvDMKDQDcvseJLnjHUYiCITng7/pub?output=csv"
        )
        self.lock_overlay = LockOverlay(self)
        self.lock_manager.lock_status_changed.connect(self._on_lock_status_changed)
        self.lock_manager.lock_message_changed.connect(self._on_lock_message_changed)
        
        # Show overlay if already locked on startup
        if self.lock_manager.get_current_status():
            self.lock_overlay.set_custom_message(self.lock_manager.get_lock_message())
            self.lock_overlay.show_overlay()

        # Settings Window
        self.settings_window = SettingsWindow(self)
        # Language/status state
        self._current_lang = "en"
        self._last_status_text = "Ready"
        # Default typing label base
        self._typing_label_base = "Assistant is typing"
        self._offline_state: dict = {}

        # System tray icon for notifications
        self.tray_icon = None
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray_icon = QSystemTrayIcon(self)
            try:
                self.tray_icon.setIcon(QIcon("assets/logo.png"))
            except Exception:
                pass
            self.tray_icon.setVisible(True)

        # Sidebar toggle state and animation setup



        self.sidebar_visible = False
        self.sidebar_expanded_width = 240
        self.ui.sidebarPanel.setMinimumWidth(0)
        self.ui.sidebarPanel.setMaximumWidth(self.sidebar_expanded_width)
        self.sidebar_animation = QPropertyAnimation(self.ui.sidebarPanel, b"maximumWidth")
        self.sidebar_animation.setDuration(250)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)


        # Sidebar toggle state and animation setup 
        # - change/remove this to show the sidebar menu again
        self.sidebar_visible = False                      # mark as collapsed
        self.sidebar_expanded_width = 240
        self.ui.sidebarPanel.setMinimumWidth(0)
        self.ui.sidebarPanel.setMaximumWidth(0)           # collapse to 0 on startup
        # Optional: completely hide the widget (no space taken)
        # self.ui.sidebarPanel.setVisible(False)

        # - change/remove this to show the sidebar menu again

        # Connect buttons
        # Old external choose file button removed; hook internal dropArea browse
        self.ui.analyzeButton.clicked.connect(self.analyze_document)
        
        # Apply initial theme-aware button style and set up theme change detection
        self._apply_analyze_button_theme()
        self._theme_check_timer = QTimer(self)
        self._theme_check_timer.timeout.connect(self._check_theme_change)
        self._theme_check_timer.start(2000)  # Check every 2 seconds
        self._last_dark_mode = is_windows_dark_mode()
        self.ui.settingsButton.clicked.connect(self.open_settings)
        # Top settings mirrors sidebar settings
        if hasattr(self.ui, 'topSettingsButton'):
            self.ui.topSettingsButton.clicked.connect(self.open_settings)
        self.ui.exportButton.clicked.connect(self.export_pdf)
        if hasattr(self.ui, 'copySummaryButton'):
            self.ui.copySummaryButton.clicked.connect(self.copy_summary_to_clipboard)
        self.ui.toggleSidebarButton.clicked.connect(self.toggle_sidebar)
        if hasattr(self.ui, 'refreshModelsButton'):
            self.ui.refreshModelsButton.clicked.connect(self.refresh_models)

        # Connect DropArea signal if available
        if hasattr(self.ui, 'dropArea'):
            try:
                self.ui.dropArea.fileDropped.connect(self._on_file_dropped)
                self.ui.dropArea.browseRequested.connect(self.choose_file)
            except Exception:
                pass

        # Background refresh state (init before any refresh call)
        self._refresh_thread = None
        self._refresh_worker = None
        self._is_refreshing = False
        self._settings_open = False

        # Model source and list
        # Config lives in %APPDATA%/AI Document Analyzer/config.json (copied from working dir if present on first run)
        self.app_config_dir = self._appdata_config_dir()
        try:
            os.makedirs(self.app_config_dir, exist_ok=True)
        except Exception:
            pass
        self.config_path = os.path.join(self.app_config_dir, "config.json")
        self.offline_state_path = os.path.join(self.app_config_dir, "offline_state.json")
        self._offline_state = self._load_offline_state()
        self._apply_offline_state_to_settings()

        # Initialize attributes that will be set by background worker (with safe defaults)
        self.large_doc_manager = None
        self._qa_vector_doc_key = ""
        self._pending_analysis_params = None
        self._processing_thread = None
        self._processing_worker = None
        self._ocr_reader = None
        self.online_models_gemini = []

        # Defer heavy initialization to background thread
        self._init_thread = QThread(self)
        self._init_worker = InitializationWorker(self)
        self._init_worker.moveToThread(self._init_thread)
        self._init_thread.started.connect(self._init_worker.run)
        self._init_worker.progress.connect(self._on_init_progress)
        self._init_worker.offline_progress.connect(self._on_offline_progress)
        self._init_worker.offline_state_ready.connect(self._on_offline_state_ready)
        self._init_worker.finished.connect(self._on_init_finished)
        self._init_worker.finished.connect(self._init_thread.quit)
        self._init_worker.finished.connect(self._init_worker.deleteLater)
        self._init_thread.finished.connect(self._init_thread.deleteLater)

        # Start initialization in background after a short delay (allow UI to paint)
        QTimer.singleShot(100, self._init_thread.start)

        # Analyze button loader state
        self._analyze_loader_timer = QTimer(self)
        self._analyze_loader_timer.setInterval(300)
        self._analyze_loader_timer.timeout.connect(self._tick_analyze_loader)
        self._analyze_loader_phase = 0
        self._analyze_button_base = self._get_analyze_button_text()
        self._analysis_thread = None
        self._analysis_worker = None
        # NOTE: Refresh state is initialized earlier; do not reset here to avoid
        # losing in-flight refresh state or leaving UI stuck in loading.

        # --- Q&A Chat UI (below Export button) ---
        self._last_summary_text: str = ""
        self._last_input_text_for_qa: str = ""
        self._qa_document_text: str = ""
        self._current_doc_key: str = ""
        self._qa_thread = None
        self._qa_worker = None
        self._qa_messages = []  # list of {role: 'user'|'assistant', content: str}
        self._last_summary_json = None  # parsed JSON dict when available

        self.ui.qaGroup = QGroupBox("Q&A Chat")
        qa_group_layout = QVBoxLayout(self.ui.qaGroup)
        qa_group_layout.setContentsMargins(8, 8, 8, 8)

        self.ui.chatHistoryBrowser = QTextBrowser()
        self.ui.chatHistoryBrowser.setOpenExternalLinks(True)
        qa_group_layout.addWidget(self.ui.chatHistoryBrowser)

        # Typing indicator label (hidden by default)
        self.ui.typingLabel = QLabel("")
        self.ui.typingLabel.setVisible(False)
        qa_group_layout.addWidget(self.ui.typingLabel)

        qa_controls = QWidget()
        qa_controls_layout = QHBoxLayout(qa_controls)
        qa_controls_layout.setContentsMargins(0, 0, 0, 0)

        # Removed chat context dropdown per requirement
        self.ui.questionLineEdit = QLineEdit()
        self.ui.questionLineEdit.setPlaceholderText("Ask a question about the summary...")
        self.ui.sendQuestionButton = QPushButton("Send")
        self.ui.clearChatButton = QPushButton("Clear")

        qa_controls_layout.addWidget(self.ui.questionLineEdit, 1)
        qa_controls_layout.addWidget(self.ui.sendQuestionButton)
        qa_controls_layout.addWidget(self.ui.clearChatButton)
        qa_group_layout.addWidget(qa_controls)

        # Image to PDF button (hidden by default, shown only if selected file is an image)
        self.ui.saveImageAsPdfButton = QPushButton("Save IMAGE as PDF")
        self.ui.saveImageAsPdfButton.setVisible(False)
        self.ui.saveImageAsPdfButton.clicked.connect(self._save_image_as_pdf)
        if hasattr(self.ui, 'rightLayout'):
            self.ui.rightLayout.addWidget(self.ui.saveImageAsPdfButton)

        # Insert just below the Export button in the right panel
        if hasattr(self.ui, 'rightLayout'):
            self.ui.rightLayout.addWidget(self.ui.qaGroup)

        # Disabled until a summary is generated
        self._qa_opacity_effect = QGraphicsOpacityEffect(self.ui.qaGroup)
        try:
            self.ui.qaGroup.setGraphicsEffect(self._qa_opacity_effect)
        except Exception:
            pass
        self.ui.questionLineEdit.returnPressed.connect(self._send_question)
        self.ui.sendQuestionButton.clicked.connect(self._send_question)
        self.ui.clearChatButton.clicked.connect(self._clear_chat)
        # Typing indicator timer for Q&A
        self._qa_typing_timer = QTimer(self)
        self._qa_typing_timer.setInterval(300)
        self._qa_typing_timer.timeout.connect(self._tick_qa_typing_indicator)
        self._qa_typing_phase = 0

        # Ensure UI is localized to current runtime language
        self.apply_language(getattr(self, "_current_lang", "en"))
        
        self._api_base_url = ""
        self._user_strip = QWidget()
        _u_layout = QHBoxLayout(self._user_strip)
        _u_layout.setContentsMargins(0, 0, 0, 0)
        _u_layout.setSpacing(6)
        self._user_label = QLabel("")
        self._logout_button = QPushButton("LOGOUT")
        try:
            self._logout_button.setFlat(True)
        except Exception:
            pass
        try:
            self._logout_button.setStyleSheet(
                "QPushButton { background-color: #B71C1C; color: white; border: 1px solid #7F0000; "
                "border-radius: 4px; padding: 4px 10px; } "
                "QPushButton:hover { background-color: #C62828; } "
                "QPushButton:pressed { background-color: #8E0000; }"
            )
        except Exception:
            pass
        self._logout_button.clicked.connect(self._on_logout_clicked)
        _u_layout.addWidget(self._user_label)
        _u_layout.addWidget(self._logout_button)
        try:
            if hasattr(self.ui, 'statusbar'):
                self.ui.statusbar.addPermanentWidget(self._user_strip)
        except Exception:
            pass
        self._update_user_strip()
        
    def show_login_overlay(self, base_url: str) -> None:
        try:
            if hasattr(self, "_loading_overlay") and self._loading_overlay and self._loading_overlay.isVisible():
                self._hide_loading_overlay()
        except Exception:
            pass
        if not getattr(self, "_login_overlay", None):
            self._login_overlay = LoginOverlay(base_url, self)
            try:
                self._login_overlay.logged_in.connect(self._on_login_success)
            except Exception:
                pass
        self._api_base_url = base_url or getattr(self, "_api_base_url", "")
        try:
            self._login_overlay.show_overlay()
            # Start animated loading text only while the app initializes
            try:
                if getattr(self, "_init_in_progress", False):
                    self._login_overlay.start_loading_animation("Loading AI Document Analyzer")
                else:
                    self._login_overlay.stop_loading_animation()
                # Ensure overlay is interactive
                self._login_overlay.setEnabled(True)
            except Exception:
                pass
        except Exception:
            pass

    def _on_login_success(self) -> None:
        try:
            if getattr(self, "_login_overlay", None):
                self._login_overlay.hide_overlay()
        except Exception:
            pass
        try:
            self._update_user_strip()
        except Exception:
            pass

    def _update_user_strip(self) -> None:
        user = getattr(AuthState, 'user', None) or {}
        email = str(user.get('email', '') or '').strip() if isinstance(user, dict) else ''
        has_user = bool(email)
        try:
            if has_user:
                self._user_label.setText(email)
                self._user_strip.setVisible(True)
                self._logout_button.setVisible(True)
            else:
                self._user_label.setText("")
                self._user_strip.setVisible(False)
        except Exception:
            pass

    def _on_logout_clicked(self) -> None:
        try:
            clear_tokens()
        except Exception:
            pass
        try:
            self._reset_user_session_state()
        except Exception:
            pass
        try:
            self._update_user_strip()
        except Exception:
            pass
        base = getattr(self, "_api_base_url", "") or self._get_api_base_url_fallback()
        try:
            self.show_login_overlay(base)
        except Exception:
            pass

    def _reset_user_session_state(self) -> None:
        try:
            self._last_summary_text = ""
        except Exception:
            pass
        try:
            self._last_summary_json = None
        except Exception:
            pass
        try:
            self._last_input_text_for_qa = ""
            self._qa_document_text = ""
            self._qa_vector_doc_key = ""
            self._current_doc_key = ""
        except Exception:
            pass
        try:
            self._clear_chat()
        except Exception:
            pass
        try:
            if hasattr(self.ui, 'summaryTextEdit'):
                self.ui.summaryTextEdit.clear()
        except Exception:
            pass
        try:
            if hasattr(self.ui, 'questionLineEdit'):
                self.ui.questionLineEdit.clear()
        except Exception:
            pass
        try:
            if hasattr(self.ui, 'pasteTextEdit'):
                self.ui.pasteTextEdit.clear()
        except Exception:
            pass
        try:
            self._set_qa_group_enabled(False)
        except Exception:
            pass
        try:
            self._stop_qa_typing_indicator()
        except Exception:
            pass
        try:
            self._selected_file_path = ""
            if hasattr(self.ui, 'dropArea'):
                self.ui.dropArea.setSelectedFileName("")
        except Exception:
            pass

    def _get_api_base_url_fallback(self) -> str:
        try:
            import json as _json
            import os as _os
            appdata = _os.getenv("APPDATA") or _os.path.expanduser("~")
            cfg_dir = _os.path.join(appdata, "AI Document Analyzer")
            cfg_path = _os.path.join(cfg_dir, "config.json")
            if _os.path.exists(cfg_path):
                with open(cfg_path, "r", encoding="utf-8") as f:
                    cfg = _json.load(f)
                base = cfg.get("API_BASE_URL")
                if base:
                    return str(base).rstrip("/")
        except Exception:
            pass
        try:
            import json as _json
            if os.path.exists("config.json"):
                with open("config.json", "r", encoding="utf-8") as f:
                    cfg = _json.load(f)
                base = cfg.get("API_BASE_URL")
                if base:
                    return str(base).rstrip("/")
        except Exception:
            pass
        return "https://ssma.sa/ai_api"

    # Override init-finished hook to stop the overlay's loading animation
    def _on_init_finished(self):
        try:
            super()._on_init_finished()
        except Exception:
            pass
        try:
            if getattr(self, "_login_overlay", None):
                self._login_overlay.stop_loading_animation()
        except Exception:
            pass

    def _appdata_config_dir(self) -> str:
        try:
            appdata = os.getenv("APPDATA") or os.path.expanduser("~")
            return os.path.join(appdata, "AI Document Analyzer")
        except Exception:
            return os.getcwd()

    def _load_offline_state(self) -> dict:
        path = getattr(self, "offline_state_path", "")
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    return data
            except Exception:
                pass
        return {}

    def _apply_offline_state_to_settings(self) -> None:
        state = getattr(self, "_offline_state", {}) or {}
        try:
            if hasattr(self, "settings_window") and hasattr(self.settings_window, "apply_offline_state"):
                self.settings_window.apply_offline_state(state)
        except Exception:
            pass

    def copy_summary_to_clipboard(self):
        text = self.ui.summaryTextEdit.toPlainText() if hasattr(self.ui, 'summaryTextEdit') else ""
        if not text:
            QMessageBox.information(self, "Copy", "There is no summary to copy.")
            return
        try:
            QApplication.clipboard().setText(text)
            self._set_status("Summary copied to clipboard")
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Failed to copy summary:\n{e}")

    def _set_loading(self, is_loading: bool):
        if is_loading:
            self.ui.analyzeButton.setEnabled(False)
            self._analyze_loader_phase = 0
            self._analyze_loader_timer.start()
        else:
            self._analyze_loader_timer.stop()
            # Reset to localized base label
            self.ui.analyzeButton.setText(self._get_analyze_button_text())
            self.ui.analyzeButton.setEnabled(True)

    def _tick_analyze_loader(self):
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        base = "جاري التحليل" if is_ar else "Analyzing"
        phases = [base, base + ".", base + "..", base + "..."]
        self._analyze_loader_phase = (self._analyze_loader_phase + 1) % len(phases)
        self.ui.analyzeButton.setText(phases[self._analyze_loader_phase])

    def choose_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Documents and Images (*.pdf *.docx *.txt *.png *.jpg *.jpeg)"])
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self._selected_file_path = selected_file
            if hasattr(self.ui, 'dropArea'):
                try:
                    self.ui.dropArea.setSelectedFileName(selected_file)
                except Exception:
                    pass
            # Toggle image-to-PDF button visibility based on file type
            try:
                if hasattr(self.ui, 'saveImageAsPdfButton'):
                    self.ui.saveImageAsPdfButton.setVisible(self.is_image_file(selected_file))
            except Exception:
                pass

    @pyqtSlot(str)
    def _on_file_dropped(self, file_path: str):
        if not file_path:
            return
        self._selected_file_path = file_path
        if hasattr(self.ui, 'dropArea'):
            try:
                self.ui.dropArea.setSelectedFileName(file_path)
            except Exception:
                pass
        # Toggle image-to-PDF button visibility based on file type
        try:
            if hasattr(self.ui, 'saveImageAsPdfButton'):
                self.ui.saveImageAsPdfButton.setVisible(self.is_image_file(file_path))
        except Exception:
            pass

    # Removed clear-file handler (feature reverted)

    def analyze_document(self):
        # Check if initialization completed successfully
        if self.large_doc_manager is None:
            QMessageBox.critical(
                self,
                "Initialization Error",
                "The application failed to initialize properly. Please check the console for errors and restart the application."
            )
            return
        
        source = self.ui.modelSourceCombo.currentText() if hasattr(self.ui, 'modelSourceCombo') else ""
        
        # Determine which tab is active to prioritize the correct input source
        # Tab 0 = Upload Document, Tab 1 = Paste Text
        active_tab_index = 0
        if hasattr(self.ui, 'tabs'):
            active_tab_index = self.ui.tabs.currentIndex()
        
        file_path = ""
        input_text = ""
        is_image = False
        
        if active_tab_index == 1:
            # User is on "Paste Text" tab - analyze pasted text only
            input_text = self._get_input_text()
            if not input_text:
                QMessageBox.information(self, "Input Required", "Please paste text to analyze.")
                return
        else:
            # User is on "Upload Document" tab - analyze uploaded file only
            file_path = self._get_selected_file_path()
            is_image = bool(file_path and self.is_image_file(file_path))
            if not file_path:
                QMessageBox.information(self, "Input Required", "Please choose a supported file (PDF/DOCX/TXT/PNG/JPG).")
                return

        provider = ""
        model = self.ui.availableModelCombo.currentText() if hasattr(self.ui, 'availableModelCombo') else ""
        if source.startswith("Offline"):
            provider = "ollama"
            if not ollama_client:
                QMessageBox.warning(self, "Ollama", "Ollama client not available. Please install ollama and its Python package.")
                return
            if not self.is_ollama_server_running():
                QMessageBox.warning(self, "Ollama", "Ollama server is not running. Please start the Ollama service.")
                return
            if not model or model.startswith("Ollama not") or model.startswith("No models") or model.startswith("Ollama server"):
                QMessageBox.information(self, "Ollama", "No valid local model selected.")
                return
            # Check if selected model is not an embedding model
            if model.startswith("nomic-embed-text"):
                QMessageBox.warning(self, "Invalid Model", "Please select a chat model for summarization, not an embedding model.")
                return
            self._set_status(f"Offline - Running {model}...")
        elif "Gemini" in source:
            provider = "gemini"
            if not model or model.startswith("Missing"):
                QMessageBox.information(self, "Gemini", "Please select a valid Gemini model.")
                return
            key = self._get_gemini_key()
            if not key:
                QMessageBox.warning(self, "Gemini", "Missing GOOGLE_API_KEY. Add it in Settings.")
                return
            if genai is None:
                QMessageBox.warning(self, "Gemini", "Google Generative AI SDK not installed. Please install 'google-generativeai'.")
                return
            self._set_status(f"Online - Gemini {model} ...")
        else:
            QMessageBox.information(self, "Analysis", "Please select a valid source and model.")
            return

        # NOTE: Any heavy operations (like file text extraction) are handled in the worker thread now

        # Prepare params for background execution
        params = {
            "provider": provider,
            "model": model,
            "is_image": is_image,
            "file_path": file_path,
            "input_text": input_text,
            "gemini_key": self._get_gemini_key() if provider == "gemini" else "",
        }

        doc_key = ""
        # Compute doc_key for images/documents or pasted text
        if file_path:
            try:
                doc_key = self.large_doc_manager.compute_document_key(file_path)
            except Exception:
                doc_key = ""
            params["doc_key"] = doc_key
        else:
            if input_text:
                try:
                    doc_key = self._compute_text_doc_key(input_text)
                except Exception:
                    doc_key = ""
            params["doc_key"] = doc_key

        # Handle images, documents, and pasted text with RAG pipeline (always process into vector store)
        if (file_path or input_text) and doc_key:
            has_store = bool(self.large_doc_manager.has_vector_store(doc_key))
            if not has_store:
                self._current_doc_key = doc_key
                self._pending_analysis_params = params
                if file_path:
                    self._set_status("Processing with OCR..." if is_image else "Processing document...")
                    self._set_loading(True)
                    print(f"Starting {'image OCR' if is_image else 'document'} processing worker")
                    self._start_large_doc_processing(file_path, doc_key, is_image=is_image)
                else:
                    self._set_status("Processing pasted text...")
                    self._set_loading(True)
                    print("Starting pasted text processing worker")
                    self._start_pasted_text_processing(doc_key, input_text)
                return
            # Already processed; use existing vector store
            self._qa_vector_doc_key = doc_key
        else:
            self._qa_vector_doc_key = ""

        # Reset and prepare Q&A chat state
        self._last_input_text_for_qa = input_text or ""
        self._qa_document_text = ""  # will be populated after extraction in worker
        self._last_summary_text = ""
        self._clear_chat()
        self._qa_messages = []
        self._set_qa_group_enabled(False)
        self._stop_qa_typing_indicator()

        self._start_background_analysis(params)

    def _prepare_qa_context_options(self):
        # Context dropdown removed; nothing to prepare
        return

    def _escape_html(self, s: str) -> str:
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _append_chat(self, role: str, text: str):
        role_lower = role.lower()
        is_user = role_lower in {"you", "user"}
        is_assistant = role_lower in {"assistant"}
        # Unified alignment: left in English, right in Arabic
        try:
            is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        except Exception:
            is_ar = False
        align = 'right' if is_ar else 'left'
        direction = 'rtl' if is_ar else 'ltr'

        # Colors and label
        if is_user:
            label = "User"
        elif is_assistant:
            label = "Assistant"
        else:  # Error or other
            bg = "#FFF5F5"
            fg = "#b10f2e"
            border = "#b10f2e"
            label = role

        # Default bubble style (same for user and assistant)
        if is_user or is_assistant:
            bg = "#FFFFFF"
            fg = "#000000"
            border = "#E0E0E0"

        # Use same corner style for both
        corner = "border-top-left-radius: 4px; border-top-right-radius: 12px; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;"

        content = self._escape_html(text).replace("\n", "<br>")
        # Inline label with a space after the colon
        content_with_label = f"<span style='font-weight:600'>{self._escape_html(label)}: </span>{content}"

        html = (
            f"<p align='{align}' dir='{direction}' style='margin:6px 0;'>"
            f"  <span style='display:inline-block; max-width:85%; background:{bg}; color:{fg};"
            f"    padding:8px 12px; border:1px solid {border}; {corner}"
            f"    white-space:pre-wrap; word-wrap:break-word;' dir='{direction}'>"
            f"    {content_with_label}"
            f"  </span>"
            f"</p>"
        )
        self.ui.chatHistoryBrowser.append(html)
        self.ui.chatHistoryBrowser.verticalScrollBar().setValue(self.ui.chatHistoryBrowser.verticalScrollBar().maximum())

    def _clear_chat(self):
        try:
            self.ui.chatHistoryBrowser.clear()
        except Exception:
            pass
        # Also clear in-memory history
        self._qa_messages = []

    def _append_history(self, role: str, content: str):
        self._qa_messages.append({"role": role, "content": content})

    def _format_messages_for_prompt(self, messages: list, max_messages: int = 10) -> str:
        # Convert last N messages into a simple transcript
        recent = messages[-max_messages:] if messages else []
        lines = []
        for m in recent:
            role = m.get("role", "user")
            content = m.get("content", "")
            prefix = "User" if role == "user" else "Assistant"
            lines.append(f"{prefix}: {content}")
        return "\n".join(lines)

    def _classify_question_type(self, question: str, provider: str, model: str, gemini_key: str = "") -> str:
        """
        Classify if a question is asking for counting word occurrences.
        Returns "COUNT" for counting questions, "OTHER" for everything else.
        """
        if not question.strip():
            return "OTHER"
        
        # Classification prompt
        classification_prompt = (
            "You are a classifier that determines if a question is asking to count word or phrase occurrences in a document.\n\n"
            "Examples of COUNT questions:\n"
            "- How many times does the word 'energy' appear?\n"
            "- Count the occurrences of 'artificial intelligence'\n"
            "- Number of times 'AI' is mentioned\n"
            "- How often is 'machine learning' used?\n"
            "- Count instances of the phrase 'data science'\n\n"
            "Examples of OTHER questions:\n"
            "- What is the main topic of this document?\n"
            "- Summarize the key points\n"
            "- What does the author think about AI?\n"
            "- Explain the methodology used\n\n"
            f"Question: \"{question}\"\n\n"
            "Answer with only one word: COUNT or OTHER"
        )
        
        try:
            if provider == "ollama":
                if not ollama_client:
                    return "OTHER"
                result = ollama_client.generate(model=model, prompt=classification_prompt, stream=False)
                if isinstance(result, dict):
                    response = result.get('response', '').strip().upper()
                else:
                    response = str(getattr(result, 'response', '')).strip().upper()
            elif provider == "gemini":
                if not genai or not gemini_key:
                    return "OTHER"
                genai.configure(api_key=gemini_key)
                m = genai.GenerativeModel(model_name=model)
                resp = m.generate_content([classification_prompt])
                response = getattr(resp, 'text', '').strip().upper()
            else:
                return "OTHER"
            
            # Extract COUNT or OTHER from response
            if "COUNT" in response:
                return "COUNT"
            else:
                return "OTHER"
                
        except Exception as e:
            print(f"Classification error: {e}")
            return "OTHER"

    def _extract_counting_target(self, question: str) -> str:
        """
        Extract the word or phrase to count from a counting question.
        Uses simple heuristics to find quoted text or common patterns.
        """
        import re
        
        # Look for quoted text first
        quoted_matches = re.findall(r'["\']([^"\']+)["\']', question)
        if quoted_matches:
            return quoted_matches[0]
        
        # Look for common patterns like "word X" or "phrase Y"
        patterns = [
            r'(?:word|term)\s+["\']?([^"\'?\s]+)["\']?',
            r'(?:phrase)\s+["\']?([^"\'?]+)["\']?',
            r'(?:occurrences? of)\s+["\']?([^"\'?]+)["\']?',
            r'(?:times (?:does|is))\s+["\']?([^"\'?]+)["\']?',
            r'(?:mentions? of)\s+["\']?([^"\'?]+)["\']?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            if matches:
                return matches[0].strip()
        
        # Fallback: look for the next meaningful word (skip filler/stop words)
        words = question.split()
        for i, word in enumerate(words):
            if word.lower() in ['how', 'many', 'times', 'count', 'occurrences', 'mentions']:
                # Look for the next meaningful word
                for j in range(i+1, min(i+4, len(words))):
                    candidate = words[j].strip('.,!?"\'()[]{}')
                    stop = {
                        'the','is','are','does','do','did','appear','appears','appeared','mentioned','mention',
                        'many','much','number','of','in','on','at','to','from','a','an','this','that','these','those',
                        'document','file','text','words','word','lines','line','verses','verse','poetry','sentences','sentence',
                    }
                    if len(candidate) > 2 and candidate.lower() not in stop:
                        return candidate
        
        return ""

    def _detect_structural_count(self, question: str) -> str:
        """
        Detect if the question asks to count structural units like lines, verses, paragraphs,
        sentences, words, or characters.
        Returns one of: 'lines', 'verses', 'paragraphs', 'sentences', 'words', 'characters', or ''.
        """
        q = (question or "").lower()
        # Normalize parentheses text
        q = q.replace("(", " ").replace(")", " ")
        # Preferred order (more specific first)
        if "verses" in q or "verse" in q or "lines of poetry" in q:
            return "verses"
        if "lines" in q or "line" in q:
            return "lines"
        if "stanzas" in q or "stanza" in q or "paragraphs" in q or "paragraph" in q:
            return "paragraphs"
        if "sentences" in q or "sentence" in q:
            return "sentences"
        if "words" in q or "word count" in q or "number of words" in q:
            return "words"
        if "characters" in q or "letters" in q:
            return "characters"
        return ""

    def _count_word_occurrences(self, text: str, target: str, case_sensitive: bool = False) -> int:
        """
        Count exact occurrences of a word or phrase in text.
        Supports both word boundaries and phrase matching.
        """
        if not text or not target:
            return 0
        
        import re
        
        # Prepare text and target for comparison
        search_text = text if case_sensitive else text.lower()
        search_target = target if case_sensitive else target.lower()
        
        # If target is a single word, use word boundaries for exact matching
        if ' ' not in search_target.strip():
            # Single word - use word boundaries
            pattern = r'\b' + re.escape(search_target) + r'\b'
            matches = re.findall(pattern, search_text)
            return len(matches)
        else:
            # Phrase - count overlapping occurrences
            count = 0
            start = 0
            while True:
                pos = search_text.find(search_target, start)
                if pos == -1:
                    break
                count += 1
                start = pos + 1
            return count

    def _handle_counting_question(self, question: str, doc_key: str = "") -> str:
        """
        Handle a counting question by extracting the target and counting occurrences.
        """
        # Get full document text first
        full_text = ""
        if doc_key and self.large_doc_manager.has_vector_store(doc_key):
            try:
                full_text = self.large_doc_manager.read_full_text(doc_key)
            except Exception:
                pass
        if not full_text and hasattr(self, '_qa_document_text'):
            full_text = self._qa_document_text or ""
        if not full_text:
            is_ar = getattr(self, '_current_lang', 'en') == 'ar'
            return "لا يوجد نص مستند متاح للعد." if is_ar else "No document text available for counting."

        # Structural counting (lines, verses, paragraphs, sentences, words, characters)
        stype = self._detect_structural_count(question)
        if stype:
            import re
            is_ar = getattr(self, '_current_lang', 'en') == 'ar'
            result = 0
            if stype in {"lines", "verses"}:
                result = len([ln for ln in full_text.splitlines() if ln.strip()])
                if is_ar:
                    return (f"عدد الأبيات (أسطر الشعر) في المستند: {result}" if stype == "verses"
                            else f"عدد الأسطر في المستند: {result}")
                else:
                    return (f"Number of verses (lines of poetry) in the document: {result}" if stype == "verses"
                            else f"Number of lines in the document: {result}")
            if stype == "paragraphs":
                # Split on blank lines (one or more)
                parts = [p for p in re.split(r"(?:\r?\n\s*){2,}", full_text) if p and p.strip()]
                result = len(parts)
                if is_ar:
                    return f"عدد الفقرات في المستند: {result}"
                else:
                    return f"Number of paragraphs in the document: {result}"
            if stype == "sentences":
                parts = [s for s in re.split(r"[.!?]+", full_text) if s and s.strip()]
                result = len(parts)
                if is_ar:
                    return f"عدد الجمل في المستند: {result}"
                else:
                    return f"Number of sentences in the document: {result}"
            if stype == "words":
                words = re.findall(r"\b\w+\b", full_text, flags=re.UNICODE)
                result = len(words)
                if is_ar:
                    return f"عدد الكلمات في المستند: {result}"
                else:
                    return f"Number of words in the document: {result}"
            if stype == "characters":
                result = len(re.sub(r"\s+", "", full_text))
                if is_ar:
                    return f"عدد الأحرف (بدون مسافات) في المستند: {result}"
                else:
                    return f"Number of characters (non-whitespace) in the document: {result}"

        # Otherwise, extract a literal word/phrase to count
        target = self._extract_counting_target(question)
        if not target:
            is_ar = getattr(self, '_current_lang', 'en') == 'ar'
            return "لم أتمكن من تحديد الكلمة أو العبارة المراد عدها من السؤال." if is_ar else "Could not identify the word or phrase to count from your question."

        # Count occurrences of the target term/phrase
        count = self._count_word_occurrences(full_text, target, case_sensitive=False)
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        if is_ar:
            return f"تم العثور على \"{target}\" {count} مرة في المستند."
        else:
            return f"The word/phrase \"{target}\" appears {count} times in the document."

    def _set_qa_controls_enabled(self, enabled: bool):
        self.ui.sendQuestionButton.setEnabled(enabled)
        self.ui.questionLineEdit.setEnabled(enabled)
        try:
            if hasattr(self.ui, 'chatContextCombo'):
                self.ui.chatContextCombo.setEnabled(enabled)
        except Exception:
            pass

    def _set_qa_group_enabled(self, enabled: bool):
        # Enable/disable interactivity
        self.ui.qaGroup.setEnabled(enabled)
        # Apply a faded look when disabled
        try:
            if not hasattr(self, '_qa_opacity_effect') or self._qa_opacity_effect is None:
                self._qa_opacity_effect = QGraphicsOpacityEffect(self.ui.qaGroup)
                self.ui.qaGroup.setGraphicsEffect(self._qa_opacity_effect)
            self._qa_opacity_effect.setOpacity(1.0 if enabled else 0.4)
        except Exception:
            pass

    def _is_large_document(self, file_path: str) -> bool:
        """Check if document is large (more than 2 pages for PDF, or similar logic)."""
        try:
            _, ext = os.path.splitext(file_path)
            ext = (ext or "").lower()
            if ext == ".pdf":
                if PdfReader is None:
                    return False
                with open(file_path, "rb") as f:
                    reader = PdfReader(f)
                    return len(reader.pages) > 2
            elif ext == ".docx":
                if Document is None:
                    return False
                doc = Document(file_path)
                text = "\n".join(p.text for p in doc.paragraphs if p.text)
                # Approximate pages based on character count (rough estimate)
                return len(text) > 5000
            elif ext == ".txt":
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
                return len(text) > 5000
        except Exception:
            pass
        return False

    def _prompt_large_doc_processing(self) -> bool:
        """Prompt user to confirm large document processing."""
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        title = "معالجة مستند كبير" if is_ar else "Large Document Processing"
        message = (
            "هذا المستند كبير جداً. هل تريد تقسيمه إلى مقاطع وتخزينه في قاعدة بيانات المتجهات لتحسين المعالجة؟\n\n"
            "سيتم إنشاء تقرير الملخص من هذه المقاطع."
            if is_ar else
            "This document is large. Would you like to split it into chunks and store in a vector database for better processing?\n\n"
            "The summary report will be created from these chunks."
        )
        reply = QMessageBox.question(
            self, title, message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        return reply == QMessageBox.StandardButton.Yes

    def _compute_text_doc_key(self, text: str) -> str:
        """Compute a stable key for pasted text using MD5 of its content."""
        raw = (text or "").strip()
        try:
            return hashlib.md5(raw.encode("utf-8"), usedforsecurity=False).hexdigest()
        except TypeError:
            # Fallback for Python versions without 'usedforsecurity'
            return hashlib.md5(raw.encode("utf-8")).hexdigest()

    def _start_pasted_text_processing(self, doc_key: str, text: str):
        """Start background processing for pasted text with RAG chunking."""
        self._processing_thread = QThread(self)
        self._processing_worker = PastedTextProcessWorker(self, doc_key, text)
        self._processing_worker.moveToThread(self._processing_thread)
        self._processing_thread.started.connect(self._processing_worker.run)
        self._processing_worker.finished.connect(self._on_large_doc_processing_finished)
        self._processing_worker.error.connect(self._on_large_doc_processing_error)
        self._processing_worker.finished.connect(self._processing_thread.quit)
        self._processing_worker.finished.connect(self._processing_worker.deleteLater)
        self._processing_thread.finished.connect(self._processing_thread.deleteLater)
        self._processing_thread.start()

    def _start_large_doc_processing(self, file_path: str, doc_key: str, is_image: bool = False):
        """Start background processing for large documents or images with OCR."""
        self._processing_thread = QThread(self)
        self._processing_worker = LargeDocProcessWorker(self, file_path, doc_key, is_image=is_image)
        self._processing_worker.moveToThread(self._processing_thread)
        self._processing_thread.started.connect(self._processing_worker.run)
        self._processing_worker.finished.connect(self._on_large_doc_processing_finished)
        self._processing_worker.error.connect(self._on_large_doc_processing_error)
        self._processing_worker.finished.connect(self._processing_thread.quit)
        self._processing_worker.finished.connect(self._processing_worker.deleteLater)
        self._processing_thread.finished.connect(self._processing_thread.deleteLater)
        self._processing_thread.start()

    @pyqtSlot(str, int)
    def _on_large_doc_processing_finished(self, doc_key: str, chunk_count: int):
        """Handle successful large document processing."""
        self._set_loading(False)
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        message = (
            f"تم تقسيم المستند إلى {chunk_count} مقطعاً وتخزينها في قاعدة البيانات.\n\nجاري إنشاء التقرير..."
            if is_ar else
            f"Document split into {chunk_count} chunks and stored in database.\n\nGenerating report..."
        )
        self._set_status(message)
        # Now proceed with analysis using the vector context
        if self._pending_analysis_params:
            self._pending_analysis_params["doc_key"] = doc_key
            self._qa_vector_doc_key = doc_key
            self._start_background_analysis(self._pending_analysis_params)
            self._pending_analysis_params = None

    @pyqtSlot(str)
    def _on_large_doc_processing_error(self, error_message: str):
        """Handle large document processing error."""
        self._set_loading(False)
        self._pending_analysis_params = None
        QMessageBox.critical(self, "Processing Error", f"Failed to process large document:\n{error_message}")
        self._set_status("Ready")

    def _send_question(self):
        question = self.ui.questionLineEdit.text().strip()
        if not question:
            return
        if not self._last_summary_text.strip():
            QMessageBox.information(self, "Q&A", "Please generate a summary first.")
            return

        # Use full original document text (extracted or pasted) by default
        include_input = True
        provider = self.ui.modelSourceCombo.currentText() if hasattr(self.ui, 'modelSourceCombo') else ""
        model = self.ui.availableModelCombo.currentText() if hasattr(self.ui, 'availableModelCombo') else ""
        # Check if selected model is valid for Q&A
        if provider.startswith("Offline") and model.startswith("nomic-embed-text"):
            QMessageBox.warning(self, "Invalid Model", "Please select a chat model for Q&A, not an embedding model.")
            return

        self._append_chat("You", question)
        self._append_history("user", question)
        self.ui.questionLineEdit.clear()
        self._set_qa_controls_enabled(False)
        self._start_qa_typing_indicator()

        # Determine provider and API key (classification will run in the worker thread)
        provider_type = "ollama" if provider.startswith("Offline") else ("gemini" if "Gemini" in provider else "")
        gemini_key = self._get_gemini_key() if "Gemini" in provider else ""

        # Continue with normal RAG processing for non-counting questions
        params = {
            "provider": provider_type,
            "model": model,
            "messages": list(self._qa_messages),
            "summary": self._last_summary_text,
            "input_text": (self._qa_document_text or self._last_input_text_for_qa) if include_input else "",
            "gemini_key": gemini_key,
            "doc_key": self._qa_vector_doc_key,
        }

        thread = QThread(self)
        worker = _QAWorker(self, params)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_qa_finished)
        worker.error.connect(self._on_qa_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._qa_thread = thread
        self._qa_worker = worker
        thread.start()

    def _on_qa_finished(self, answer_text: str):
        self._append_chat("Assistant", answer_text or "(No answer)")
        if answer_text:
            self._append_history("assistant", answer_text)
        self._set_qa_controls_enabled(True)
        self._stop_qa_typing_indicator()

    def _on_qa_error(self, error_message: str):
        if error_message:
            self._append_chat("Error", error_message)
            QMessageBox.critical(self, "Q&A Error", error_message)
        self._set_qa_controls_enabled(True)
        self._stop_qa_typing_indicator()

    def _start_qa_typing_indicator(self):
        try:
            self._qa_typing_phase = 0
            self.ui.typingLabel.setVisible(True)
            self.ui.typingLabel.setText("Assistant is typing")
            self._qa_typing_timer.start()
        except Exception:
            pass

    def _stop_qa_typing_indicator(self):
        try:
            self._qa_typing_timer.stop()
            self.ui.typingLabel.setVisible(False)
        except Exception:
            pass

    def _tick_qa_typing_indicator(self):
        base = self._typing_label_base or "Assistant is typing"
        phases = [base, base + ".", base + "..", base + "..."]
        self._qa_typing_phase = (self._qa_typing_phase + 1) % len(phases)
        self.ui.typingLabel.setText(phases[self._qa_typing_phase])

    def apply_language(self, lang: str):
        is_ar = (lang == "ar")
        try:
            self._current_lang = 'ar' if is_ar else 'en'
            self.setWindowTitle("محلل المستندات الذكي" if is_ar else "AI Document Analyzer")
            self.ui.newChatButton.setText("＋ تحليل جديد" if is_ar else "＋ New Analysis")
            self.ui.availableModelLabel.setText("النموذج:" if is_ar else "Model:")
            self.ui.modelSourceLabel.setText("المصدر:" if is_ar else "Source:")
            self.ui.refreshModelsButton.setText("تحديث" if is_ar else "Refresh")
            self.ui.topSettingsButton.setText("الإعدادات" if is_ar else "Settings")
            self.ui.analyzeButton.setText("تحليل المستند" if is_ar else "Analyze Document")
            # Keep base text in sync with localization
            try:
                self._analyze_button_base = self._get_analyze_button_text()
            except Exception:
                pass
            self.ui.exportButton.setText("تصدير الملخص كملف PDF" if is_ar else "Export Summary as PDF")
            if hasattr(self.ui, 'copySummaryButton'):
                self.ui.copySummaryButton.setText("نسخ الملخص" if is_ar else "Copy Summary")
            self.ui.questionLineEdit.setPlaceholderText("اسأل سؤالاً حول الملخص..." if is_ar else "Ask a question about the summary...")
            # Summary placeholder
            if hasattr(self.ui, 'summaryTextEdit'):
                self.ui.summaryTextEdit.setPlaceholderText("سيظهر التحليل هنا..." if is_ar else "Your analysis will appear here...")
            if hasattr(self.ui, 'pasteTextEdit'):
                self.ui.pasteTextEdit.setPlaceholderText("الصق نصك هنا..." if is_ar else "Paste your text here...")
            # Tabs text: Upload / Paste
            if hasattr(self.ui, 'tabs') and hasattr(self.ui, 'uploadTab') and hasattr(self.ui, 'pasteTab'):
                try:
                    self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.uploadTab), "رفع مستند" if is_ar else "Upload Document")
                    self.ui.tabs.setTabText(self.ui.tabs.indexOf(self.ui.pasteTab), "لصق نص" if is_ar else "Paste Text")
                except Exception:
                    pass
            # Q&A Send / Clear buttons
            if hasattr(self.ui, 'sendQuestionButton'):
                self.ui.sendQuestionButton.setText("إرسال" if is_ar else "Send")
            if hasattr(self.ui, 'clearChatButton'):
                self.ui.clearChatButton.setText("مسح" if is_ar else "Clear")
            self._typing_label_base = "المساعد يكتب" if is_ar else "Assistant is typing"
            self.ui.qaGroup.setTitle("دردشة الأسئلة والأجوبة" if is_ar else "Q&A Chat")
            # Drop area label text
            if hasattr(self.ui, 'dropArea'):
                try:
                    localized_drop = (
                        "انقر لاختيار ملف: PDF, DOCX, TXT, PNG, JPG"
                        if is_ar else
                        "Click to choose a file: PDF, DOCX, TXT, PNG, JPG"
                    )
                    if hasattr(self.ui.dropArea, '_default_label_text'):
                        self.ui.dropArea._default_label_text = localized_drop
                    if not self._get_selected_file_path() and hasattr(self.ui.dropArea, '_label'):
                        self.ui.dropArea._label.setText(localized_drop)
                except Exception:
                    pass
            # Refresh status with localized text
            self._set_status(getattr(self, '_last_status_text', 'Ready'))
        except Exception:
            pass

    def _start_background_analysis(self, params: dict):
        self._set_loading(True)
        thread = QThread(self)
        worker = _AnalysisWorker(self, params)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_analysis_finished)
        worker.error.connect(self._on_analysis_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        # Keep refs to prevent GC
        self._analysis_thread = thread
        self._analysis_worker = worker
        thread.start()

    @pyqtSlot(str, str, str, str)
    def _on_analysis_finished(self, summary_text: str, status_text: str, notify_title: str, notify_message: str):
        # Try to parse JSON and render a clean formatted HTML summary
        parsed = self._try_parse_summary_json(summary_text or "")
        if parsed is not None:
            self._last_summary_json = parsed
            html = self._format_json_summary_as_html(parsed)
            text_for_context = self._format_json_summary_as_text(parsed)
            try:
                self.ui.summaryTextEdit.setHtml(html)
            except Exception:
                self.ui.summaryTextEdit.setPlainText(text_for_context)
            self._last_summary_text = text_for_context
        else:
            self._last_summary_json = None
            self.ui.summaryTextEdit.setPlainText(summary_text or "(No response)")
            self._last_summary_text = summary_text or ""
        # Enable Q&A chat now that we have a summary
        # Context dropdown removed; Q&A enabled based only on presence of summary
        self._set_qa_group_enabled(bool(self._last_summary_text.strip()))
        if notify_title and notify_message:
            self._maybe_notify(notify_title, notify_message)
        if status_text:
            self._set_status(status_text)
        self._set_loading(False)

    @pyqtSlot(str, str)
    def _on_analysis_error(self, status_text: str, error_message: str):
        if error_message:
            QMessageBox.critical(self, "Analysis Error", error_message)
        if status_text:
            self._set_status(status_text)
        self._set_loading(False)

    def open_settings(self):
        # Guard against repeated clicks and keep UI responsive
        if self._settings_open:
            try:
                self.settings_window.raise_()
                self.settings_window.activateWindow()
            except Exception:
                pass
            return
        self._settings_open = True
        try:
            self.settings_window.apply_offline_state(self._offline_state)
        except Exception:
            pass
        self._set_settings_buttons_enabled(False)
        self.settings_window.show()
        self.settings_window.finished.connect(self.on_settings_closed)

    def on_settings_closed(self):
        # Reload models if API keys changed
        self.on_model_source_changed()
        self._settings_open = False
        self._set_settings_buttons_enabled(True)

    def _set_settings_buttons_enabled(self, enabled: bool):
        try:
            if hasattr(self.ui, 'settingsButton'):
                self.ui.settingsButton.setEnabled(enabled)
            if hasattr(self.ui, 'topSettingsButton'):
                self.ui.topSettingsButton.setEnabled(enabled)
        except Exception:
            pass

    @pyqtSlot(float, str)
    def _on_offline_progress(self, percent: float, message: str):
        try:
            self.settings_window.apply_offline_progress(percent, message)
        except Exception:
            pass
        if isinstance(self._offline_state, dict):
            self._offline_state["progress"] = percent

    @pyqtSlot(dict)
    def _on_offline_state_ready(self, state: dict):
        if not isinstance(state, dict):
            state = {}
        self._offline_state = state
        try:
            self.settings_window.apply_offline_state(self._offline_state)
        except Exception:
            pass
        if self._offline_state.get("offline_ready"):
            self._set_status("READY for Offline use")

    def export_pdf(self):
        text = self.ui.summaryTextEdit.toPlainText() if hasattr(self.ui, 'summaryTextEdit') else ""
        if not text.strip():
            QMessageBox.information(self, "Export", "There is no summary to export.")
            return

        save_dialog = QFileDialog(self)
        save_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        save_dialog.setNameFilters(["PDF Files (*.pdf)"])
        save_dialog.selectFile("summary.pdf")
        if not save_dialog.exec():
            return
        save_path = save_dialog.selectedFiles()[0]
        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"
        # Build final HTML in UI thread, then export in background thread
        try:
            widget_html = self.ui.summaryTextEdit.toHtml()
        except Exception:
            widget_html = ""

        if widget_html:
            inner = self._extract_body_inner_html(widget_html) or widget_html
            final_html = self._build_export_html(inner)
        else:
            is_ar = getattr(self, "_current_lang", "en") == "ar"
            if is_ar:
                fallback_font = "Tahoma, Arial, sans-serif"
            else:
                fallback_font = "Poppins, Segoe UI, Arial, sans-serif"
            body = (
                f"<div style='white-space:pre-wrap; font-family:{fallback_font}; font-size:48pt;'>"
                f"{self._escape_html(text)}"  # safe, escaped
                "</div>"
            )
            final_html = self._build_export_html(body)

        # Kick off background export
        try:
            if hasattr(self.ui, 'exportButton'):
                self.ui.exportButton.setEnabled(False)
        except Exception:
            pass
        self._set_status("Exporting PDF...")
        self._start_background_export(final_html, save_path)

    def _save_image_as_pdf(self):
        path = self._get_selected_file_path()
        if not path or not self.is_image_file(path):
            QMessageBox.information(self, "Image", "Please select an image file (PNG/JPG/JPEG) first.")
            return
        # Ask for save path
        save_dialog = QFileDialog(self)
        save_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        save_dialog.setNameFilters(["PDF Files (*.pdf)"])
        save_dialog.selectFile("image.pdf")
        if not save_dialog.exec():
            return
        save_path = save_dialog.selectedFiles()[0]
        if not save_path.lower().endswith(".pdf"):
            save_path += ".pdf"
        try:
            image = QImage(path)
            if image.isNull():
                QMessageBox.critical(self, "Image", "Failed to read the selected image.")
                return
            writer = QPdfWriter(save_path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setResolution(300)
            # Remove margins to use full page for centering
            try:
                layout = writer.pageLayout()
                layout.setMargins(QMarginsF(0, 0, 0, 0))
                writer.setPageLayout(layout)
            except Exception:
                pass
            painter = QPainter(writer)
            # Use the full page rectangle in device pixels
            full_rect = writer.pageLayout().fullRectPixels(writer.resolution())
            page_w = float(full_rect.width())
            page_h = float(full_rect.height())
            img_w = image.width()
            img_h = image.height()
            if img_w == 0 or img_h == 0:
                painter.end()
                QMessageBox.critical(self, "Image", "Invalid image dimensions.")
                return
            scale = min(page_w / float(img_w), page_h / float(img_h))
            target_w = float(img_w) * scale
            target_h = float(img_h) * scale
            x = float(full_rect.x()) + (page_w - target_w) / 2.0
            y = float(full_rect.y()) + (page_h - target_h) / 2.0
            dest_rect = QRectF(x, y, target_w, target_h)
            painter.drawImage(dest_rect, image)
            painter.end()
            QMessageBox.information(self, "Image", f"Saved PDF to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Image to PDF", f"Failed to save PDF:\n{e}")

    def toggle_sidebar(self):
        # Animate sidebar open/close by changing maximumWidth
        self.sidebar_animation.stop()
        if self.sidebar_visible:
            start_value = self.ui.sidebarPanel.maximumWidth()
            end_value = 0
            self.sidebar_animation.setStartValue(start_value)
            self.sidebar_animation.setEndValue(end_value)
            self.sidebar_animation.start()
            self.sidebar_visible = False
        else:
            # Ensure visible before expanding
            self.ui.sidebarPanel.setVisible(True)
            start_value = self.ui.sidebarPanel.maximumWidth()
            end_value = self.sidebar_expanded_width
            self.sidebar_animation.setStartValue(start_value)
            self.sidebar_animation.setEndValue(end_value)
            self.sidebar_animation.start()
            self.sidebar_visible = True

    def _maybe_notify(self, title: str, message: str):
        try:
            if self.settings_window.notifications_enabled() and self.tray_icon:
                self.tray_icon.showMessage(title, message, self.tray_icon.icon())
        except Exception:
            pass

    # --- Model selection & detection ---
    def on_model_source_changed(self):
        # Kick off background refresh instead of blocking UI
        self.refresh_models()

    def refresh_models(self):
        # Avoid overlapping refreshes
        if self._is_refreshing:
            return
        self._is_refreshing = True
        try:
            if hasattr(self.ui, 'refreshModelsButton'):
                self.ui.refreshModelsButton.setEnabled(False)
            self._set_status("Refreshing models...")
            self._begin_models_loading_ui()
        except Exception:
            pass

        source = self.ui.modelSourceCombo.currentText() if hasattr(self.ui, 'modelSourceCombo') else ""
        provider = "gemini" if source.startswith("Online") else ("ollama" if "Offline" in source else "")
        params = {
            "provider": provider,
        }

        thread = QThread(self)
        worker = _RefreshWorker(self, params)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_refresh_finished)
        worker.error.connect(self._on_refresh_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._refresh_thread = thread
        self._refresh_worker = worker
        thread.start()

    @pyqtSlot(str, list, str)
    def _on_refresh_finished(self, provider: str, items: list, message: str):
        try:
            if hasattr(self.ui, 'availableModelCombo'):
                # Always clear the combo first to remove any "Loading models..." message
                self.ui.availableModelCombo.clear()
                if provider == "ollama":
                    if items:
                        self.ui.availableModelCombo.addItems(items)
                    else:
                        self.ui.availableModelCombo.addItem(message or "No models installed")
                elif provider == "gemini":
                    if items:
                        self.ui.availableModelCombo.addItems(items)
                    else:
                        # Show informative message but leave combo enabled
                        self.ui.availableModelCombo.addItem(message or "No Key Found")
                # Always re-enable after loading completes, regardless of whether items were loaded
                try:
                    self.ui.availableModelCombo.setEnabled(True)
                except Exception:
                    pass
        except Exception:
            pass
        finally:
            self._is_refreshing = False
            try:
                if hasattr(self.ui, 'refreshModelsButton'):
                    self.ui.refreshModelsButton.setEnabled(True)
                self._set_status("Ready")
            except Exception:
                pass

    @pyqtSlot(str)
    def _on_refresh_error(self, error_message: str):
        try:
            if hasattr(self.ui, 'availableModelCombo'):
                self.ui.availableModelCombo.clear()
                self.ui.availableModelCombo.addItem("Failed to refresh models")
                try:
                    self.ui.availableModelCombo.setEnabled(True)
                except Exception:
                    pass
            QMessageBox.critical(self, "Models", error_message)
        except Exception:
            pass
        finally:
            self._is_refreshing = False
            try:
                if hasattr(self.ui, 'refreshModelsButton'):
                    self.ui.refreshModelsButton.setEnabled(True)
                self._set_status("Ready")
            except Exception:
                pass

    def _begin_models_loading_ui(self):
        try:
            if hasattr(self.ui, 'availableModelCombo'):
                self.ui.availableModelCombo.clear()
                self.ui.availableModelCombo.addItem("Loading models...")
                self.ui.availableModelCombo.setEnabled(False)
        except Exception:
            pass

    def _start_background_export(self, html: str, save_path: str):
        thread = QThread(self)
        is_ar = getattr(self, "_current_lang", "en") == "ar"
        worker = _ExportWorker(html, save_path, is_ar)
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self._on_export_finished)
        worker.error.connect(self._on_export_error)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(thread.deleteLater)
        self._export_thread = thread
        self._export_worker = worker
        thread.start()

    @pyqtSlot(str)
    def _on_export_finished(self, save_path: str):
        try:
            QMessageBox.information(self, "Export", f"Summary exported to:\n{save_path}")
        except Exception:
            pass
        try:
            if hasattr(self.ui, 'exportButton'):
                self.ui.exportButton.setEnabled(True)
        except Exception:
            pass
        self._set_status("Ready")

    @pyqtSlot(str)
    def _on_export_error(self, error_message: str):
        try:
            QMessageBox.critical(self, "Export Error", f"Failed to export PDF:\n{error_message}")
        except Exception:
            pass
        try:
            if hasattr(self.ui, 'exportButton'):
                self.ui.exportButton.setEnabled(True)
        except Exception:
            pass
        self._set_status("Ready")

    def _set_status(self, text: str):
        self._last_status_text = text or getattr(self, '_last_status_text', 'Ready')
        if hasattr(self.ui, 'statusbar'):
            prefix = "الحالة" if getattr(self, '_current_lang', 'en') == 'ar' else "Status"
            localized = self._translate_status_text(self._last_status_text)
            self.ui.statusbar.showMessage(f"{prefix}: {localized}")

    def _translate_status_text(self, text: str) -> str:
        lang = getattr(self, '_current_lang', 'en')
        if lang != 'ar':
            return text
        if not text:
            return ""
        mapping = {
            "Ready": "جاهز",
            "Refreshing models...": "تحديث النماذج...",
            "Offline": "غير متصل",
            "Online - Gemini": "متصل - Gemini",
            "Offline - Done": "غير متصل - تم",
            "Online - Gemini Done": "متصل - Gemini - تم",
            "Ollama not available": "Ollama غير متاح",
            "Ollama server is not running": "خادم Ollama غير قيد التشغيل",
            "No models installed": "لا توجد نماذج مثبتة",
            "Failed to refresh models": "فشل في تحديث النماذج",
            "Processing with OCR...": "جارٍ المعالجة عبر OCR...",
            "Processing document...": "جارٍ معالجة المستند...",
            "Processing pasted text...": "جارٍ معالجة النص الملصق...",
            "Summary copied to clipboard": "تم نسخ الملخص إلى الحافظة",
            "Exporting PDF...": "جارٍ تصدير PDF...",
        }
        if text in mapping:
            return mapping[text]
        if text.startswith("Offline - Running "):
            return text.replace("Offline - Running ", "غير متصل - تشغيل ")
        if text.startswith("Online - Gemini "):
            return text.replace("Online - Gemini ", "متصل - Gemini ")
        return text

    def _get_analyze_button_text(self) -> str:
        try:
            is_ar = getattr(self, '_current_lang', 'en') == 'ar'
            return "تحليل المستند" if is_ar else "Analyze Document"
        except Exception:
            return "Analyze Document"

    def _apply_analyze_button_theme(self):
        """Apply theme-aware styling to the Analyze Document button based on Windows dark/light mode."""
        try:
            dark_mode = is_windows_dark_mode()
            if dark_mode:
                # Dark mode: white background, black text
                self.ui.analyzeButton.setStyleSheet(
                    "QPushButton {"
                    "  background-color: #FFFFFF; color: #000000;"
                    "  font-weight: bold;"
                    "}"
                    "QPushButton:hover {"
                    "  background-color: #E0E0E0;"
                    "}"
                    "QPushButton:pressed {"
                    "  background-color: #BDBDBD;"
                    "}"
                )
            else:
                # Light mode: black background, white text
                self.ui.analyzeButton.setStyleSheet(
                    "QPushButton {"
                    "  background-color: #000000; color: #FFFFFF;"
                    "  font-weight: bold;"
                    "}"
                    "QPushButton:hover {"
                    "  background-color: #333333;"
                    "}"
                    "QPushButton:pressed {"
                    "  background-color: #555555;"
                    "}"
                )
        except Exception:
            pass

    def _check_theme_change(self):
        """Periodically check if Windows theme has changed and update UI accordingly."""
        try:
            current_dark_mode = is_windows_dark_mode()
            if current_dark_mode != getattr(self, '_last_dark_mode', False):
                self._last_dark_mode = current_dark_mode
                self._apply_analyze_button_theme()
                # Also update DropArea theme (background, border, and label)
                if hasattr(self.ui, 'dropArea') and hasattr(self.ui.dropArea, 'updateTheme'):
                    try:
                        self.ui.dropArea.updateTheme()
                    except Exception:
                        pass
        except Exception:
            pass

    # --- Inputs & Extraction ---
    def _get_input_text(self) -> str:
        """Return pasted text only. Do not extract from file locally."""
        pasted_text = self.ui.pasteTextEdit.toPlainText() if hasattr(self.ui, 'pasteTextEdit') else ""
        return pasted_text.strip() if pasted_text and pasted_text.strip() else ""

    def _get_selected_file_path(self) -> str:
        return self._selected_file_path.strip()

    def is_image_file(self, file_path: str) -> bool:
        _, ext = os.path.splitext(file_path)
        return (ext or "").lower() in {".png", ".jpg", ".jpeg"}

    def _read_image_base64_and_mime(self, file_path: str) -> tuple[str, str]:
        mime, _ = mimetypes.guess_type(file_path)
        if not mime:
            # Default to png if unknown
            mime = "image/png"
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode("utf-8")
        return b64, mime

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF, DOCX, TXT, or image files. Raises on unsupported types."""
        _, ext = os.path.splitext(file_path)
        ext = (ext or "").lower()
        
        # Handle images with OCR
        if ext in {".png", ".jpg", ".jpeg"}:
            return self.extract_text_from_image_ocr(file_path)
        
        if ext == ".pdf":
            if PdfReader is None:
                raise RuntimeError("PyPDF2 not installed. Please install 'PyPDF2'.")
            text_parts = []
            with open(file_path, "rb") as f:
                reader = PdfReader(f)
                for page in getattr(reader, "pages", []):
                    try:
                        text_parts.append(page.extract_text() or "")
                    except Exception:
                        continue
            return "\n".join(part for part in text_parts if part)
        if ext == ".docx":
            if Document is None:
                raise RuntimeError("python-docx not installed. Please install 'python-docx'.")
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text)
        if ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        if ext == ".doc":
            raise RuntimeError(".doc files are not supported. Please convert to .docx or PDF.")
        raise RuntimeError(f"Unsupported file type: {ext}")
    
    def extract_text_from_image_ocr(self, file_path: str) -> str:
        """Extract text from image using EasyOCR."""
        # Ensure dependencies are available at call time
        try:
            import easyocr  # type: ignore
        except Exception as import_err:
            raise RuntimeError(f"EasyOCR not installed or failed to load: {import_err}")
        try:
            from PIL import Image  # type: ignore
        except Exception:
            raise RuntimeError("Pillow not installed. Please install 'Pillow'.")

        # Lazy-load OCR reader (expensive initialization)
        if self._ocr_reader is None:
            try:
                # Initialize with English and Arabic support, GPU disabled for frozen apps
                gpu = False
                if not getattr(sys, 'frozen', False):
                    # Only try GPU in non-frozen environment
                    try:
                        import torch  # type: ignore
                        try:
                            gpu = bool(torch.cuda.is_available())
                        except Exception:
                            gpu = False
                    except Exception:
                        gpu = False
                # Force EasyOCR to use app-local models cache prepared by offline_bootstrap
                try:
                    models_dir = getattr(self.large_doc_manager, 'models_dir', None)
                    if not models_dir:
                        models_dir = os.path.join(self._appdata_config_dir(), 'models')
                except Exception:
                    models_dir = os.path.join(os.getcwd(), 'models')
                easyocr_dir = os.path.join(models_dir, 'easyocr')
                try:
                    os.makedirs(easyocr_dir, exist_ok=True)
                except Exception:
                    pass
                # Allow download if models not present (first run scenario)
                # Check if models already exist
                models_exist = any(
                    f.endswith('.pth') or f.endswith('.bin')
                    for f in os.listdir(easyocr_dir)
                ) if os.path.isdir(easyocr_dir) else False
                self._ocr_reader = easyocr.Reader(
                    ['en', 'ar'],
                    gpu=gpu,
                    model_storage_directory=easyocr_dir,
                    download_enabled=not models_exist,  # Download only if models missing
                )
            except Exception as e:
                raise RuntimeError(f"Failed to initialize EasyOCR reader: {e}")
        
        try:
            # Read image
            img = Image.open(file_path)
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Perform OCR
            results = self._ocr_reader.readtext(file_path)
            
            # Extract text from results
            # EasyOCR returns list of (bbox, text, confidence)
            extracted_lines = []
            for detection in results:
                if len(detection) >= 2:
                    text = detection[1]
                    if text and text.strip():
                        extracted_lines.append(text.strip())
            
            full_text = "\n".join(extracted_lines)
            if not full_text.strip():
                raise RuntimeError("No text detected in the image. The image may be blank or contain no readable text.")
            
            return full_text
        except Exception as e:
            if "No text detected" in str(e):
                raise
            raise RuntimeError(f"OCR extraction failed: {e}")

    # --- Summarization Helpers ---
    def summarize_text_offline(self, model: str, input_text: str) -> str:
        schema = (
            '{\n'
            '  "summary": {\n'
            '    "key_points": ["...", "..."],\n'
            '    "methods": ["...", "..."],\n'
            '    "conclusions": ["...", "..."]\n'
            '  }\n'
            '}'
        )
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        if is_ar:
            prompt = (
                "أنت مُلخِّص أكاديمي خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "
                "لخّص نص المستند المقدم فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية.\n\n"
                f"نص المستند:\n{input_text}\n\n"
                "أعد الملخص بهذا الهيكل JSON:\n"
                f"{schema}\n\n"
                "أرجع JSON صالح فقط دون أي أسطر برمجية أو نص خارج JSON. اكتب المحتوى باللغة العربية."
            )
        else:
            prompt = (
                "You are an expert summarizer. You must return the summary in strict JSON format. "
                "Summarize only the provided document text. Focus on key points, methods, and conclusions. No extra commentary. "
                "You must always provide content for all three fields (key_points, methods, conclusions), even if the document does not explicitly contain them. "
                "If necessary, infer plausible entries to ensure each field is filled.\n\n"
                f"Document text:\n{input_text}\n\n"
                "Return the summary in this JSON structure:\n"
                f"{schema}\n\n"
                "Return only valid JSON without code fences. Write the content in English."
            )
        result = ollama_client.generate(model=model, prompt=prompt, format='json', stream=False)
        if isinstance(result, dict):
            return result.get('response', '') or ''
        # Support typed responses from newer clients
        try:
            resp = getattr(result, 'response', '')
            if resp:
                return resp
        except Exception:
            pass
        return str(result)

    def summarize_text_gemini(self, model: str, input_text: str, api_key: str) -> Optional[str]:
        genai.configure(api_key=api_key)  # type: ignore
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        if is_ar:
            sys_instr = (
                "أنت مُلخِّص أكاديمي خبير. يجب أن تُرجع الملخص بصيغة JSON صارمة فقط. "
                "لخّص نص المستند المقدم فقط. ركّز على النقاط الرئيسية والأساليب والاستنتاجات. بدون أي تعليقات إضافية."
            )
            user_prompt = (
                "نص المستند:\n" + input_text + "\n\n" +
                "أعد الملخص بهذا الهيكل JSON:\n" +
                '{\n  "summary": {\n    "key_points": ["...", "..."],\n    "methods": ["...", "..."],\n    "conclusions": ["...", "..."]\n  }\n}\n\n' +
                "أرجع JSON صالح فقط دون أي أسطر برمجية أو نص خارج JSON. اكتب المحتوى باللغة العربية."
            )
        else:
            sys_instr = (
                "You are an expert summarizer. You must return the summary in strict JSON format. "
                "Summarize only the provided document text. Focus on key points, methods, and conclusions. No extra commentary. "
                "You must always provide content for all three fields (key_points, methods, conclusions), even if the document does not explicitly contain them. "
                "If necessary, infer plausible entries to ensure each field is filled."
            )
            user_prompt = (
                "Document text:\n" + input_text + "\n\n" +
                "Return the summary in this JSON structure:\n" +
                '{\n  "summary": {\n    "key_points": ["...", "..."],\n    "methods": ["...", "..."],\n    "conclusions": ["...", "..."]\n  }\n}\n\n' +
                "Return only valid JSON without code fences. Write the content in English."
            )
        m = genai.GenerativeModel(model_name=model, system_instruction=sys_instr)  # type: ignore
        resp = m.generate_content([user_prompt])
        return getattr(resp, 'text', None)

    # --- JSON parsing and formatting helpers ---
    def _try_parse_summary_json(self, text: str):
        if not text:
            return None
        # Direct parse
        try:
            return json.loads(text)
        except Exception:
            pass
        # Normalize common formatting artifacts and try again
        try:
            normalized = self._normalize_json_like(text)
            if normalized and normalized != text:
                try:
                    return json.loads(normalized)
                except Exception:
                    pass
        except Exception:
            pass
        # Strip code fences if present
        fenced = text.strip()
        if fenced.startswith("```)**"):
            # unlikely, safety
            fenced = fenced.strip('`')
        if fenced.startswith("```") and fenced.endswith("```"):
            inner = fenced.strip('`')
            # Remove optional language tag
            first_newline = inner.find("\n")
            if first_newline != -1:
                inner = inner[first_newline+1:]
            try:
                return json.loads(inner)
            except Exception:
                pass
        # Extract first JSON object substring (robust brace matching)
        try:
            candidate = self._extract_first_json_object(text)
            if candidate:
                try:
                    return json.loads(candidate)
                except Exception:
                    # Try normalized candidate
                    normalized_candidate = self._normalize_json_like(candidate)
                    if normalized_candidate:
                        return json.loads(normalized_candidate)
        except Exception:
            pass
        return None

    def _normalize_json_like(self, text: str) -> str:
        try:
            s = text or ""
            # Remove BOM and zero-width characters
            s = s.replace("\ufeff", "").replace("\u200b", "")
            # Replace smart quotes with straight quotes
            s = s.replace("\u201c", '"').replace("\u201d", '"')
            s = s.replace("\u2018", "'").replace("\u2019", "'")
            # Remove fenced code blocks generically
            stripped = s.strip()
            if stripped.startswith("```)**"):
                stripped = stripped.strip('`')
            if stripped.startswith("```") and stripped.endswith("```"):
                inner = stripped.strip('`')
                nl = inner.find("\n")
                if nl != -1:
                    inner = inner[nl+1:]
                s = inner
            # Remove trailing commas before object/array close
            try:
                s = re.sub(r",\s*([}\]])", r"\\1", s)
            except Exception:
                pass
            return s
        except Exception:
            return text

    def _extract_first_json_object(self, text: str) -> str:
        try:
            start = text.find('{')
            if start == -1:
                return ""
            i = start
            depth = 0
            in_string = False
            escape = False
            while i < len(text):
                ch = text[i]
                if in_string:
                    if escape:
                        escape = False
                    elif ch == '\\':
                        escape = True
                    elif ch == '"':
                        in_string = False
                else:
                    if ch == '"':
                        in_string = True
                    elif ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            return text[start:i+1]
                i += 1
            return ""
        except Exception:
            return ""

    def _format_json_summary_as_html(self, data: dict) -> str:
        summary = data.get("summary", {}) if isinstance(data, dict) else {}
        key_points = summary.get("key_points", []) if isinstance(summary, dict) else []
        methods = summary.get("methods", []) if isinstance(summary, dict) else []
        conclusions = summary.get("conclusions", []) if isinstance(summary, dict) else []
        is_ar = getattr(self, "_current_lang", "en") == "ar"

        # Localized section labels
        label_key_points = "النقاط الرئيسية" if is_ar else "Key Points"
        label_methods = "الأساليب" if is_ar else "Methods"
        label_conclusions = "الاستنتاجات" if is_ar else "Conclusions"

        def render_list(items):
            if not isinstance(items, list) or not items:
                return "<ul style='list-style-type:disc; padding-left:20px;'><li>—</li></ul>"
            lis = "".join(f"<li>{self._escape_html(str(x))}</li>" for x in items)
            return f"<ul style='list-style-type:disc; padding-left:20px; margin:6px 0;'>" + lis + "</ul>"

        title_base = self._get_document_display_name()
        title_text = self._get_localized_summary_title(title_base)
        # Align title based on language: right for Arabic, left for English
        title_align = "right" if is_ar else "left"
        # Use Windows-common fonts: Tahoma for Arabic, Poppins for English
        title_font_family = "Tahoma" if is_ar else "Poppins, Arial, sans-serif"
        title_html = (
            f"<h1 style='font-family:{title_font_family}; font-size:22pt; font-weight:bold; margin:0 0 12px 0; text-align:{title_align};'>"
            f"{self._escape_html(title_text)}"
            f"</h1>"
        )

        if is_ar:
            container_style = "font-family:Tahoma, Arial, sans-serif; font-size:12pt; color:#111; direction:rtl; text-align:right"
        else:
            container_style = "font-family:Poppins, Segoe UI, Arial, sans-serif; font-size:12pt; color:#111"

        html = (
            f"<div style='{container_style}'>"
            f"{title_html}"
            f"<h3 style='margin:12px 0 6px 0;'>{self._escape_html(label_key_points)}</h3>"
            f"{render_list(key_points)}"
            f"<h3 style='margin:12px 0 6px 0;'>{self._escape_html(label_methods)}</h3>"
            f"{render_list(methods)}"
            f"<h3 style='margin:12px 0 6px 0;'>{self._escape_html(label_conclusions)}</h3>"
            f"{render_list(conclusions)}"
            "</div>"
        )
        return html

    def _format_json_summary_as_text(self, data: dict) -> str:
        summary = data.get("summary", {}) if isinstance(data, dict) else {}
        key_points = summary.get("key_points", []) if isinstance(summary, dict) else []
        methods = summary.get("methods", []) if isinstance(summary, dict) else []
        conclusions = summary.get("conclusions", []) if isinstance(summary, dict) else []
        is_ar = getattr(self, "_current_lang", "en") == "ar"

        label_key_points = "النقاط الرئيسية" if is_ar else "Key Points"
        label_methods = "الأساليب" if is_ar else "Methods"
        label_conclusions = "الاستنتاجات" if is_ar else "Conclusions"

        title_base = self._get_document_display_name()
        title_text = self._get_localized_summary_title(title_base)
        lines = [
            f"{title_text}",
            "",
            f"{label_key_points}:",
        ]
        lines.extend([f"• {str(x)}" for x in key_points])
        lines.extend(["", f"{label_methods}:"])
        lines.extend([f"• {str(x)}" for x in methods])
        lines.extend(["", f"{label_conclusions}:"])
        lines.extend([f"• {str(x)}" for x in conclusions])
        return "\n".join(lines)

    def _get_document_display_name(self) -> str:
        try:
            path = getattr(self, "_selected_file_path", "") or ""
            if path:
                base = os.path.basename(path)
                name, _ = os.path.splitext(base)
                if name:
                    return name
                # fall through to localized default
            # Localize fallback names
            is_ar = getattr(self, "_current_lang", "en") == "ar"
            return "نص ملصق" if is_ar else "Pasted Text"
        except Exception:
            return "مستند" if getattr(self, "_current_lang", "en") == "ar" else "Document"

    def _get_localized_summary_title(self, base_name: str) -> str:
        try:
            is_ar = getattr(self, "_current_lang", "en") == "ar"
            if is_ar:
                # Arabic: "تقرير ملخص المستند"
                return f"تقرير ملخص المستند"
            return f"Document Summary Report"
        except Exception:
            return f"Document Summary Report"

    def _extract_body_inner_html(self, html: str) -> str:
        try:
            lower = html.lower()
            start = lower.find("<body")
            if start == -1:
                return html
            start = lower.find('>', start)
            if start == -1:
                return html
            end = lower.rfind("</body>")
            if end == -1:
                end = len(html)
            return html[start+1:end]
        except Exception:
            return html

    def _build_export_html(self, body_inner_html: str) -> str:
        try:
            is_ar = getattr(self, "_current_lang", "en") == "ar"
            dir_attr = " dir='rtl'" if is_ar else ""
            if is_ar:
                style_base = "font-family:Tahoma, Arial, sans-serif; font-size:11pt; color:#111; min-height:100%;"
            else:
                style_base = "font-family:Poppins, Segoe UI, Arial, sans-serif; font-size:11pt; color:#111; min-height:100%;"
            # Align H1 per language and enforce larger size/weight
            h1_align = "right" if is_ar else "left"
            page_style = (
                f"@page {{ margin: 24mm 18mm 24mm 18mm; }} "
                f"body {{ margin:0; padding:0; }} "
                f"h1 {{ text-align:{h1_align}; font-size:22pt; font-weight:700; margin:0 0 12px 0; }}"
            )
            html = (
                f"<html><head><meta charset='utf-8'><style>{page_style}</style></head>"
                f"<body{dir_attr}><div style='{style_base}'>"
                f"{body_inner_html}"
                f"</div></body></html>"
            )
            return html
        except Exception:
            return body_inner_html
    # --- Q&A Helpers ---
    def answer_question_offline(self, model: str, messages, summary: str, input_text: str, doc_key: str = "") -> str:
        # Build system + user prompts with robust instructions for safety flags, counts, and dialogue
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        if is_ar:
            system_prompt = (
                "أنت مساعد ذكاء اصطناعي يحلل مستنداً واحداً مُقدماً (نص عادي أو ملف PDF وغيرها) ويجيب فقط عن الأسئلة المتعلقة بمحتواه. "
                "تعامَل مع جميع أنواع الأسئلة مثل: هل يتضمن المستند أي عنف؟ كم مرة تكررت الكلمة \"___\"؟ عمّ يتحدث الحوار بين \"الشخصية\" و\"الشخصية\"؟ هل يتضمن المستند أفكاراً أو ألفاظاً مسيئة للقانون أو للوطن؟ وهل يحتوي على كلمات تستهدف قبيلة؟ "
                "تذكّر المحادثة السابقة مع المستخدم واستخدمها للسياق."
            )
        else:
            system_prompt = (
                "You are an AI assistant that analyzes a single provided document (plain text, PDF, etc.) and answers only questions about its content. "
                "Handle all types of questions such as: \"Does the document include any form of violence?\", \"How many times was the word repeated?\", \"What is the conversation about between character A and character B?\", \"Does the document include offensive ideas or words against the law or the country?\", and \"Does it contain words targeting a tribe?\" "
                "Remember the previous conversation with the user and use it for context."
            )
        # Strictly use original document text only (no summary fallback)
        document_text = (input_text or "").strip()
        user_question = ""
        for m in reversed(messages or []):
            if m.get("role") == "user":
                user_question = (m.get("content", "") or "").strip()
                break
        vector_context = ""
        if doc_key:
            try:
                docs = self.large_doc_manager.retrieve_context(doc_key, user_question or "")
            except Exception:
                docs = []
            if docs:
                collected: List[str] = []
                for doc in docs:
                    chunk = getattr(doc, 'page_content', '') or ''
                    if chunk.strip():
                        collected.append(chunk.strip())
                vector_context = "\n\n".join(collected)
        context_text = vector_context or document_text
        if not context_text:
            return "لا يوجد نص مستند متاح للأسئلة والأجوبة." if is_ar else "No document context available for Q&A."
        # Build conversation history
        conversation_history = ""
        if messages and len(messages) > 1:
            history_lines = []
            # Include all messages except the last user question (we'll add it separately)
            for m in messages[:-1]:
                role = m.get("role", "user")
                content = m.get("content", "")
                if role == "user":
                    prefix = "المستخدم" if is_ar else "User"
                else:
                    prefix = "المساعد" if is_ar else "Assistant"
                history_lines.append(f"{prefix}: {content}")
            if history_lines:
                conversation_history = "\n".join(history_lines)
        
        # Build the final prompt with conversation history
        if is_ar:
            user_prompt = "مقاطع سياقية:\n" + context_text + "\n\n"
            if conversation_history:
                user_prompt += "محادثة سابقة:\n" + conversation_history + "\n\n"
            user_prompt += (
                "سؤال المستخدم الحالي:\n" + user_question + "\n\n" +
                "أجب بالعربية اعتماداً فقط على نص المستند والمحادثة السابقة. لا تُضِف معلومات خارجية."
            )
        else:
            user_prompt = "Context passages:\n" + context_text + "\n\n"
            if conversation_history:
                user_prompt += "Previous conversation:\n" + conversation_history + "\n\n"
            user_prompt += (
                "Current User Question:\n" + user_question + "\n\n" +
                "Answer strictly based on the document text and previous conversation only."
            )
        prompt = system_prompt + "\n\n" + user_prompt
        result = ollama_client.generate(model=model, prompt=prompt, stream=False)
        if isinstance(result, dict):
            return result.get('response', '') or ''
        try:
            resp = getattr(result, 'response', '')
            if resp:
                return resp
        except Exception:
            pass
        return str(result)

    def answer_question_gemini(self, model: str, messages, summary: str, input_text: str, api_key: str, doc_key: str = "") -> Optional[str]:
        genai.configure(api_key=api_key)  # type: ignore
        is_ar = getattr(self, '_current_lang', 'en') == 'ar'
        if is_ar:
            system_prompt = (
                "أنت مساعد ذكاء اصطناعي يحلل مستنداً واحداً مُقدماً (نص عادي أو ملف PDF وغيرها) ويجيب فقط عن الأسئلة المتعلقة بمحتواه. "
                "تعامَل مع جميع أنواع الأسئلة مثل: هل يتضمن المستند أي عنف؟ كم مرة تكررت الكلمة \"___\"؟ عمّ يتحدث الحوار بين \"الشخصية\" و\"الشخصية\"؟ هل يتضمن المستند أفكاراً أو ألفاظاً مسيئة للقانون أو للوطن؟ وهل يحتوي على كلمات تستهدف قبيلة؟ "
                "تذكّر المحادثة السابقة مع المستخدم واستخدمها للسياق."
            )
        else:
            system_prompt = (
                "You are an AI assistant that analyzes a single provided document (plain text, PDF, etc.) and answers only questions about its content. "
                "Handle all types of questions such as: \"Does the document include any form of violence?\", \"How many times was the word repeated?\", \"What is the conversation about between character A and character B?\", \"Does the document include offensive ideas or words against the law or the country?\", and \"Does it contain words targeting a tribe?\" "
                "Remember the previous conversation with the user and use it for context."
            )
        m = genai.GenerativeModel(model_name=model, system_instruction=system_prompt)  # type: ignore
        # Strictly use original document text only (no summary fallback)
        document_text = (input_text or "").strip()
        user_question = ""
        for mobj in reversed(messages or []):
            if mobj.get("role") == "user":
                user_question = (mobj.get("content", "") or "").strip()
                break
        vector_context = ""
        if doc_key:
            try:
                docs = self.large_doc_manager.retrieve_context(doc_key, user_question or "")
            except Exception:
                docs = []
            if docs:
                collected: List[str] = []
                for doc in docs:
                    piece = getattr(doc, 'page_content', '') or ''
                    if piece.strip():
                        collected.append(piece.strip())
                vector_context = "\n\n".join(collected)
        context_text = vector_context or document_text
        if not context_text:
            return "لا يوجد نص مستند متاح للأسئلة والأجوبة." if is_ar else "No document context available for Q&A."
        # Build conversation history
        conversation_history = ""
        if messages and len(messages) > 1:
            history_lines = []
            # Include all messages except the last user question
            for msg in messages[:-1]:
                role = msg.get("role", "user")
                content_msg = msg.get("content", "")
                if role == "user":
                    prefix = "المستخدم" if is_ar else "User"
                else:
                    prefix = "المساعد" if is_ar else "Assistant"
                history_lines.append(f"{prefix}: {content_msg}")
            if history_lines:
                conversation_history = "\n".join(history_lines)
        
        if is_ar:
            user_prompt = "مقاطع سياقية:\n" + context_text + "\n\n"
            if conversation_history:
                user_prompt += "محادثة سابقة:\n" + conversation_history + "\n\n"
            user_prompt += (
                "سؤال المستخدم الحالي:\n" + user_question + "\n\n" +
                "أجب بالعربية اعتماداً فقط على نص المستند والمحادثة السابقة. لا تُضِف معلومات خارجية."
            )
        else:
            user_prompt = "Context passages:\n" + context_text + "\n\n"
            if conversation_history:
                user_prompt += "Previous conversation:\n" + conversation_history + "\n\n"
            user_prompt += (
                "Current User Question:\n" + user_question + "\n\n" +
                "Answer strictly based on the document text and previous conversation only."
            )
        resp = m.generate_content([user_prompt])
        return getattr(resp, 'text', None)

    def _read_config(self):
        try:
            # On first run, if appdata config missing but local config exists next to exe/cwd, copy it
            try:
                if not os.path.exists(self.config_path):
                    # Prefer PyInstaller resource dir in onefile mode
                    resource_dir = None
                    try:
                        if getattr(sys, 'frozen', False):
                            resource_dir = getattr(sys, '_MEIPASS', None) or os.path.dirname(sys.executable)
                    except Exception:
                        resource_dir = None
                    if not resource_dir:
                        resource_dir = os.getcwd()
                    local_cfg = os.path.join(resource_dir, "config.json")
                    if os.path.exists(local_cfg):
                        shutil.copy2(local_cfg, self.config_path)
            except Exception:
                pass
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def _get_selected_model(self) -> str:
        """Get the currently selected model from UI."""
        try:
            if hasattr(self.ui, 'availableModelCombo'):
                selected = self.ui.availableModelCombo.currentText().strip()
                if selected and not selected.startswith("Ollama") and not selected.startswith("No models") and not selected.startswith("Failed"):
                    return selected
        except Exception:
            pass
        # Default fallback - try some common models
        fallback_models = ["llama3.2", "llama3.1", "mistral", "codellama"]
        for model in fallback_models:
            try:
                # Quick check if model might be available (this is a rough check)
                if self.is_ollama_available() and self.is_ollama_server_running():
                    available = self.list_ollama_models()
                    if model in available:
                        return model
            except Exception:
                pass
        return "llama3.2"  # Final fallback

    def _get_gemini_key(self) -> str:
        """Get the Gemini API key from config or QSettings."""
        try:
            data = self._read_config()
            key = data.get("GOOGLE_API_KEY")
            if key:
                return key
        except Exception:
            pass
        # Fallback to QSettings
        return self.settings_window.settings.value("GOOGLE_API_KEY", "", type=str)

    def _get_online_summary_char_cap(self) -> int:
        """Max characters for online summarization to respect free-tier limits.

        Config key: ONLINE_SUMMARY_CHAR_CAP (int). Default: 12000
        """
        try:
            data = self._read_config()
            val = int(data.get("ONLINE_SUMMARY_CHAR_CAP", 12000))
            return max(1000, val)
        except Exception:
            return 12000

    def _get_offline_summary_char_cap(self) -> int:
        """Optional cap for offline summarization. 0 or negative means unlimited.

        Config key: OFFLINE_SUMMARY_CHAR_CAP (int). Default: 0 (unlimited)
        """
        try:
            data = self._read_config()
            val = int(data.get("OFFLINE_SUMMARY_CHAR_CAP", 0))
            return max(0, val)
        except Exception:
            return 0

    def is_ollama_available(self) -> bool:
        return ollama_client is not None

    def is_ollama_server_running(self) -> bool:
        if not ollama_client:
            return False
        try:
            # If the server is down, this will raise a connection error
            _ = ollama_client.list()
            return True
        except Exception:
            return False

    def list_ollama_models(self) -> list:
        if not ollama_client:
            return []
        try:
            data = ollama_client.list()
            # Support both dict responses and typed objects (ListResponse)
            if isinstance(data, dict):
                models = data.get('models', [])
            else:
                models = getattr(data, 'models', [])

            names = []
            for m in models:
                if isinstance(m, dict):
                    name = m.get('name') or m.get('model')
                else:
                    name = getattr(m, 'name', None) or getattr(m, 'model', None)
                if name:
                    names.append(name)
            return names
        except Exception:
            return []

    def populate_ollama_models(self):
        if not hasattr(self.ui, 'availableModelCombo'):
            return
        self.ui.availableModelCombo.clear()
        # Ensure the model combo is enabled for Offline source
        try:
            self.ui.availableModelCombo.setEnabled(True)
        except Exception:
            pass
        if not self.is_ollama_available():
            self.ui.availableModelCombo.addItem("Ollama not available")
            return
        if not self.is_ollama_server_running():
            self.ui.availableModelCombo.addItem("Ollama server is not running")
            return
        names = self.list_ollama_models()
        # Exclude embedding models from LLM selection
        names = [name for name in names if not name.startswith("nomic-embed-text")]
        if names:
            self.ui.availableModelCombo.addItems(names)
        else:
            self.ui.availableModelCombo.addItem("No chat models available")

    def populate_online_models(self, provider: str):
        if not hasattr(self.ui, 'availableModelCombo'):
            return
        self.ui.availableModelCombo.clear()
        if provider == "gemini":
            key = self._get_gemini_key()
            if not key:
                # Show informative message inside the dropdown and disable it
                self.ui.availableModelCombo.addItem("No Key Found")
                return
            try:
                self.ui.availableModelCombo.setEnabled(True)
            except Exception:
                pass
            self.ui.availableModelCombo.addItems(self.online_models_gemini)

    def _on_lock_status_changed(self, is_locked: bool):
        """Handle lock status changes from the lock manager."""
        if is_locked:
            self.lock_overlay.set_custom_message(self.lock_manager.get_lock_message())
            self.lock_overlay.show_overlay()
        else:
            self.lock_overlay.hide_overlay()
    
    def _on_lock_message_changed(self, message: str):
        """Handle lock message changes from the lock manager."""
        self.lock_overlay.set_custom_message(message)
    
    def resizeEvent(self, event):
        """Ensure lock overlay stays covering the entire window."""
        super().resizeEvent(event)
        if hasattr(self, 'lock_overlay') and self.lock_overlay.isVisible():
            self.lock_overlay.setGeometry(self.rect())

class _AnalysisWorker(QObject):
    finished = pyqtSignal(str, str, str, str)  # summary, status, notify_title, notify_message
    error = pyqtSignal(str, str)  # status, error_message

    def __init__(self, window: 'MainWindow', params: dict):
        super().__init__()
        self.window = window
        self.params = params

    @pyqtSlot()
    def run(self):
        try:
            provider = self.params.get("provider")
            model = self.params.get("model")
            is_image = self.params.get("is_image")
            file_path = self.params.get("file_path")
            input_text = self.params.get("input_text")
            gemini_key = self.params.get("gemini_key")
            doc_key = self.params.get("doc_key", "")

            # Move potentially heavy file text extraction to the worker thread
            try:
                if doc_key and self.window.large_doc_manager.has_vector_store(doc_key):
                    # Prefer full raw text for offline; cap for online
                    if provider == "ollama":
                        full_text = self.window.large_doc_manager.read_full_text(doc_key)
                        if full_text and full_text.strip():
                            cap = self.window._get_offline_summary_char_cap()
                            input_text = full_text if cap <= 0 else full_text[:cap]
                        else:
                            # Fallback to concatenated chunks with no cap
                            input_text = self.window.large_doc_manager.build_summary_context(doc_key, max_chars=10**9)
                    else:
                        # Online models: keep within cap
                        cap = self.window._get_online_summary_char_cap()
                        input_text = self.window.large_doc_manager.build_summary_context(doc_key, max_chars=cap)
                elif file_path and not (input_text or "").strip():
                    # Extract text from file (includes OCR for images)
                    if not os.path.exists(file_path):
                        self.error.emit("", f"File does not exist:\n{file_path}")
                        return
                    extracted = self.window.extract_text_from_file(file_path)
                    if not extracted:
                        self.error.emit("", "Could not extract text from the selected file.")
                        return
                    input_text = extracted
            except Exception as e:
                self.error.emit("", f"Failed to extract text from file:\n{e}")
                return

            # Persist the effective document text for Q&A usage
            try:
                effective_text = (input_text or "").strip()
                self.window._qa_document_text = effective_text
                if doc_key and self.window.large_doc_manager.has_vector_store(doc_key):
                    self.window._qa_vector_doc_key = doc_key
            except Exception:
                pass

            # For both ollama and gemini, use OCR text instead of vision models
            if provider == "ollama":
                summary = self.window.summarize_text_offline(model, input_text)
                self.finished.emit(summary or "(No response)", "Offline - Done", "Analysis Complete", "Your offline analysis has finished.")
                return
            if provider == "gemini":
                summary = self.window.summarize_text_gemini(model, input_text, gemini_key)
                self.finished.emit(summary or "(No response)", "Online - Gemini Done", "Analysis Complete", "Your Gemini analysis has finished.")
                return
            self.error.emit("", "Unknown provider")
        except Exception as e:
            self.error.emit("", str(e))


class _QAWorker(QObject):
    finished = pyqtSignal(str)  # answer
    error = pyqtSignal(str)  # error_message

    def __init__(self, window: 'MainWindow', params: dict):
        super().__init__()
        self.window = window
        self.params = params

    @pyqtSlot()
    def run(self):
        try:
            provider = self.params.get("provider")
            model = self.params.get("model")
            messages = self.params.get("messages") or []
            summary = self.params.get("summary")
            input_text = self.params.get("input_text")
            gemini_key = self.params.get("gemini_key")
            doc_key = self.params.get("doc_key", "")

            if not model:
                self.error.emit("No model selected for Q&A")
                return

            # First, classify the question type in the background thread
            try:
                # Extract the latest user question
                question = ""
                for m in reversed(messages or []):
                    if m.get("role") == "user":
                        question = (m.get("content", "") or "").strip()
                        break
                if question:
                    qtype = self.window._classify_question_type(question, provider, model, gemini_key or "")
                    if qtype == "COUNT":
                        try:
                            count_result = self.window._handle_counting_question(question, doc_key)
                            self.finished.emit(count_result or "")
                            return
                        except Exception:
                            # Fall back to normal RAG if counting fails
                            pass
            except Exception:
                # On any classification error, proceed with normal flow
                pass

            if provider == "ollama":
                answer = self.window.answer_question_offline(model, messages, summary, input_text, doc_key)
                self.finished.emit(answer or "")
                return
            if provider == "gemini":
                answer = self.window.answer_question_gemini(model, messages, summary, input_text, gemini_key, doc_key)
                self.finished.emit(answer or "")
                return
            self.error.emit("Unknown provider for Q&A")
        except Exception as e:
            self.error.emit(str(e))


class LargeDocProcessWorker(QObject):
    finished = pyqtSignal(str, int)
    error = pyqtSignal(str)

    def __init__(self, window: 'MainWindow', file_path: str, doc_key: str, is_image: bool = False):
        super().__init__()
        self.window = window
        self.file_path = file_path
        self.doc_key = doc_key
        self.is_image = is_image

    @pyqtSlot()
    def run(self):
        file_type = "image" if self.is_image else "document"
        print(f"LargeDocProcessWorker.run started for {file_type}: {self.file_path}, doc_key: {self.doc_key}")
        try:
            if not os.path.exists(self.file_path):
                self.error.emit(f"File does not exist:\n{self.file_path}")
                return
            
            if self.is_image:
                print("Extracting text from image using OCR...")
            else:
                print("File exists, extracting text")
            
            text = self.window.extract_text_from_file(self.file_path)
            print(f"Text extracted, length: {len(text)}")
            
            if not text or not text.strip():
                if self.is_image:
                    self.error.emit("OCR could not extract any text from the image. The image may be blank or contain no readable text.")
                else:
                    self.error.emit("Could not extract text from the file or file is empty.")
                return
            
            print(f"Calling prepare_document with {len(text)} characters")
            chunk_count = self.window.large_doc_manager.prepare_document(
                self.doc_key,
                self.file_path,
                text,
            )
            print(f"prepare_document completed, chunks: {chunk_count}")
            self.finished.emit(self.doc_key, chunk_count)
        except Exception as e:
            print(f"Exception in LargeDocProcessWorker: {e}")
            error_msg = f"OCR processing failed: {str(e)}" if self.is_image else f"Processing failed: {str(e)}"
            self.error.emit(error_msg)


class PastedTextProcessWorker(QObject):
    finished = pyqtSignal(str, int)
    error = pyqtSignal(str)

    def __init__(self, window: 'MainWindow', doc_key: str, text: str):
        super().__init__()
        self.window = window
        self.doc_key = doc_key
        self.text = text

    @pyqtSlot()
    def run(self):
        print(f"PastedTextProcessWorker.run started for doc_key: {self.doc_key}")
        try:
            clean_text = (self.text or "").strip()
            if not clean_text:
                self.error.emit("Pasted text is empty.")
                return
            # Use a descriptive source label for metadata
            source_label = f"pasted:{self.doc_key}"
            chunk_count = self.window.large_doc_manager.prepare_document(
                self.doc_key,
                source_label,
                clean_text,
            )
            print(f"PastedTextProcessWorker completed, chunks: {chunk_count}")
            self.finished.emit(self.doc_key, chunk_count)
        except Exception as e:
            print(f"Exception in PastedTextProcessWorker: {e}")
            self.error.emit(f"Processing failed: {str(e)}")


class _RefreshWorker(QObject):
    finished = pyqtSignal(str, list, str)  # provider, items, message
    error = pyqtSignal(str)  # error message

    def __init__(self, window: 'MainWindow', params: dict):
        super().__init__()
        self.window = window
        self.params = params

    @pyqtSlot()
    def run(self):
        try:
            provider = self.params.get("provider")
            if provider == "ollama":
                # Distinguish between server-down vs no models installed
                if not self.window.is_ollama_available():
                    self.finished.emit("ollama", [], "Ollama not available")
                    return
                if not self.window.is_ollama_server_running():
                    self.finished.emit("ollama", [], "Ollama server is not running")
                    return
                names = self.window.list_ollama_models()
                msg = "No models installed" if not names else ""
                self.finished.emit("ollama", names, msg)
                return
            if provider == "gemini":
                key = self.window._get_gemini_key()
                if not key:
                    self.finished.emit("gemini", [], "No Key Found")
                    return
                self.finished.emit("gemini", list(self.window.online_models_gemini), "")
                return
            self.error.emit("Unknown provider")
        except Exception as e:
            self.error.emit(str(e))


class _ExportWorker(QObject):
    finished = pyqtSignal(str)  # save_path
    error = pyqtSignal(str)  # error message

    def __init__(self, html: str, save_path: str, is_ar: bool = False):
        super().__init__()
        self.html = html
        self.save_path = save_path
        self.is_ar = is_ar

    def _resolve_export_user_name(self) -> str:
        try:
            user = getattr(AuthState, "user", None) or {}
            if isinstance(user, dict):
                name = str(user.get("name", "") or "").strip()
                email = str(user.get("email", "") or "").strip()
            else:
                name = ""
                email = ""

            if name:
                parts = [p for p in name.split() if p]
                if not parts:
                    return ""
                if len(parts) == 1:
                    return parts[0]
                return f"{parts[0]} {parts[-1]}"

            if email:
                local = email.split("@", 1)[0]
                local_clean = re.sub(r"[._\-]+", " ", local)
                tokens = [t for t in local_clean.split() if t]
                if tokens:
                    if len(tokens) == 1:
                        return tokens[0].capitalize()
                    return f"{tokens[0].capitalize()} {tokens[-1].capitalize()}"
        except Exception:
            pass
        return ""

    @pyqtSlot()
    def run(self):
        try:
            writer = QPdfWriter(self.save_path)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setResolution(300)

            doc = QTextDocument()
            doc.setHtml(self.html)

            dpi = writer.resolution()
            full_rect = writer.pageLayout().fullRectPixels(dpi)
            page_width = float(full_rect.width())
            page_height = float(full_rect.height())

            def mm_to_pixels(mm: float) -> float:
                return mm * dpi / 25.4

            # Use the same margins as defined in _build_export_html's @page rule
            left_margin = mm_to_pixels(18.0)
            right_margin = mm_to_pixels(18.0)
            top_margin = mm_to_pixels(24.0)
            bottom_margin = mm_to_pixels(24.0)

            text_rect = QRectF(
                float(full_rect.x()) + left_margin,
                float(full_rect.y()) + top_margin,
                page_width - left_margin - right_margin,
                page_height - top_margin - bottom_margin,
            )

            # Paginate the document based on the text area
            doc.setPageSize(text_rect.size())
            page_count = doc.pageCount()

            painter = QPainter(writer)
            try:
                export_name = self._resolve_export_user_name()
                footer_text = ""
                if export_name:
                    name_parts = [p for p in str(export_name).split() if p]
                    first_name = name_parts[0] if name_parts else str(export_name)
                    if getattr(self, "is_ar", False):
                        footer_text = f"ملخص تم تصديره بواسطة {export_name}"
                    else:
                        footer_text = f"Summary Exported by {export_name}"

                footer_height = painter.fontMetrics().height() if footer_text else painter.fontMetrics().height()
                footer_rect = QRectF(
                    text_rect.left(),
                    text_rect.bottom(),
                    text_rect.width(),
                    bottom_margin if bottom_margin > footer_height else footer_height,
                )

                for page_index in range(page_count):
                    if page_index > 0:
                        writer.newPage()

                    painter.save()
                    page_top = float(page_index) * doc.pageSize().height()
                    painter.setClipRect(text_rect)
                    painter.translate(text_rect.left(), text_rect.top() - page_top)
                    doc.drawContents(painter)
                    painter.restore()

                    if footer_text:
                        painter.drawText(
                            footer_rect,
                            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                            footer_text,
                        )

                    page_number_text = str(page_index + 1)
                    painter.drawText(
                        footer_rect,
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight,
                        page_number_text,
                    )
            finally:
                try:
                    painter.end()
                except Exception:
                    pass

            self.finished.emit(self.save_path)
        except Exception as e:
            self.error.emit(str(e))
