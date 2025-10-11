from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QSettings
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QGuiApplication
import json
import os
import shutil
from typing import Dict, Optional
from ui_settings_window import Ui_SettingsWindow


class SettingsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
        self.settings = QSettings()
        self.config_path = self._init_config_path()
        # Track current language locally for runtime only (no persistence)
        self._current_lang = "en"
        self._offline_state: Dict[str, object] = {}

        # Load saved settings
        self._load_settings()

        # Wire actions
        self.ui.saveButton.clicked.connect(self._save_settings)
        # Language toggle
        if hasattr(self.ui, 'toggleLanguageButton'):
            self.ui.toggleLanguageButton.clicked.connect(self._toggle_language)
            # Sync initial label based on saved language
            self._sync_language_button()

    def _load_settings(self):
        # Notifications are always enabled by default; keep the value in QSettings for backward compatibility
        self.settings.setValue("notificationsEnabled", True)

        gemini_qsettings_key = self.settings.value("GOOGLE_API_KEY", "", type=str)
        if hasattr(self.ui, 'geminiKeyEdit'):
            self.ui.geminiKeyEdit.setText(gemini_qsettings_key)

        # Load API keys from config.json if present
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    gemini_key = data.get("GOOGLE_API_KEY", "")
                    if gemini_key:
                        self.settings.setValue("GOOGLE_API_KEY", gemini_key)
                        if hasattr(self.ui, 'geminiKeyEdit'):
                            self.ui.geminiKeyEdit.setText(gemini_key)
        except Exception:
            pass

    def _save_settings(self):
        # Notifications always on; no UI control
        self.settings.setValue("notificationsEnabled", True)
        # Also persist keys to config.json for portability
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            existing = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    existing = json.load(f)
            if hasattr(self.ui, 'geminiKeyEdit'):
                existing["GOOGLE_API_KEY"] = self.ui.geminiKeyEdit.text()
                self.settings.setValue("GOOGLE_API_KEY", self.ui.geminiKeyEdit.text())
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(existing, f, indent=2)
        except Exception:
            pass
        self.accept()

    def _toggle_language(self):
        current = getattr(self, "_current_lang", "en")
        new_lang = "ar" if current != "ar" else "en"
        self._current_lang = new_lang
        try:
            self.apply_language(new_lang)
        except Exception:
            pass
        if self.parent() is not None and hasattr(self.parent(), 'apply_language'):
            try:
                self.parent().apply_language(new_lang)
            except Exception:
                pass
        self._sync_language_button()

    def notifications_enabled(self) -> bool:
        # Always enabled per new requirement
        return True

    def _init_config_path(self) -> str:
        # %APPDATA%/AI Document Analyzer/config.json; copy from cwd on first run if present
        try:
            appdata = os.getenv("APPDATA") or os.path.expanduser("~")
            config_dir = os.path.join(appdata, "AI Document Analyzer")
            os.makedirs(config_dir, exist_ok=True)
            target = os.path.join(config_dir, "config.json")
            # Copy once from working directory if target missing but a local config exists
            local = os.path.join(os.getcwd(), "config.json")
            if not os.path.exists(target) and os.path.exists(local):
                try:
                    shutil.copy2(local, target)
                except Exception:
                    pass
            return target
        except Exception:
            # Fallback to current working directory
            return os.path.join(os.getcwd(), "config.json")

    def apply_language(self, lang: str):
        is_ar = (lang == "ar")
        try:
            self.setWindowTitle("الإعدادات" if is_ar else "Settings")
            if hasattr(self.ui, 'offlineGroup'):
                self.ui.offlineGroup.setTitle("الجاهزية بدون إنترنت" if is_ar else "Offline Readiness")
            if hasattr(self.ui, 'offlineStatusLabel'):
                status = self.ui.offlineStatusLabel.text() or ("جاهز للاستخدام بدون اتصال" if is_ar else "READY for Offline use")
                if self.is_offline_ready():
                    status = "جاهز للاستخدام بدون اتصال" if is_ar else "READY for Offline use"
                self.ui.offlineStatusLabel.setText(status)
            if hasattr(self.ui, 'geminiKeyLabel'):
                self.ui.geminiKeyLabel.setText("مفتاح Gemini:" if is_ar else "Gemini API Key:")
            if hasattr(self.ui, 'saveButton'):
                self.ui.saveButton.setText("حفظ" if is_ar else "Save")
            if hasattr(self.ui, 'toggleLanguageButton'):
                # Button shows the action to switch to the other language
                self.ui.toggleLanguageButton.setText("التحويل إلى الإنجليزية" if is_ar else "Switch to Arabic")
        except Exception:
            pass

    def _sync_language_button(self):
        lang = getattr(self, "_current_lang", "en")
        try:
            self.apply_language(lang)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Offline readiness UI helpers
    # ------------------------------------------------------------------
    def apply_offline_state(self, state: Optional[Dict[str, object]] = None):
        if state is not None:
            self._offline_state = dict(state)
        state = getattr(self, "_offline_state", {}) or {}
        ready = bool(state.get("offline_ready", False))
        tasks = state.get("tasks", {}) if isinstance(state.get("tasks"), dict) else {}

        if hasattr(self.ui, 'offlineProgressBar'):
            value = 100 if ready else int(min(100, max(0, state.get("progress", 0))))
            self.ui.offlineProgressBar.setValue(value)

        if hasattr(self.ui, 'offlineStatusLabel'):
            if ready:
                text = "READY for Offline use"
            else:
                text = "Preparing offline assets..."
            self.ui.offlineStatusLabel.setText(text)

        if hasattr(self.ui, 'offlineDetailsLabel'):
            if tasks:
                lines = []
                for name, status in tasks.items():
                    label = {
                        "embeddings": "Embedding model",
                        "easyocr": "EasyOCR weights",
                    }.get(name, name)
                    lines.append(f"{label}: {'Ready' if status else 'Pending'}")
                self.ui.offlineDetailsLabel.setText("\n".join(lines))
            else:
                self.ui.offlineDetailsLabel.setText("")

        # Ensure language-specific text if needed
        self._sync_language_button()

    def apply_offline_progress(self, percent: float, message: str):
        if hasattr(self.ui, 'offlineProgressBar'):
            self.ui.offlineProgressBar.setValue(int(max(0, min(100, percent))))
        if hasattr(self.ui, 'offlineStatusLabel') and message:
            self.ui.offlineStatusLabel.setText(message)
        # Persist last progress into temporary state
        if isinstance(self._offline_state, dict):
            self._offline_state['progress'] = percent
        self._sync_language_button()

    def is_offline_ready(self) -> bool:
        state = getattr(self, "_offline_state", {}) or {}
        return bool(state.get("offline_ready", False))
