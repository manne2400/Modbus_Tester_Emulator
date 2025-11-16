"""Status bar widget"""
from PyQt6.QtWidgets import QLabel


class StatusBar(QLabel):
    """Status bar widget for session status"""
    
    def __init__(self):
        """Initialize status bar"""
        super().__init__()
        self.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        self.update_status("Klar")
    
    def update_status(self, message: str, error: bool = False):
        """Update status message"""
        if error:
            self.setStyleSheet("padding: 5px; background-color: #ffcccc;")
        else:
            self.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        self.setText(message)
