"""About dialog for Modbus Tester"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src import __version__
from src.ui.styles.theme import Theme


class AboutDialog(QDialog):
    """About dialog showing application information"""
    
    def __init__(self, parent=None):
        """Initialize about dialog"""
        super().__init__(parent)
        self.setWindowTitle("About Modbus Tester")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self._setup_ui()
        self._apply_dark_theme()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_STANDARD)
        layout.setContentsMargins(Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD)
        
        # Title
        title = QLabel("Modbus Tester")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Version
        version_label = QLabel(f"Version {__version__}")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        # Description
        description = QTextBrowser()
        description.setReadOnly(True)
        description.setMaximumHeight(200)
        description.setHtml("""
        <p><b>Modbus Master/Simulator Desktop Application</b></p>
        <p>A professional tool for testing Modbus RTU and TCP/IP connections.</p>
        <p><b>Features:</b></p>
        <ul>
            <li>Modbus RTU (RS-485/RS-232) and Modbus TCP/IP</li>
            <li>Multiple parallel sessions</li>
            <li>Read/write coils, discrete inputs, input registers and holding registers</li>
            <li>Comprehensive debugging with hexdump and logging</li>
            <li>Real-time data display</li>
        </ul>
        <p><b>Technology:</b></p>
        <ul>
            <li>Python 3.10+</li>
            <li>PyQt6</li>
            <li>pymodbus</li>
            <li>pyserial</li>
        </ul>
        """)
        layout.addWidget(description)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)
