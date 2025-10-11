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

        # Offline readiness panel
        self.offlineGroup = QtWidgets.QGroupBox("Offline Readiness")
        group_layout = QtWidgets.QVBoxLayout(self.offlineGroup)
        group_layout.setContentsMargins(12, 12, 12, 12)
        group_layout.setSpacing(6)

        self.offlineStatusLabel = QtWidgets.QLabel("Checking offline assets...")
        self.offlineStatusLabel.setWordWrap(True)
        group_layout.addWidget(self.offlineStatusLabel)

        self.offlineProgressBar = QtWidgets.QProgressBar()
        self.offlineProgressBar.setRange(0, 100)
        self.offlineProgressBar.setValue(0)
        group_layout.addWidget(self.offlineProgressBar)

        self.offlineDetailsLabel = QtWidgets.QLabel("")
        self.offlineDetailsLabel.setWordWrap(True)
        group_layout.addWidget(self.offlineDetailsLabel)

        self.layout.addWidget(self.offlineGroup)

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