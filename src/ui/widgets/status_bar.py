"""Status bar widget"""
from PyQt6.QtWidgets import QLabel, QSizePolicy
from PyQt6.QtCore import Qt, QSize


class StatusBar(QLabel):
    """Status bar widget for session status"""
    
    def __init__(self):
        """Initialize status bar"""
        super().__init__()
        # Set size policy to prevent expansion - use Maximum instead of Preferred
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        # Set fixed height to prevent resizing
        self.setFixedHeight(35)
        # Align text to left
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        # Set word wrap to false to prevent text wrapping
        self.setWordWrap(False)
        self.setStyleSheet("""
            QLabel {
                padding: 6px 12px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                font-size: 10pt;
            }
        """)
        # Set initial text to calculate size
        self.setText("Ready")
        # Set initial size constraints based on content
        self._update_size_constraints()
        self.update_status("Ready")
    
    def _update_size_constraints(self):
        """Update size constraints based on current content"""
        hint = super().sizeHint()
        if hint.width() > 0:
            # Set maximum width based on content with some padding
            max_width = min(hint.width() + 20, 500)
            self.setMaximumWidth(max_width)
            # Also set minimum width to prevent shrinking below content
            self.setMinimumWidth(hint.width())
    
    def sizeHint(self) -> QSize:
        """Return size hint based on content"""
        hint = super().sizeHint()
        # Limit width to content size, but allow up to reasonable maximum
        if hint.width() > 500:
            hint.setWidth(500)
        return hint
    
    def minimumSizeHint(self) -> QSize:
        """Return minimum size hint"""
        hint = super().minimumSizeHint()
        # Ensure minimum width is based on content
        return hint
    
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
        # Update size constraints based on new content
        self._update_size_constraints()
        # Force geometry update to prevent expansion
        self.updateGeometry()
