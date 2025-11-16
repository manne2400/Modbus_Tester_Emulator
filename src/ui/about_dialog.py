"""About dialog for Modbus Tester"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QTextBrowser
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from src import __version__


class AboutDialog(QDialog):
    """About dialog showing application information"""
    
    def __init__(self, parent=None):
        """Initialize about dialog"""
        super().__init__(parent)
        self.setWindowTitle("Om Modbus Tester")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
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
        <p><b>Modbus Master/Simulator Desktop Applikation</b></p>
        <p>En professionel værktøj til test af Modbus RTU og TCP/IP forbindelser.</p>
        <p><b>Funktioner:</b></p>
        <ul>
            <li>Modbus RTU (RS-485/RS-232) og Modbus TCP/IP</li>
            <li>Flere parallelle sessions</li>
            <li>Læs/skriv coils, discrete inputs, input registers og holding registers</li>
            <li>Omfattende fejlsøgning med hexdump og logging</li>
            <li>Real-time data visning</li>
        </ul>
        <p><b>Teknologi:</b></p>
        <ul>
            <li>Python 3.10+</li>
            <li>PyQt6</li>
            <li>pymodbus</li>
            <li>pyserial</li>
        </ul>
        """)
        layout.addWidget(description)
        
        # Close button
        close_btn = QPushButton("Luk")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
