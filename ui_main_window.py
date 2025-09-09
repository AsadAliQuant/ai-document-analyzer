from PyQt6 import QtCore, QtGui, QtWidgets


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

        # Settings button (moved to bottom of sidebar)
        self.settingsButton = QtWidgets.QPushButton("⚙ Settings")
        self.sidebarLayout.addStretch(1)
        self.sidebarLayout.addWidget(self.settingsButton)

        # Left panel (Upload + Tabs)
        self.leftPanel = QtWidgets.QWidget(self.centralwidget)
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)

        # Tabs: Upload / Paste
        self.tabs = QtWidgets.QTabWidget(self.leftPanel)
        self.uploadTab = QtWidgets.QWidget()
        self.pasteTab = QtWidgets.QWidget()

        # Upload tab UI
        self.uploadLayout = QtWidgets.QVBoxLayout(self.uploadTab)
        self.chooseFileButton = QtWidgets.QPushButton("Choose a File")
        self.filePathEdit = QtWidgets.QPlainTextEdit()
        self.filePathEdit.setPlaceholderText("PDF, DOCX, PNG, or JPG")
        self.filePathEdit.setReadOnly(True)
        self.filePathEdit.setWordWrapMode(QtGui.QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.filePathEdit.setFixedHeight(60)
        self.uploadLayout.addWidget(self.chooseFileButton)
        self.uploadLayout.addWidget(self.filePathEdit)

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
        self.leftLayout.addWidget(self.analyzeButton)

        # Right panel (Analysis + Export)
        self.rightPanel = QtWidgets.QWidget(self.centralwidget)
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)

        self.summaryTextEdit = QtWidgets.QPlainTextEdit()
        self.summaryTextEdit.setPlaceholderText("Your analysis will appear here...")
        self.rightLayout.addWidget(self.summaryTextEdit)

        self.exportButton = QtWidgets.QPushButton("Export Summary as PDF")
        self.rightLayout.addWidget(self.exportButton)

        # Add panels to main layout
        self.horizontalLayout.addWidget(self.edgePanel, 0)
        self.horizontalLayout.addWidget(self.sidebarPanel, 0)
        self.horizontalLayout.addWidget(self.leftPanel, 1)
        self.horizontalLayout.addWidget(self.rightPanel, 2)
        MainWindow.setCentralWidget(self.centralwidget)
