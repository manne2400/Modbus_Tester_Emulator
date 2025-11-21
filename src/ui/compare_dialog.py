"""Dialog for comparing two snapshots"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QCheckBox, QGroupBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QFileDialog
from pathlib import Path
from src.models.snapshot import Snapshot
from src.application.snapshot_comparer import SnapshotComparer, SnapshotDifference
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CompareDialog(QDialog):
    """Dialog for comparing two snapshots"""
    
    def __init__(self, parent=None, snapshot_a: Snapshot = None, snapshot_b: Snapshot = None):
        """Initialize compare dialog"""
        super().__init__(parent)
        self.setWindowTitle("Compare Snapshots")
        self.setMinimumSize(1200, 700)
        
        self.snapshot_a = snapshot_a
        self.snapshot_b = snapshot_b
        self.comparer = SnapshotComparer(snapshot_a, snapshot_b) if snapshot_a and snapshot_b else None
        
        self._setup_ui()
        self._apply_dark_theme()
        self._update_comparison()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Summary panel
        summary_group = QGroupBox("Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(100)
        summary_layout.addWidget(self.summary_text)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Filters
        filter_layout = QHBoxLayout()
        
        self.changed_only_check = QCheckBox("Kun ændrede værdier")
        self.changed_only_check.stateChanged.connect(self._update_comparison)
        filter_layout.addWidget(self.changed_only_check)
        
        filter_layout.addStretch()
        
        layout.addLayout(filter_layout)
        
        # Comparison table
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "Session", "Address", "Tag", "Værdi A (Raw)", "Værdi A (Scaled)",
            "Værdi B (Raw)", "Værdi B (Scaled)", "Forskel", "Procent"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        export_btn = QPushButton("Export to CSV...")
        export_btn.clicked.connect(self._export_comparison)
        buttons_layout.addWidget(export_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _update_comparison(self):
        """Update comparison table"""
        if not self.comparer:
            return
        
        # Get differences
        changed_only = self.changed_only_check.isChecked()
        differences = self.comparer.compare(changed_only=changed_only)
        
        # Update summary
        summary = self.comparer.get_summary()
        summary_lines = []
        summary_lines.append(f"Snapshot A: {self.snapshot_a.name} ({self.snapshot_a.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
        summary_lines.append(f"Snapshot B: {self.snapshot_b.name} ({self.snapshot_b.timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
        summary_lines.append(f"\nTotal værdier: {summary['total']}")
        summary_lines.append(f"Ændrede: {summary['changed']}")
        summary_lines.append(f"Tilføjet: {summary['added']}")
        summary_lines.append(f"Fjernet: {summary['removed']}")
        summary_lines.append(f"Uændret: {summary['unchanged']}")
        
        self.summary_text.setPlainText("\n".join(summary_lines))
        
        # Update table
        self.table.setRowCount(0)
        
        for diff in differences:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Session
            session_item = QTableWidgetItem(diff.session_name)
            session_item.setFlags(session_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, session_item)
            
            # Address
            addr_item = QTableWidgetItem(str(diff.address))
            addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, addr_item)
            
            # Tag name
            tag_item = QTableWidgetItem(diff.tag_name or "")
            tag_item.setFlags(tag_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, tag_item)
            
            # Check if value changed
            diff_val = diff.get_scaled_difference()
            pct = diff.get_percentage_change()
            has_changed = (diff_val is not None and diff_val != 0) or (pct is not None and pct != 0)
            
            # Color for changed values (orange/yellow background)
            changed_bg_color = QColor(255, 165, 0, 80)  # Orange with transparency
            changed_brush = QBrush(changed_bg_color)
            
            # Value A (Raw)
            raw_a = str(diff.value_a.raw_value) if diff.value_a and diff.value_a.raw_value is not None else ""
            raw_a_item = QTableWidgetItem(raw_a)
            raw_a_item.setFlags(raw_a_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_changed:
                raw_a_item.setBackground(changed_brush)
            self.table.setItem(row, 3, raw_a_item)
            
            # Value A (Scaled)
            scaled_a = f"{diff.value_a.scaled_value:.2f}" if diff.value_a and diff.value_a.scaled_value is not None else ""
            scaled_a_item = QTableWidgetItem(scaled_a)
            scaled_a_item.setFlags(scaled_a_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_changed:
                scaled_a_item.setBackground(changed_brush)
            self.table.setItem(row, 4, scaled_a_item)
            
            # Value B (Raw)
            raw_b = str(diff.value_b.raw_value) if diff.value_b and diff.value_b.raw_value is not None else ""
            raw_b_item = QTableWidgetItem(raw_b)
            raw_b_item.setFlags(raw_b_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_changed:
                raw_b_item.setBackground(changed_brush)
            self.table.setItem(row, 5, raw_b_item)
            
            # Value B (Scaled)
            scaled_b = f"{diff.value_b.scaled_value:.2f}" if diff.value_b and diff.value_b.scaled_value is not None else ""
            scaled_b_item = QTableWidgetItem(scaled_b)
            scaled_b_item.setFlags(scaled_b_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_changed:
                scaled_b_item.setBackground(changed_brush)
            self.table.setItem(row, 6, scaled_b_item)
            
            # Difference
            diff_str = f"{diff_val:.2f}" if diff_val is not None else ""
            diff_item = QTableWidgetItem(diff_str)
            diff_item.setFlags(diff_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_changed:
                diff_item.setBackground(changed_brush)
                diff_item.setForeground(QColor(255, 255, 255))  # White text for better contrast
            self.table.setItem(row, 7, diff_item)
            
            # Percentage
            pct_str = f"{pct:.1f}%" if pct is not None else ""
            pct_item = QTableWidgetItem(pct_str)
            pct_item.setFlags(pct_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if has_changed:
                pct_item.setBackground(changed_brush)
                pct_item.setForeground(QColor(255, 255, 255))  # White text for better contrast
            self.table.setItem(row, 8, pct_item)
        
        self.table.resizeColumnsToContents()
    
    def _export_comparison(self):
        """Export comparison to CSV"""
        if not self.comparer:
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Comparison",
            f"comparison_{self.snapshot_a.name}_vs_{self.snapshot_b.name}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            try:
                import csv
                
                differences = self.comparer.compare(changed_only=self.changed_only_check.isChecked())
                
                with open(file_path, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    
                    # Header
                    writer.writerow([
                        "Session", "Address", "Tag Name",
                        "Value A (Raw)", "Value A (Scaled)",
                        "Value B (Raw)", "Value B (Scaled)",
                        "Difference", "Percentage Change"
                    ])
                    
                    # Data
                    for diff in differences:
                        raw_a = diff.value_a.raw_value if diff.value_a and diff.value_a.raw_value is not None else ""
                        scaled_a = diff.value_a.scaled_value if diff.value_a and diff.value_a.scaled_value is not None else ""
                        raw_b = diff.value_b.raw_value if diff.value_b and diff.value_b.raw_value is not None else ""
                        scaled_b = diff.value_b.scaled_value if diff.value_b and diff.value_b.scaled_value is not None else ""
                        diff_val = diff.get_scaled_difference()
                        pct = diff.get_percentage_change()
                        
                        writer.writerow([
                            diff.session_name,
                            diff.address,
                            diff.tag_name or "",
                            raw_a,
                            scaled_a,
                            raw_b,
                            scaled_b,
                            diff_val if diff_val is not None else "",
                            f"{pct:.1f}%" if pct is not None else ""
                        ])
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Comparison eksporteret til {file_path}."
                )
            except Exception as e:
                logger.error(f"Failed to export comparison: {e}")
                QMessageBox.warning(self, "Error", f"Kunne ikke eksportere: {e}")
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

