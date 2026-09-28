from PyQt6 import QtWidgets


class Ui_SettingsWindow(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Settings")
        Dialog.setStyleSheet("")

        self.layout = QtWidgets.QVBoxLayout(Dialog)
        self.layout.setContentsMargins(12, 12, 12, 12)
        self.layout.setSpacing(6)
        try:
            Dialog.setFixedWidth(420)
            Dialog.setSizeGripEnabled(False)
        except Exception:
            pass

        # Gemini API Key
        self.geminiKeyLabel = QtWidgets.QLabel("Gemini API Key:")
        self.geminiKeyEdit = QtWidgets.QLineEdit()
        self.geminiKeyEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.geminiKeyLabel)

        key_row = QtWidgets.QHBoxLayout()
        key_row.setSpacing(4)
        key_row.addWidget(self.geminiKeyEdit)
        self.toggleApiKeyBtn = QtWidgets.QPushButton()
        self.toggleApiKeyBtn.setFixedSize(32, 32)
        self.toggleApiKeyBtn.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            "QPushButton:hover { background: rgba(0,0,0,20); border-radius: 4px; }"
        )
        key_row.addWidget(self.toggleApiKeyBtn)
        self.layout.addLayout(key_row)

        # Save Button
        self.saveButton = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.saveButton)

        # Toggle Language Button
        self.toggleLanguageButton = QtWidgets.QPushButton("Switch to Arabic")
        self.layout.addWidget(self.toggleLanguageButton)

        Dialog.adjustSize()