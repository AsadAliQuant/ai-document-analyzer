from PyQt6 import QtWidgets


class Ui_SettingsWindow(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Settings")
        Dialog.resize(520, 320)
        Dialog.setStyleSheet("")

        self.layout = QtWidgets.QVBoxLayout(Dialog)
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(8)
        # Keep height compact but allow wider content
        try:
            Dialog.setFixedHeight(320)
            Dialog.setMinimumWidth(520)
        except Exception:
            pass

        # Gemini API Key
        self.geminiKeyLabel = QtWidgets.QLabel("Gemini API Key:")
        self.geminiKeyEdit = QtWidgets.QLineEdit()
        self.geminiKeyEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.geminiKeyLabel)
        self.layout.addWidget(self.geminiKeyEdit)

        # Save Button
        self.saveButton = QtWidgets.QPushButton("Save")
        self.layout.addWidget(self.saveButton)

        # Toggle Language Button
        self.toggleLanguageButton = QtWidgets.QPushButton("Switch to Arabic")
        self.layout.addWidget(self.toggleLanguageButton)