from PyQt6 import QtWidgets


class Ui_SettingsWindow(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Settings")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("background-color: #f7f9fc; color: #1f2937;")

        self.layout = QtWidgets.QVBoxLayout(Dialog)

        # Model Selection
        self.modelLabel = QtWidgets.QLabel("Select Model:")
        self.modelComboBox = QtWidgets.QComboBox()
        self.modelComboBox.addItems(["Gemini Flash 2.5", "GPT-5"])
        self.layout.addWidget(self.modelLabel)
        self.layout.addWidget(self.modelComboBox)

        # API Key Input
        self.apiKeyLabel = QtWidgets.QLabel("Enter API Key:")
        self.apiKeyEdit = QtWidgets.QLineEdit()
        self.apiKeyEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.layout.addWidget(self.apiKeyLabel)
        self.layout.addWidget(self.apiKeyEdit)

        # Save Button
        self.saveButton = QtWidgets.QPushButton("Save")
        self.saveButton.setStyleSheet("background-color: #e5e7eb; padding: 10px; border-radius: 5px; border: 1px solid #d1d5db; color: #111827;")
        self.layout.addWidget(self.saveButton)
