from PyQt6 import QtWidgets


class Ui_SettingsWindow(object):
    def setupUi(self, Dialog):
        Dialog.setWindowTitle("Settings")
        Dialog.resize(400, 300)
        Dialog.setStyleSheet("")

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
        self.layout.addWidget(self.saveButton)
