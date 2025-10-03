from PyQt6.QtWidgets import QDialog
from PyQt6.QtCore import QSettings
from PyQt6.QtCore import QEvent
from PyQt6.QtGui import QGuiApplication
import json
import os
import shutil
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
