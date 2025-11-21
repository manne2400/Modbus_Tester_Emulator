"""Dialog for viewing snapshot details"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from src.models.snapshot import Snapshot
from src.ui.styles.theme import Theme


class SnapshotViewDialog(QDialog):
    """Dialog for viewing snapshot details"""
    
    def __init__(self, parent=None, snapshot: Snapshot = None):
        """Initialize snapshot view dialog"""
        super().__init__(parent)
        self.setWindowTitle(f"View Snapshot: {snapshot.name if snapshot else 'Unknown'}")
        self.setMinimumSize(900, 600)
        
        self.snapshot = snapshot
        
        self._setup_ui()
        self._apply_dark_theme()
        self._load_snapshot()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Info panel
        info_group = QGroupBox("Snapshot Information")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Values table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "Session", "Address", "Tag Name", "Raw Value", "Scaled Value", "Status"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_snapshot(self):
        """Load snapshot data"""
        if not self.snapshot:
            return
        
        # Set info text
        info_lines = []
        info_lines.append(f"Navn: {self.snapshot.name}")
        info_lines.append(f"Dato/Tid: {self.snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if self.snapshot.note:
            info_lines.append(f"Note: {self.snapshot.note}")
        info_lines.append(f"Antal sessions: {len(self.snapshot.sessions)}")
        info_lines.append(f"Total værdier: {self.snapshot.get_value_count()}")
        
        self.info_text.setPlainText("\n".join(info_lines))
        
        # Populate table
        self.table.setRowCount(0)
        
        for session in self.snapshot.sessions:
            for value in session.values:
                row = self.table.rowCount()
                self.table.insertRow(row)
                
                # Session
                session_item = QTableWidgetItem(session.session_name)
                session_item.setFlags(session_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 0, session_item)
                
                # Address
                addr_item = QTableWidgetItem(str(value.address))
                addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 1, addr_item)
                
                # Tag name
                tag_item = QTableWidgetItem(value.tag_name or "")
                tag_item.setFlags(tag_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 2, tag_item)
                
                # Raw value
                raw_item = QTableWidgetItem(str(value.raw_value) if value.raw_value is not None else "")
                raw_item.setFlags(raw_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 3, raw_item)
                
                # Scaled value
                scaled_str = f"{value.scaled_value:.2f}" if value.scaled_value is not None else ""
                scaled_item = QTableWidgetItem(scaled_str)
                scaled_item.setFlags(scaled_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 4, scaled_item)
                
                # Status
                status_item = QTableWidgetItem(value.status.value)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if value.status.value == "OK":
                    status_item.setForeground(Qt.GlobalColor.green)
                else:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.table.setItem(row, 5, status_item)
        
        self.table.resizeColumnsToContents()
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

