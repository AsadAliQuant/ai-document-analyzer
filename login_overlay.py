import os
import sys
import webbrowser

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QLineEdit, QPushButton, QHBoxLayout, QMessageBox, QApplication, QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QEvent, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QCursor
from auth import login as auth_login


def _asset_path(*parts) -> str:
    """Resolve a path under the bundled assets dir for both source runs and PyInstaller EXEs."""
    if getattr(sys, 'frozen', False):
        base_dir = getattr(sys, '_MEIPASS', None) or os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, *parts)

_EYE_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
    ' stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
    '<circle cx="12" cy="12" r="3"/>'
    '</svg>'
)

_EYE_OFF_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none"'
    ' stroke="#555" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
    '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8'
    ' a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4'
    ' c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19'
    ' m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>'
    '<line x1="1" y1="1" x2="23" y2="23"/>'
    '</svg>'
)


def _is_dark_mode() -> bool:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        )
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        winreg.CloseKey(key)
        return value == 0
    except Exception:
        return False


def _svg_to_icon(svg_str: str, size: int = 18) -> QIcon:
    try:
        from PyQt6.QtSvg import QSvgRenderer
        renderer = QSvgRenderer(svg_str.encode())
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)
    except Exception:
        return QIcon()


class LoginOverlay(QFrame):
    """Full-window white semi-transparent overlay with login fields."""

    logged_in = pyqtSignal()

    def __init__(self, base_url: str, parent=None):
        super().__init__(parent)
        self.base_url = base_url

        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("LoginOverlay { background-color: #141626; }")

        # Centered layout holding the glass login card
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("loginCard")
        card.setFixedWidth(380)
        card.setStyleSheet(
            "QFrame#loginCard {"
            " background-color: #0d0b16;"
            " border: 1px solid rgba(255, 255, 255, 40);"
            " border-radius: 16px;"
            "}"
        )
        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.setSpacing(12)
        card_layout.setContentsMargins(28, 28, 28, 28)
        layout.addWidget(card)

        logo_pixmap = QPixmap(_asset_path("assets", "logo_2.jpeg"))
        if not logo_pixmap.isNull():
            logo_label = QLabel()
            logo_label.setPixmap(
                logo_pixmap.scaledToWidth(280, Qt.TransformationMode.SmoothTransformation)
            )
            logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            logo_label.setStyleSheet("background: transparent;")
            card_layout.addWidget(logo_label)

        title = QLabel("Sign in")
        # Set font size to 48pt (5x) and bold
        title_font = QFont()
        title_font.setPointSize(75)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Ensure application stylesheets do not shrink this label
        title.setStyleSheet(
            "font-size: 32px; font-weight: 600; color: #FFFFFF; background: transparent;"
        )
        card_layout.addWidget(title)

        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Email")
        self.email_edit.setFixedWidth(320)
        self.email_edit.setStyleSheet("padding: 10px;")
        card_layout.addWidget(self.email_edit, alignment=Qt.AlignmentFlag.AlignHCenter)

        pw_container = QWidget()
        pw_container.setFixedWidth(320)
        pw_container.setStyleSheet(
            "QWidget { background: white; border: 1px solid #ccc; border-radius: 4px; }"
        )
        pw_layout = QHBoxLayout(pw_container)
        pw_layout.setContentsMargins(0, 0, 4, 0)
        pw_layout.setSpacing(0)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Password")
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_edit.setStyleSheet(
            "padding: 10px; border: none; background: transparent; color: #280000;"
        )
        pw_layout.addWidget(self.password_edit)

        self.toggle_pw_btn = QPushButton()
        self.toggle_pw_btn.setFixedSize(32, 32)
        self.toggle_pw_btn.setIcon(_svg_to_icon(_EYE_SVG))
        self.toggle_pw_btn.setIconSize(QSize(18, 18))
        self.toggle_pw_btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; }"
            "QPushButton:hover { background: rgba(0,0,0,20); border-radius: 4px; }"
        )
        self.toggle_pw_btn.clicked.connect(self._toggle_password)
        pw_layout.addWidget(self.toggle_pw_btn)

        card_layout.addWidget(pw_container, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #E0E0E0; background: transparent;")
        card_layout.addWidget(self.status_label)

        forgot_pw_btn = QPushButton("Forgot Password?")
        forgot_pw_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        forgot_pw_btn.setStyleSheet(
            "QPushButton { background: transparent; border: none; color: #7B8CFF;"
            " font-size: 13px; text-decoration: underline; padding: 2px 0; }"
            " QPushButton:hover { color: #A8B4FF; }"
        )
        forgot_pw_btn.clicked.connect(self._on_forgot_password)
        card_layout.addWidget(forgot_pw_btn, alignment=Qt.AlignmentFlag.AlignHCenter)

        buttons = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.cancel_btn = QPushButton("Exit")
        buttons.addWidget(self.login_btn)
        buttons.addWidget(self.cancel_btn)
        card_layout.addLayout(buttons)

        # Signals
        self.login_btn.clicked.connect(self._on_login)
        self.cancel_btn.clicked.connect(self._on_exit)
        self.email_edit.returnPressed.connect(self._on_login)
        self.password_edit.returnPressed.connect(self._on_login)

        self._apply_button_styles()

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

    def _apply_button_styles(self):
        dark = _is_dark_mode()
        if dark:
            login_style = (
                "QPushButton { background-color: #FFFFFF; color: #000000;"
                " border-radius: 4px; padding: 8px 16px; font-weight: bold; }"
                " QPushButton:hover { background-color: #E0E0E0; }"
                " QPushButton:pressed { background-color: #BDBDBD; }"
            )
        else:
            login_style = (
                "QPushButton { background-color: #000000; color: #FFFFFF;"
                " border-radius: 4px; padding: 8px 16px; font-weight: bold; }"
                " QPushButton:hover { background-color: #333333; }"
                " QPushButton:pressed { background-color: #555555; }"
            )
        exit_style = (
            "QPushButton { background-color: #B71C1C; color: white;"
            " border: 1px solid #7F0000; border-radius: 4px; padding: 8px 16px; font-weight: bold; }"
            " QPushButton:hover { background-color: #C62828; }"
            " QPushButton:pressed { background-color: #8E0000; }"
        )
        self.login_btn.setStyleSheet(login_style)
        self.cancel_btn.setStyleSheet(exit_style)

    def show_overlay(self):
        if self.parent():
            self.setGeometry(self.parent().rect())
        self._apply_button_styles()
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
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_pw_btn.setIcon(_svg_to_icon(_EYE_SVG))
        except Exception:
            pass

    def _toggle_password(self):
        if self.password_edit.echoMode() == QLineEdit.EchoMode.Password:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_pw_btn.setIcon(_svg_to_icon(_EYE_OFF_SVG))
        else:
            self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_pw_btn.setIcon(_svg_to_icon(_EYE_SVG))

    def _on_forgot_password(self):
        webbrowser.open("https://ssma.sa/console/?action=forgot-password")

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

class LogoutOverlay(QFrame):
    """Full-window overlay shown during logout."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet("LogoutOverlay { background-color: rgba(20, 22, 38, 220); }")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label = QLabel("Logging you out...")
        self.label.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)
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
        self.raise_()
        self.show()
        
    def hide_overlay(self):
        self.hide()
