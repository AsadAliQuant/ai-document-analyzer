from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("AI Document Analyzer")
        MainWindow.resize(1200, 700)
        MainWindow.setStyleSheet("background-color: #f7f9fc; color: #1f2937;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)

        # Sidebar (Chat History)
        self.sidebarPanel = QtWidgets.QWidget(self.centralwidget)
        self.sidebarLayout = QtWidgets.QVBoxLayout(self.sidebarPanel)
        self.newChatButton = QtWidgets.QPushButton("＋ New Chat")
        self.newChatButton.setStyleSheet("background-color: #e5e7eb; padding: 10px; border-radius: 5px; border: 1px solid #d1d5db; color: #111827;")
        self.historyList = QtWidgets.QListWidget()
        self.historyList.setStyleSheet("QListWidget { background-color: #ffffff; border: 1px solid #d1d5db; } QListWidget::item { padding: 8px; } QListWidget::item:selected { background-color: #e5e7eb; }")
        # Placeholder items
        self.historyList.addItems(["Welcome", "Project Proposal", "Meeting Notes"])
        self.sidebarLayout.addWidget(self.newChatButton)
        self.sidebarLayout.addWidget(self.historyList)

        # Settings button (moved to bottom of sidebar)
        self.settingsButton = QtWidgets.QPushButton("⚙ Settings")
        self.settingsButton.setStyleSheet("background-color: #e5e7eb; padding: 8px; border-radius: 5px; border: 1px solid #d1d5db; color: #111827;")
        self.sidebarLayout.addStretch(1)
        self.sidebarLayout.addWidget(self.settingsButton)

        # Left panel (Upload + Tabs)
        self.leftPanel = QtWidgets.QWidget(self.centralwidget)
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)

        # Tabs: Upload / Paste
        self.tabs = QtWidgets.QTabWidget(self.leftPanel)
        self.tabs.setStyleSheet("QTabWidget::pane { border: 1px solid #d1d5db; }")
        self.uploadTab = QtWidgets.QWidget()
        self.pasteTab = QtWidgets.QWidget()

        # Upload tab UI
        self.uploadLayout = QtWidgets.QVBoxLayout(self.uploadTab)
        self.chooseFileButton = QtWidgets.QPushButton("Choose a File")
        self.chooseFileButton.setStyleSheet("background-color: #e5e7eb; padding: 10px; border-radius: 5px; border: 1px solid #d1d5db; color: #111827;")
        self.filePathLabel = QtWidgets.QLabel("PDF, DOCX, PNG, or JPG")
        self.filePathLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.uploadLayout.addWidget(self.chooseFileButton)
        self.uploadLayout.addWidget(self.filePathLabel)

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
        self.analyzeButton.setStyleSheet("background-color: #e5e7eb; padding: 12px; font-weight: bold; border-radius: 5px; border: 1px solid #d1d5db; color: #111827;")
        self.leftLayout.addWidget(self.analyzeButton)

        # Right panel (Analysis + Export)
        self.rightPanel = QtWidgets.QWidget(self.centralwidget)
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)

        # Toggle sidebar button (always visible in main area)
        self.toggleSidebarButton = QtWidgets.QPushButton("☰")
        self.toggleSidebarButton.setFixedWidth(36)
        self.toggleSidebarButton.setStyleSheet("background-color: #e5e7eb; padding: 6px; border-radius: 5px; text-align: center; border: 1px solid #d1d5db; color: #111827;")
        self.rightLayout.addWidget(self.toggleSidebarButton)

        self.summaryTextEdit = QtWidgets.QPlainTextEdit()
        self.summaryTextEdit.setPlaceholderText("Your analysis will appear here...")
        self.rightLayout.addWidget(self.summaryTextEdit)

        self.exportButton = QtWidgets.QPushButton("Export Summary as PDF")
        self.exportButton.setStyleSheet("background-color: #e5e7eb; padding: 12px; font-weight: bold; border-radius: 5px; border: 1px solid #d1d5db; color: #111827;")
        self.rightLayout.addWidget(self.exportButton)

        # Add panels to main layout
        self.horizontalLayout.addWidget(self.sidebarPanel, 0)
        self.horizontalLayout.addWidget(self.leftPanel, 1)
        self.horizontalLayout.addWidget(self.rightPanel, 2)
        MainWindow.setCentralWidget(self.centralwidget)
