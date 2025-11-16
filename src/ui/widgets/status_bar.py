"""Status bar widget"""
from PyQt6.QtWidgets import QLabel


class StatusBar(QLabel):
    """Status bar widget for session status"""
    
    def __init__(self):
        """Initialize status bar"""
        super().__init__()
        self.setStyleSheet("""
            QLabel {
                padding: 6px 12px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                font-size: 10pt;
            }
        """)
        self.update_status("Klar")
    
    def update_status(self, message: str, error: bool = False):
        """Update status message"""
        if error:
            self.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #ffebee;
                    border: 1px solid #ef5350;
                    border-radius: 3px;
                    color: #c62828;
                    font-size: 10pt;
                    font-weight: 500;
                }
            """)
        else:
            self.setStyleSheet("""
                QLabel {
                    padding: 6px 12px;
                    background-color: #e8f5e9;
                    border: 1px solid #66bb6a;
                    border-radius: 3px;
                    color: #2e7d32;
                    font-size: 10pt;
                }
            """)
        self.setText(message)
