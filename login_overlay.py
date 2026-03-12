from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QApplication
from PyQt6.QtCore import Qt, pyqtSignal, QEvent
from PyQt6.QtGui import QFont
from auth import login as auth_login


class LoginOverlay(QFrame):
    """Full-window white semi-transparent overlay with login fields."""

    logged_in = pyqtSignal()

    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url

        # Grey background
        self.setStyleSheet(
            """
            QFrame {
                background-color: rgba(128, 128, 128, 255);
            }
            """
        )
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Centered layout for login form
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        title = QLabel("Sign in")
        # Set font size to 48pt (5x) and bold
        title_font = QFont()
        title_font.setPointSize(75)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Ensure application stylesheets do not shrink this label
        title.setStyleSheet("font-size: 32px; font-weight: 600;")
        layout.addWidget(title)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.email_edit.setFixedWidth(320)
        self.email_edit.setStyleSheet("padding: 10px;")
        layout.addWidget(self.email_edit, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setFixedWidth(320)
        self.password_edit.setStyleSheet("padding: 10px;")
        layout.addWidget(self.password_edit, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        buttons = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.cancel_btn = QPushButton("Exit")
        buttons.addWidget(self.login_btn)
        buttons.addWidget(self.cancel_btn)
        layout.addLayout(buttons)

        # Signals
        self.login_btn.clicked.connect(self._on_login)
        self.cancel_btn.clicked.connect(self._on_exit)
        self.email_edit.returnPressed.connect(self._on_login)
        self.password_edit.returnPressed.connect(self._on_login)

        # Track parent resize to keep full coverage
        if parent is not None:
            parent.installEventFilter(self)

        self.hide()

    def eventFilter(self, obj, event):
        if obj is self.parent() and event.type() == QEvent.Type.Resize:
            try:
                self.setGeometry(self.parent().rect())
            except Exception:
                pass
        return super().eventFilter(obj, event)

    def show_overlay(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        # Reset any stale UI state from prior use
        try:
            self._reset_form_state()
        except Exception:
            pass
        self.raise_()
        self.show()
        try:
            self.email_edit.setFocus()
        except Exception:
            pass

    def hide_overlay(self):
        self.hide()

    def _reset_form_state(self):
        try:
            self.status_label.setText("")
        except Exception:
            pass
        try:
            self.login_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
        except Exception:
            pass
        try:
            self.password_edit.clear()
        except Exception:
            pass

    def _on_exit(self):
        app = QApplication.instance()
        if app:
            app.quit()

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
            self.logged_in.emit()
        except Exception as e:
            QMessageBox.critical(self, "Login Failed", str(e))
            self.status_label.setText("")
            self.login_btn.setEnabled(True)
            self.cancel_btn.setEnabled(True)
