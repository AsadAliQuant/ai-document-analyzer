from PyQt6.QtWidgets import QDialog
from ui_settings_window import Ui_SettingsWindow


class SettingsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SettingsWindow()
        self.ui.setupUi(self)
