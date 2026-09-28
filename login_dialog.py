from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
from auth import login as auth_login

class LoginDialog(QDialog):
    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url
        self.setWindowTitle("Login")
        self.setModal(True)
        layout = QVBoxLayout(self)
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.email_edit.setStyleSheet("padding: 10px;")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet("padding: 10px; color: #280000;")
        self.status_label = QLabel("")
        self.login_btn = QPushButton("Login")
        self.cancel_btn = QPushButton("Cancel")
        btns = QHBoxLayout()
        btns.addWidget(self.login_btn)
        btns.addWidget(self.cancel_btn)
        layout.addWidget(self.email_edit)
        layout.addWidget(self.password_edit)
        layout.addWidget(self.status_label)
        layout.addLayout(btns)
        self.login_btn.clicked.connect(self._on_login)
        self.cancel_btn.clicked.connect(self.reject)
        self.email_edit.returnPressed.connect(self._on_login)
        self.password_edit.returnPressed.connect(self._on_login)

    def _on_login(self):
        email = (self.email_edit.text() or "").strip()
        password = self.password_edit.text() or ""
        if not email or not password:
            QMessageBox.warning(self, "Login", "Username and password are required.")
            return
        self.login_btn.setEnabled(False)
        self.cancel_btn.setEnabled(False)
        self.status_label.setText("Signing in...")
        try:
            auth_login(self.base_url, email, password)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Login Failed", str(e))
            self.status_label.setText("")
            self.login_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
