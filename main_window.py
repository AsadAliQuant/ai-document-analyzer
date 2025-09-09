from PyQt6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve
from ui_main_window import Ui_MainWindow
from settings_window import SettingsWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Settings Window
        self.settings_window = SettingsWindow()

        # Sidebar toggle state and animation setup
        self.sidebar_visible = True
        self.sidebar_expanded_width = 240
        self.ui.sidebarPanel.setMinimumWidth(0)
        self.ui.sidebarPanel.setMaximumWidth(self.sidebar_expanded_width)
        self.sidebar_animation = QPropertyAnimation(self.ui.sidebarPanel, b"maximumWidth")
        self.sidebar_animation.setDuration(250)
        self.sidebar_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Connect buttons
        self.ui.chooseFileButton.clicked.connect(self.choose_file)
        self.ui.analyzeButton.clicked.connect(self.fake_analyze)
        self.ui.settingsButton.clicked.connect(self.open_settings)
        self.ui.exportButton.clicked.connect(self.export_pdf)
        self.ui.toggleSidebarButton.clicked.connect(self.toggle_sidebar)

    def choose_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilters(["Documents (*.pdf *.doc *.docx)", "Images (*.png *.jpg *.jpeg)"])
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self.ui.filePathEdit.setPlainText(selected_file)

    def fake_analyze(self):
        self.ui.summaryTextEdit.setPlainText(
            "🔹 Document successfully uploaded.\n"
            "🔹 Analysis is not implemented yet.\n"
            "🔹 This is a UI preview only."
        )

    def open_settings(self):
        self.settings_window.show()

    def export_pdf(self):
        save_dialog = QFileDialog(self)
        save_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        save_dialog.setNameFilters(["PDF Files (*.pdf)"])
        if save_dialog.exec():
            save_path = save_dialog.selectedFiles()[0]
            QMessageBox.information(self, "Export", f"Summary exported to:\n{save_path}")

    def toggle_sidebar(self):
        # Animate sidebar open/close by changing maximumWidth
        self.sidebar_animation.stop()
        if self.sidebar_visible:
            start_value = self.ui.sidebarPanel.maximumWidth()
            end_value = 0
            self.sidebar_animation.setStartValue(start_value)
            self.sidebar_animation.setEndValue(end_value)
            self.sidebar_animation.start()
            self.sidebar_visible = False
        else:
            # Ensure visible before expanding
            self.ui.sidebarPanel.setVisible(True)
            start_value = self.ui.sidebarPanel.maximumWidth()
            end_value = self.sidebar_expanded_width
            self.sidebar_animation.setStartValue(start_value)
            self.sidebar_animation.setEndValue(end_value)
            self.sidebar_animation.start()
            self.sidebar_visible = True
