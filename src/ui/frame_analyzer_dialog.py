"""Frame Analyzer dialog for analyzing Modbus frames"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem,
    QPushButton, QComboBox, QLabel, QLineEdit, QTextEdit, QGroupBox, QFormLayout,
    QCheckBox, QSpinBox, QSplitter, QWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from datetime import datetime
from typing import Optional, List
from src.models.trace_entry import TraceEntry, TraceDirection, TraceStatus
from src.application.trace_store import TraceStore
from src.application.diagnostics_engine import DiagnosticsEngine, DiagnosticFinding
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FrameAnalyzerDialog(QDialog):
    """Dialog for analyzing Modbus frames and traces"""
    
    def __init__(self, parent=None, trace_store: Optional[TraceStore] = None):
        """Initialize frame analyzer dialog"""
        super().__init__(parent)
        self.setWindowTitle("Frame Analyzer")
        self.setMinimumSize(1200, 800)
        
        self.trace_store = trace_store
        self.diagnostics_engine = DiagnosticsEngine(trace_store) if trace_store else None
        
        self._setup_ui()
        self._apply_dark_theme()
        self._refresh_data()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_data)
        toolbar_layout.addWidget(refresh_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_data)
        toolbar_layout.addWidget(clear_btn)
        
        toolbar_layout.addStretch()
        
        # Filters
        toolbar_layout.addWidget(QLabel("Filters:"))
        
        self.errors_only_check = QCheckBox("Kun fejl")
        self.errors_only_check.stateChanged.connect(self._apply_filters)
        toolbar_layout.addWidget(self.errors_only_check)
        
        self.direction_combo = QComboBox()
        self.direction_combo.addItems(["Alle", "TX", "RX"])
        self.direction_combo.currentTextChanged.connect(self._apply_filters)
        toolbar_layout.addWidget(QLabel("Retning:"))
        toolbar_layout.addWidget(self.direction_combo)
        
        self.slave_id_edit = QLineEdit()
        self.slave_id_edit.setPlaceholderText("Slave ID")
        self.slave_id_edit.setMaximumWidth(80)
        self.slave_id_edit.textChanged.connect(self._apply_filters)
        toolbar_layout.addWidget(QLabel("Slave ID:"))
        toolbar_layout.addWidget(self.slave_id_edit)
        
        self.function_combo = QComboBox()
        self.function_combo.addItems(["Alle", "1", "2", "3", "4", "5", "6", "15", "16"])
        self.function_combo.currentTextChanged.connect(self._apply_filters)
        toolbar_layout.addWidget(QLabel("Function:"))
        toolbar_layout.addWidget(self.function_combo)
        
        layout.addLayout(toolbar_layout)
        
        # Main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left: Table
        table_widget = QWidget()
        table_layout = QVBoxLayout(table_widget)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Tid", "Retning", "Slave ID", "Function", "Adresseområde", "Resultat", "Responstid"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.itemSelectionChanged.connect(self._on_selection_changed)
        table_layout.addWidget(self.table)
        
        splitter.addWidget(table_widget)
        
        # Right: Details panel
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_label = QLabel("Detaljer:")
        details_label.setStyleSheet("font-weight: bold;")
        details_layout.addWidget(details_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumWidth(400)
        details_layout.addWidget(self.details_text)
        
        splitter.addWidget(details_widget)
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        
        layout.addWidget(splitter)
        
        # Tabs for Statistics and Diagnostics
        tabs = QTabWidget()
        
        # Statistics tab
        stats_widget = QWidget()
        stats_layout = QVBoxLayout(stats_widget)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        stats_layout.addWidget(self.stats_text)
        
        tabs.addTab(stats_widget, "Statistics")
        
        # Diagnostics tab
        diagnostics_widget = QWidget()
        diagnostics_layout = QVBoxLayout(diagnostics_widget)
        
        self.diagnostics_text = QTextEdit()
        self.diagnostics_text.setReadOnly(True)
        diagnostics_layout.addWidget(self.diagnostics_text)
        
        tabs.addTab(diagnostics_widget, "Diagnostics")
        
        layout.addWidget(tabs)
        
        # Buttons
        buttons = QHBoxLayout()
        buttons.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons.addWidget(close_btn)
        
        layout.addLayout(buttons)
    
    def _refresh_data(self):
        """Refresh data from trace store"""
        if not self.trace_store:
            return
        
        self._update_table()
        self._update_statistics()
        self._update_diagnostics()
    
    def _update_table(self):
        """Update table with trace entries"""
        if not self.trace_store:
            return
        
        # Get filter parameters
        direction_filter = None
        if self.direction_combo.currentText() == "TX":
            direction_filter = TraceDirection.TX
        elif self.direction_combo.currentText() == "RX":
            direction_filter = TraceDirection.RX
        
        slave_id_filter = None
        if self.slave_id_edit.text().strip():
            try:
                slave_id_filter = int(self.slave_id_edit.text().strip())
            except ValueError:
                pass
        
        function_filter = None
        if self.function_combo.currentText() != "Alle":
            try:
                function_filter = int(self.function_combo.currentText())
            except ValueError:
                pass
        
        # Get entries
        entries = self.trace_store.get_entries(
            direction=direction_filter,
            slave_id=slave_id_filter,
            function_code=function_filter,
            errors_only=self.errors_only_check.isChecked()
        )
        
        # Update table
        self.table.setRowCount(0)
        
        for entry in entries:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Time
            time_str = entry.timestamp.strftime("%H:%M:%S.%f")[:-3]
            time_item = QTableWidgetItem(time_str)
            time_item.setFlags(time_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 0, time_item)
            
            # Direction
            direction_item = QTableWidgetItem(entry.direction.value)
            direction_item.setFlags(direction_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if entry.direction == TraceDirection.TX:
                direction_item.setForeground(Qt.GlobalColor.blue)
            else:
                direction_item.setForeground(Qt.GlobalColor.green)
            self.table.setItem(row, 1, direction_item)
            
            # Slave ID
            slave_id_str = str(entry.slave_id) if entry.slave_id is not None else "N/A"
            slave_item = QTableWidgetItem(slave_id_str)
            slave_item.setFlags(slave_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, slave_item)
            
            # Function
            func_str = entry.get_function_name()
            func_item = QTableWidgetItem(func_str)
            func_item.setFlags(func_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, func_item)
            
            # Address range
            addr_str = entry.get_address_range_str()
            addr_item = QTableWidgetItem(addr_str)
            addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, addr_item)
            
            # Status
            status_str = entry.status.value
            if entry.error_message:
                status_str += f": {entry.error_message[:30]}"
            status_item = QTableWidgetItem(status_str)
            status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            if entry.status != TraceStatus.OK:
                status_item.setForeground(Qt.GlobalColor.red)
            self.table.setItem(row, 5, status_item)
            
            # Response time
            resp_str = f"{entry.response_time_ms:.2f} ms" if entry.response_time_ms else "N/A"
            resp_item = QTableWidgetItem(resp_str)
            resp_item.setFlags(resp_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 6, resp_item)
            
            # Store entry reference
            for col in range(7):
                item = self.table.item(row, col)
                if item:
                    item.setData(Qt.ItemDataRole.UserRole, entry)
        
        # Auto-resize columns
        self.table.resizeColumnsToContents()
    
    def _on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            self.details_text.clear()
            return
        
        row = selected_rows[0].row()
        entry_item = self.table.item(row, 0)
        if not entry_item:
            return
        
        entry = entry_item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(entry, TraceEntry):
            return
        
        # Build details text
        details = []
        details.append(f"Timestamp: {entry.timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
        details.append(f"Direction: {entry.direction.value}")
        details.append(f"Session ID: {entry.session_id or 'N/A'}")
        details.append(f"Connection: {entry.connection_name or 'N/A'}")
        details.append(f"Slave ID: {entry.slave_id or 'N/A'}")
        details.append(f"Function: {entry.get_function_name()} ({entry.function_code})")
        details.append(f"Start Address: {entry.start_address or 'N/A'}")
        details.append(f"Quantity: {entry.quantity or 'N/A'}")
        details.append(f"Address Range: {entry.get_address_range_str()}")
        details.append(f"Status: {entry.status.value}")
        
        if entry.error_message:
            details.append(f"Error: {entry.error_message}")
        
        if entry.exception_code:
            details.append(f"Exception Code: {entry.exception_code}")
        
        if entry.response_time_ms:
            details.append(f"Response Time: {entry.response_time_ms:.2f} ms")
        
        if entry.decoded_info:
            details.append(f"\nDecoded Info:")
            details.append(entry.decoded_info)
        
        if entry.raw_hex_string:
            details.append(f"\nRaw Hex:")
            details.append(entry.raw_hex_string)
        
        self.details_text.setPlainText("\n".join(details))
    
    def _apply_filters(self):
        """Apply filters to table"""
        self._update_table()
    
    def _update_statistics(self):
        """Update statistics tab"""
        if not self.trace_store:
            self.stats_text.setPlainText("No trace store available")
            return
        
        stats = self.trace_store.get_statistics()
        
        stats_text = []
        stats_text.append("=== Trace Statistics ===\n")
        stats_text.append(f"Total Entries: {stats['total_entries']}")
        stats_text.append(f"TX Count: {stats['tx_count']}")
        stats_text.append(f"RX Count: {stats['rx_count']}")
        stats_text.append(f"OK Count: {stats['ok_count']}")
        stats_text.append(f"Error Count: {stats['error_count']}")
        stats_text.append(f"Timeout Count: {stats['timeout_count']}")
        stats_text.append(f"CRC Error Count: {stats['crc_error_count']}")
        stats_text.append(f"Exception Count: {stats['exception_count']}")
        stats_text.append(f"Average Response Time: {stats['avg_response_time_ms']:.2f} ms")
        
        if stats['timeouts_per_slave']:
            stats_text.append("\n=== Timeouts per Slave ===")
            for slave_id, count in sorted(stats['timeouts_per_slave'].items()):
                stats_text.append(f"Slave {slave_id}: {count} timeouts")
        
        if stats['crc_errors_per_connection']:
            stats_text.append("\n=== CRC Errors per Connection ===")
            for conn_name, count in sorted(stats['crc_errors_per_connection'].items()):
                stats_text.append(f"{conn_name}: {count} CRC errors")
        
        if stats['exceptions_per_slave']:
            stats_text.append("\n=== Exceptions per Slave ===")
            for slave_id, count in sorted(stats['exceptions_per_slave'].items()):
                stats_text.append(f"Slave {slave_id}: {count} exceptions")
        
        self.stats_text.setPlainText("\n".join(stats_text))
    
    def _update_diagnostics(self):
        """Update diagnostics tab"""
        if not self.diagnostics_engine:
            self.diagnostics_text.setPlainText("No diagnostics engine available")
            return
        
        findings = self.diagnostics_engine.analyze()
        
        if not findings:
            self.diagnostics_text.setPlainText("No problems found. Everything looks good!")
            return
        
        diagnostics_text = []
        diagnostics_text.append(f"=== Diagnostic Findings ({len(findings)} total) ===\n")
        
        # Group by severity
        errors = [f for f in findings if f.severity == "Error"]
        warnings = [f for f in findings if f.severity == "Warning"]
        infos = [f for f in findings if f.severity == "Info"]
        
        if errors:
            diagnostics_text.append("=== ERRORS ===")
            for finding in errors:
                diagnostics_text.append(f"\n[{finding.category}] {finding.message}")
                if finding.details:
                    diagnostics_text.append(f"  {finding.details}")
        
        if warnings:
            diagnostics_text.append("\n=== WARNINGS ===")
            for finding in warnings:
                diagnostics_text.append(f"\n[{finding.category}] {finding.message}")
                if finding.details:
                    diagnostics_text.append(f"  {finding.details}")
        
        if infos:
            diagnostics_text.append("\n=== INFO ===")
            for finding in infos:
                diagnostics_text.append(f"\n[{finding.category}] {finding.message}")
                if finding.details:
                    diagnostics_text.append(f"  {finding.details}")
        
        self.diagnostics_text.setPlainText("\n".join(diagnostics_text))
    
    def _clear_data(self):
        """Clear trace store data"""
        if not self.trace_store:
            return
        
        reply = QMessageBox.question(
            self,
            "Clear Trace Data",
            "Er du sikker på at du vil rydde al trace data?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.trace_store.clear()
            self._refresh_data()
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

