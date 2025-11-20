"""Log viewer widget"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QLabel, QFileDialog
)
from PyQt6.QtCore import Qt
from datetime import datetime
from src.models.log_entry import LogEntry, LogDirection
from src.ui.styles.theme import Theme
from typing import List, Optional


class LogViewer(QWidget):
    """Log viewer window for Modbus communication"""
    
    def __init__(self, parent=None):
        """Initialize log viewer"""
        super().__init__(parent)
        self.setWindowTitle("Modbus Log")
        self.setGeometry(100, 100, 1000, 600)
        
        self.entries: List[LogEntry] = []
        
        self._setup_ui()
        self._apply_dark_theme()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear)
        toolbar_layout.addWidget(clear_btn)
        
        toolbar_layout.addWidget(QLabel("Filter:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "TX", "RX", "Error"])
        self.filter_combo.currentTextChanged.connect(self._apply_filter)
        toolbar_layout.addWidget(self.filter_combo)
        
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_log)
        toolbar_layout.addWidget(export_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "Direction", "Hex", "Comment"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
    
    def add_entry(self, entry: LogEntry):
        """Add log entry"""
        self.entries.append(entry)
        self._add_entry_to_table(entry)
    
    def _add_entry_to_table(self, entry: LogEntry):
        """Add entry to table"""
        row = self.table.rowCount()
        self.table.insertRow(row)
        
        # Timestamp
        if isinstance(entry.timestamp, datetime):
            timestamp_str = entry.timestamp.strftime("%H:%M:%S.%f")[:-3]
        else:
            timestamp_str = datetime.fromtimestamp(entry.timestamp).strftime("%H:%M:%S.%f")[:-3]
        timestamp_item = QTableWidgetItem(timestamp_str)
        timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 0, timestamp_item)
        
        # Direction
        direction_item = QTableWidgetItem(entry.direction.value)
        direction_item.setFlags(direction_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if entry.direction == LogDirection.TX:
            direction_item.setForeground(Qt.GlobalColor.blue)
        else:
            direction_item.setForeground(Qt.GlobalColor.green)
        self.table.setItem(row, 1, direction_item)
        
        # Hex
        hex_item = QTableWidgetItem(entry.hex_string)
        hex_item.setFlags(hex_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 2, hex_item)
        
        # Comment
        comment = entry.comment
        if entry.error_description:
            comment = f"{comment} - {entry.error_description}"
        comment_item = QTableWidgetItem(comment)
        comment_item.setFlags(comment_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if entry.error_description:
            comment_item.setForeground(Qt.GlobalColor.red)
        self.table.setItem(row, 3, comment_item)
        
        # Auto-scroll to bottom
        self.table.scrollToBottom()
    
    def _apply_filter(self, filter_text: str):
        """Apply filter to log entries"""
        self.table.setRowCount(0)
        
        for entry in self.entries:
            if filter_text == "All":
                self._add_entry_to_table(entry)
            elif filter_text == "TX" and entry.direction == LogDirection.TX:
                self._add_entry_to_table(entry)
            elif filter_text == "RX" and entry.direction == LogDirection.RX:
                self._add_entry_to_table(entry)
            elif filter_text == "Error" and entry.error_description:
                self._add_entry_to_table(entry)
    
    def clear(self):
        """Clear all log entries"""
        self.entries.clear()
        self.table.setRowCount(0)
    
    def _export_log(self):
        """Export log to file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Log",
            "",
            "Text Files (*.txt);;CSV Files (*.csv)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Time\tDirection\tHex\tComment\n")
                    for entry in self.entries:
                        if isinstance(entry.timestamp, datetime):
                            timestamp_str = entry.timestamp.isoformat()
                        else:
                            timestamp_str = datetime.fromtimestamp(entry.timestamp).isoformat()
                        comment = entry.comment
                        if entry.error_description:
                            comment = f"{comment} - {entry.error_description}"
                        f.write(f"{timestamp_str}\t{entry.direction.value}\t{entry.hex_string}\t{comment}\n")
            except Exception as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Could not export log: {e}")
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)
