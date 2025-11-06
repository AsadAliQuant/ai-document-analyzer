from PyQt6 import QtCore, QtGui, QtWidgets


class DropArea(QtWidgets.QWidget):
    fileDropped = QtCore.pyqtSignal(str)
    browseRequested = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._is_drag_over = False
        self._accepted_exts = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
        self._preferred_height = 120
        self.setMinimumHeight(self._preferred_height)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.MinimumExpanding,
        )
        self._content = QtWidgets.QVBoxLayout(self)
        self._content.setContentsMargins(0, 0, 0, 0)
        self._default_label_text = "Drag & Drop here (PDF, DOCX, TXT, PNG, JPG) OR click to choose a file"
        self._label = QtWidgets.QLabel(self._default_label_text)
        self._label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._label.setWordWrap(True)
        self._content.addStretch(1)
        self._content.addWidget(self._label)
        # Browse button inside drop area
        self._browseButton = QtWidgets.QPushButton("Choose a File")
        self._browseButton.setFixedSize(180, 36)
        self._browseButton.setStyleSheet(
            "QPushButton {"
            "  font-size: 14px; font-weight: 600;"
            "  background-color: #4C7DFF; color: white;"
            "  border-radius: 6px;"
            "}"
            "QPushButton:hover {"
            "  background-color: #3A67E0;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #2F55B7;"
            "}"
        )
        self._browseButton.clicked.connect(self.browseRequested.emit)
        self._content.addWidget(self._browseButton, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        # Hide the internal button; the whole area is clickable
        self._browseButton.setVisible(False)
        self._content.addStretch(1)

        self._update_style()

    def sizeHint(self) -> QtCore.QSize:  # type: ignore[override]
        return QtCore.QSize(0, self._preferred_height)

    def setSelectedFileName(self, file_path: str):
        name = QtCore.QFileInfo(file_path).fileName()
        if name:
            self._label.setText(name)
        else:
            self._label.setText(self._default_label_text)

    

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            try:
                self.browseRequested.emit()
            except Exception:
                pass
        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            try:
                self.browseRequested.emit()
            except Exception:
                pass
        super().mouseDoubleClickEvent(event)


    def _update_style(self):
        bg = "#fff8f2" if self._is_drag_over else "#fdffffff"
        self.setStyleSheet(
            "border: 2px dashed #570000;"
            "padding: 80px;"
            "border-radius: 8px;"
            f"background-color: {bg};"
        )

    def _has_acceptable_file(self, mime_data: QtCore.QMimeData) -> bool:
        if not mime_data.hasUrls():
            return False
        for url in mime_data.urls():
            path = url.toLocalFile()
            if not path:
                continue
            ext_lower = ("." + QtCore.QFileInfo(path).suffix()).lower()
            if ext_lower in self._accepted_exts:
                return True
        return False

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        if self._has_acceptable_file(event.mimeData()):
            event.acceptProposedAction()
            self._is_drag_over = True
            self._update_style()
        else:
            event.ignore()

    def dragMoveEvent(self, event: QtGui.QDragMoveEvent):
        if self._has_acceptable_file(event.mimeData()):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragLeaveEvent(self, event: QtGui.QDragLeaveEvent):
        self._is_drag_over = False
        self._update_style()
        event.accept()

    def dropEvent(self, event: QtGui.QDropEvent):
        self._is_drag_over = False
        self._update_style()
        if not event.mimeData().hasUrls():
            event.ignore()
            return
        # Use first acceptable file
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if not path:
                continue
            ext_lower = ("." + QtCore.QFileInfo(path).suffix()).lower()
            if ext_lower in self._accepted_exts:
                self.fileDropped.emit(path)
                event.acceptProposedAction()
                return
        event.ignore()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("AI Document Analyzer")
        MainWindow.resize(1200, 700)

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)

        # Edge panel (leftmost) with toggle button outside the sidebar
        self.edgePanel = QtWidgets.QWidget(self.centralwidget)
        self.edgeLayout = QtWidgets.QVBoxLayout(self.edgePanel)
        self.toggleSidebarButton = QtWidgets.QPushButton("☰")
        self.toggleSidebarButton.setFixedWidth(36)
        self.toggleSidebarButton.setVisible(False) # hide the hamburger menu button
        self.edgeLayout.addWidget(self.toggleSidebarButton)
        self.edgeLayout.addStretch(1)

        # Sidebar (Chat History)
        self.sidebarPanel = QtWidgets.QWidget(self.centralwidget)
        self.sidebarLayout = QtWidgets.QVBoxLayout(self.sidebarPanel)
        self.newChatButton = QtWidgets.QPushButton("＋ New Analysis")
        self.historyList = QtWidgets.QListWidget()
        # Placeholder items
        self.historyList.addItems(["Welcome", "Project Proposal", "Meeting Notes"])
        self.sidebarLayout.addWidget(self.newChatButton)
        self.sidebarLayout.addWidget(self.historyList)

        # Settings button (moved to bottom of sidebar) - hidden per requirement
        self.settingsButton = QtWidgets.QPushButton("⚙ Settings")
        self.settingsButton.setVisible(False)
        self.sidebarLayout.addStretch(1)
        self.sidebarLayout.addWidget(self.settingsButton)

        # Left panel (Upload + Tabs)
        self.leftPanel = QtWidgets.QWidget(self.centralwidget)
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)

        # Top controls: Model Source / Models / Refresh / Settings
        self.topBar = QtWidgets.QWidget(self.leftPanel)
        self.topBarLayout = QtWidgets.QHBoxLayout(self.topBar)
        self.modelSourceLabel = QtWidgets.QLabel("Source:")
        self.modelSourceCombo = QtWidgets.QComboBox()
        self.modelSourceCombo.setMinimumWidth(160)
        self.availableModelLabel = QtWidgets.QLabel("Model:")
        self.availableModelCombo = QtWidgets.QComboBox()
        self.availableModelCombo.setMinimumWidth(220)
        self.refreshModelsButton = QtWidgets.QPushButton("Refresh")
        self.topSettingsButton = QtWidgets.QPushButton("Settings")
        self.topBarLayout.addWidget(self.modelSourceLabel)
        self.topBarLayout.addWidget(self.modelSourceCombo)
        self.topBarLayout.addWidget(self.availableModelLabel)
        self.topBarLayout.addWidget(self.availableModelCombo, 1)
        self.topBarLayout.addWidget(self.refreshModelsButton)
        self.topBarLayout.addStretch(1)
        self.topBarLayout.addWidget(self.topSettingsButton)
        self.leftLayout.addWidget(self.topBar)
        self.tabs = QtWidgets.QTabWidget(self.leftPanel)
        self.uploadTab = QtWidgets.QWidget()
        self.pasteTab = QtWidgets.QWidget()

        # Upload tab UI
        self.uploadLayout = QtWidgets.QVBoxLayout(self.uploadTab)

        # Add a stretch to push the widgets down from the top
        self.uploadLayout.addStretch(1)

        # Container for drop area to be centered
        center_container = QtWidgets.QVBoxLayout()
        
        # Drag & Drop area
        self.dropArea = DropArea()

        center_container.addWidget(self.dropArea)

        self.uploadLayout.addLayout(center_container)

        # Add a stretch to push the widgets up from the bottom
        self.uploadLayout.addStretch(1)

        # Paste tab UI
        self.pasteLayout = QtWidgets.QVBoxLayout(self.pasteTab)
        self.pasteTextEdit = QtWidgets.QPlainTextEdit()
        self.pasteTextEdit.setPlaceholderText("Paste your text here...")
        self.pasteLayout.addWidget(self.pasteTextEdit)

        # Add tabs
        self.tabs.addTab(self.uploadTab, "Upload Document")
        self.tabs.addTab(self.pasteTab, "Paste Text")
        self.leftLayout.addWidget(self.tabs)

        # Analyze button
        self.analyzeButton = QtWidgets.QPushButton("Analyze Document")
        self.analyzeButton.setStyleSheet(
            "QPushButton {"
            "  background-color: #2ECC71; color: white;"
            "}"
            "QPushButton:hover {"
            "  background-color: #27AE60;"
            "}"
            "QPushButton:pressed {"
            "  background-color: #1E8449;"
            "}"
        )
        self.leftLayout.addWidget(self.analyzeButton)

        # Right panel (Analysis + Export)
        self.rightPanel = QtWidgets.QWidget(self.centralwidget)
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)

        self.summaryTextEdit = QtWidgets.QPlainTextEdit()
        self.summaryTextEdit.setPlaceholderText("Your analysis will appear here...")
        self.rightLayout.addWidget(self.summaryTextEdit)

        buttonsRow = QtWidgets.QWidget()
        buttonsRowLayout = QtWidgets.QHBoxLayout(buttonsRow)
        buttonsRowLayout.setContentsMargins(0, 0, 0, 0)
        self.copySummaryButton = QtWidgets.QPushButton("Copy Summary")
        self.exportButton = QtWidgets.QPushButton("Export Summary as PDF")
        self.copySummaryButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        self.exportButton.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
        buttonsRowLayout.addWidget(self.copySummaryButton, 1)
        buttonsRowLayout.addWidget(self.exportButton, 1)
        self.rightLayout.addWidget(buttonsRow)

        # Add panels to main layout
        self.horizontalLayout.addWidget(self.edgePanel, 0)
        self.horizontalLayout.addWidget(self.sidebarPanel, 0)
        self.horizontalLayout.addWidget(self.leftPanel, 1)
        self.horizontalLayout.addWidget(self.rightPanel, 2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("AI Document Analyzer", "AI Document Analyzer"))
        self.toggleSidebarButton.setText(_translate("AI Document Analyzer", "☰"))
        self.newChatButton.setText(_translate("AI Document Analyzer", "＋ New Analysis"))
        self.topSettingsButton.setText(_translate("AI Document Analyzer", "Settings"))
        self.modelSourceLabel.setText(_translate("AI Document Analyzer", "Source:"))
        self.availableModelLabel.setText(_translate("AI Document Analyzer", "Model:"))
        self.refreshModelsButton.setText(_translate("AI Document Analyzer", "Refresh"))
        self.tabs.setTabText(self.tabs.indexOf(self.pasteTab), _translate("AI Document Analyzer", "Paste Text"))
        self.analyzeButton.setText(_translate("AI Document Analyzer", "Analyze Document"))
        self.copySummaryButton.setText(_translate("AI Document Analyzer", "Copy Summary"))
        self.exportButton.setText(_translate("AI Document Analyzer", "Export Summary as PDF"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())