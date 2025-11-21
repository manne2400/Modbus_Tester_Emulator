"""Dialog for managing snapshots"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMessageBox, QTextEdit, QGroupBox
)
from PyQt6.QtCore import Qt
from typing import Optional, List
from src.models.snapshot import Snapshot
from src.storage.snapshot_store import SnapshotStore
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SnapshotManagerDialog(QDialog):
    """Dialog for managing snapshots"""
    
    def __init__(self, parent=None, snapshot_store: Optional[SnapshotStore] = None):
        """Initialize snapshot manager dialog"""
        super().__init__(parent)
        self.setWindowTitle("Manage Snapshots")
        self.setMinimumSize(800, 600)
        
        self.snapshot_store = snapshot_store or SnapshotStore()
        self.snapshots: List[Snapshot] = []
        
        self._setup_ui()
        self._apply_dark_theme()
        self._refresh_snapshots()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_snapshots)
        toolbar_layout.addWidget(refresh_btn)
        
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # Snapshots table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Navn", "Dato/Tid", "Scope", "Værdier"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)  # Allow multiple selection with Ctrl/Shift
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.table)
        
        # Details panel
        details_group = QGroupBox("Detaljer")
        details_layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(150)
        details_layout.addWidget(self.details_text)
        
        details_group.setLayout(details_layout)
        layout.addWidget(details_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        view_btn = QPushButton("View")
        view_btn.clicked.connect(self._view_snapshot)
        buttons_layout.addWidget(view_btn)
        
        compare_btn = QPushButton("Compare...")
        compare_btn.clicked.connect(self._compare_snapshots)
        buttons_layout.addWidget(compare_btn)
        
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_snapshot)
        buttons_layout.addWidget(export_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_snapshot)
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _refresh_snapshots(self):
        """Refresh snapshots list"""
        self.snapshots = self.snapshot_store.load_all_snapshots()
        self._update_table()
    
    def _update_table(self):
        """Update table with snapshots"""
        self.table.setRowCount(0)
        
        for snapshot in self.snapshots:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(snapshot.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, snapshot)
            self.table.setItem(row, 0, name_item)
            
            # Timestamp
            timestamp_str = snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            timestamp_item = QTableWidgetItem(timestamp_str)
            timestamp_item.setFlags(timestamp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, timestamp_item)
            
            # Scope
            scope_str = f"{len(snapshot.sessions)} session(s)"
            scope_item = QTableWidgetItem(scope_str)
            scope_item.setFlags(scope_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, scope_item)
            
            # Value count
            value_count = snapshot.get_value_count()
            count_item = QTableWidgetItem(str(value_count))
            count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, count_item)
        
        self.table.resizeColumnsToContents()
    
    def _on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.details_text.clear()
            return
        
        row = selected_rows[0].row()
        name_item = self.table.item(row, 0)
        if not name_item:
            return
        
        snapshot = name_item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(snapshot, Snapshot):
            return
        
        # Build details text
        details = []
        details.append(f"Navn: {snapshot.name}")
        details.append(f"Dato/Tid: {snapshot.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        if snapshot.note:
            details.append(f"Note: {snapshot.note}")
        details.append(f"Antal sessions: {len(snapshot.sessions)}")
        details.append(f"Total værdier: {snapshot.get_value_count()}")
        details.append("\nSessions:")
        for session in snapshot.sessions:
            details.append(f"  - {session.session_name}: {len(session.values)} værdier")
        
        self.details_text.setPlainText("\n".join(details))
    
    def _get_selected_snapshot(self) -> Optional[Snapshot]:
        """Get currently selected snapshot"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        name_item = self.table.item(row, 0)
        if name_item:
            return name_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def _view_snapshot(self):
        """View selected snapshot"""
        snapshot = self._get_selected_snapshot()
        if not snapshot:
            QMessageBox.warning(self, "Ingen snapshot valgt", "Vælg en snapshot at se.")
            return
        
        from src.ui.snapshot_view_dialog import SnapshotViewDialog
        
        dialog = SnapshotViewDialog(self, snapshot)
        dialog.exec()
    
    def _compare_snapshots(self):
        """Compare two snapshots"""
        selected_rows = self.table.selectionModel().selectedRows()
        if len(selected_rows) < 2:
            QMessageBox.warning(
                self,
                "Vælg snapshots",
                "Vælg mindst 2 snapshots at sammenligne.\n\nTip: Hold Ctrl nede og klik på flere rækker for at vælge flere snapshots."
            )
            return
        
        # Get selected snapshots
        snapshots = []
        for row_index in selected_rows:
            name_item = self.table.item(row_index.row(), 0)
            if name_item:
                snapshot = name_item.data(Qt.ItemDataRole.UserRole)
                if isinstance(snapshot, Snapshot):
                    snapshots.append(snapshot)
        
        if len(snapshots) < 2:
            QMessageBox.warning(self, "Fejl", "Kunne ikke hente snapshots.")
            return
        
        # Use first two (or show dialog to select which two if more than 2 selected)
        from src.ui.compare_dialog import CompareDialog
        
        if len(snapshots) == 2:
            dialog = CompareDialog(self, snapshots[0], snapshots[1])
        else:
            # More than 2 selected - use first two
            dialog = CompareDialog(self, snapshots[0], snapshots[1])
            QMessageBox.information(
                self,
                "Info",
                f"{len(snapshots)} snapshots valgt. Sammenligner de første 2: '{snapshots[0].name}' og '{snapshots[1].name}'."
            )
        
        dialog.exec()
    
    def _export_snapshot(self):
        """Export selected snapshot"""
        snapshot = self._get_selected_snapshot()
        if not snapshot:
            QMessageBox.warning(self, "Ingen snapshot valgt", "Vælg en snapshot at eksportere.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        from src.utils.csv_export import export_tags_to_csv
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Snapshot",
            f"{snapshot.name}.csv",
            "CSV Files (*.csv)"
        )
        
        if file_path:
            # Convert snapshot to tags format for export
            from pathlib import Path
            from src.models.tag_definition import TagDefinition, AddressType
            
            # Flatten snapshot values
            all_values = []
            for session in snapshot.sessions:
                for value in session.values:
                    all_values.append({
                        "address": value.address,
                        "name": value.tag_name or f"Address {value.address}",
                        "raw": value.raw_value,
                        "scaled": value.scaled_value,
                        "unit": value.unit or ""
                    })
            
            # For now, just show a message - proper export would need more work
            QMessageBox.information(
                self,
                "Export",
                f"Snapshot export vil blive implementeret med fuld funktionalitet."
            )
    
    def _delete_snapshot(self):
        """Delete selected snapshot"""
        snapshot = self._get_selected_snapshot()
        if not snapshot:
            QMessageBox.warning(self, "Ingen snapshot valgt", "Vælg en snapshot at slette.")
            return
        
        reply = QMessageBox.question(
            self,
            "Slet Snapshot",
            f"Er du sikker på at du vil slette snapshot '{snapshot.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.snapshot_store.delete_snapshot(snapshot.id):
                self._refresh_snapshots()
                QMessageBox.information(self, "Success", f"Snapshot '{snapshot.name}' slettet.")
            else:
                QMessageBox.warning(self, "Error", "Kunne ikke slette snapshot.")
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

