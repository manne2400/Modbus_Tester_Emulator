"""RTU Scanner Dialog"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QGroupBox, QFormLayout, QProgressBar,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSplitter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from typing import Optional
import serial.tools.list_ports
from src.application.rtu_scanner import RtuScanner, DeviceInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScannerThread(QThread):
    """Thread for running scanner to avoid blocking UI"""
    progress = pyqtSignal(int, int, str)  # current, total, status
    device_found = pyqtSignal(object)  # DeviceInfo
    finished = pyqtSignal(list)  # list of DeviceInfo
    
    def __init__(self, scanner: RtuScanner, start_id: int, end_id: int):
        super().__init__()
        self.scanner = scanner
        self.start_id = start_id
        self.end_id = end_id
        self.scanner.set_progress_callback(self._on_progress)
        self.scanner.set_result_callback(self._on_device_found)
    
    def _on_progress(self, current: int, total: int, status: str):
        """Forward progress to signal"""
        self.progress.emit(current, total, status)
    
    def _on_device_found(self, device_info: DeviceInfo):
        """Forward device found to signal"""
        self.device_found.emit(device_info)
    
    def run(self):
        """Run scanner"""
        try:
            devices = self.scanner.scan(self.start_id, self.end_id)
            self.finished.emit(devices)
        except Exception as e:
            logger.error(f"Scanner thread error: {e}")
            self.finished.emit([])
    
    def stop(self):
        """Stop scanner"""
        self.scanner.stop()


class RtuScannerDialog(QDialog):
    """Dialog for RTU device scanning"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("RTU Device Scanner")
        self.setMinimumSize(800, 600)
        
        self.scanner: Optional[RtuScanner] = None
        self.scanner_thread: Optional[ScannerThread] = None
        self.found_devices: list[DeviceInfo] = []
        
        self._setup_ui()
        self._apply_dark_theme()
        self._populate_com_ports()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Settings group
        settings_group = QGroupBox("Scan Settings")
        settings_layout = QFormLayout()
        
        # COM port
        self.port_combo = QComboBox()
        self.port_combo.setEditable(True)
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._populate_com_ports)
        port_layout = QHBoxLayout()
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(refresh_btn)
        settings_layout.addRow("COM Port:", port_layout)
        
        # Baudrate
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.baudrate_combo.setCurrentText("9600")
        settings_layout.addRow("Baudrate:", self.baudrate_combo)
        
        # Parity
        self.parity_combo = QComboBox()
        self.parity_combo.addItems(["N", "E", "O"])
        self.parity_combo.setCurrentText("N")
        settings_layout.addRow("Parity:", self.parity_combo)
        
        # Stop bits
        self.stopbits_spin = QSpinBox()
        self.stopbits_spin.setMinimum(1)
        self.stopbits_spin.setMaximum(2)
        self.stopbits_spin.setValue(1)
        settings_layout.addRow("Stop Bits:", self.stopbits_spin)
        
        # Data bits
        self.bytesize_spin = QSpinBox()
        self.bytesize_spin.setMinimum(7)
        self.bytesize_spin.setMaximum(8)
        self.bytesize_spin.setValue(8)
        settings_layout.addRow("Data Bits:", self.bytesize_spin)
        
        # Device ID range
        self.start_id_spin = QSpinBox()
        self.start_id_spin.setMinimum(1)
        self.start_id_spin.setMaximum(247)
        self.start_id_spin.setValue(1)
        settings_layout.addRow("Start Device ID:", self.start_id_spin)
        
        self.end_id_spin = QSpinBox()
        self.end_id_spin.setMinimum(1)
        self.end_id_spin.setMaximum(247)
        self.end_id_spin.setValue(247)
        settings_layout.addRow("End Device ID:", self.end_id_spin)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Ready")
        layout.addWidget(self.status_label)
        
        # Results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Results table
        results_group = QGroupBox("Found Devices")
        results_layout = QVBoxLayout()
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "Device ID",
            "Coils",
            "Discrete Inputs",
            "Holding Registers",
            "Input Registers",
            "Details"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        
        # Details text
        details_group = QGroupBox("Device Details")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)
        details_group.setLayout(details_layout)
        splitter.addWidget(details_group)
        
        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 1)
        layout.addWidget(splitter)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.scan_btn = QPushButton("Start Scan")
        self.scan_btn.clicked.connect(self._start_scan)
        self.stop_btn = QPushButton("Stop Scan")
        self.stop_btn.clicked.connect(self._stop_scan)
        self.stop_btn.setEnabled(False)
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
        
        # Connect table selection
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
                color: #cccccc;
                font-weight: 500;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #cccccc;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px 8px;
                color: #cccccc;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
                selection-background-color: #094771;
            }
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px;
                color: #cccccc;
            }
            QSpinBox:hover {
                border-color: #007acc;
            }
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 6px 16px;
                border-radius: 3px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
            QPushButton:disabled {
                background-color: #3e3e42;
                color: #6e6e6e;
            }
            QTableWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                gridline-color: #3e3e42;
                alternate-background-color: #2d2d30;
                color: #cccccc;
            }
            QTableWidget::item {
                padding: 4px;
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #094771;
                color: white;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #3e3e42;
                font-weight: 600;
                color: #cccccc;
            }
            QTextEdit {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                color: #cccccc;
            }
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                text-align: center;
                color: #cccccc;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 2px;
            }
            QSplitter::handle {
                background-color: #3e3e42;
            }
        """)
    
    def _populate_com_ports(self):
        """Populate COM port list"""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(f"{port.device} - {port.description}", port.device)
    
    def _start_scan(self):
        """Start scanning"""
        port = self.port_combo.currentData()
        if not port:
            port = self.port_combo.currentText().strip()
        
        if not port:
            QMessageBox.warning(self, "Error", "Please select a COM port")
            return
        
        try:
            baudrate = int(self.baudrate_combo.currentText())
            parity = self.parity_combo.currentText()
            stopbits = self.stopbits_spin.value()
            bytesize = self.bytesize_spin.value()
            start_id = self.start_id_spin.value()
            end_id = self.end_id_spin.value()
            
            if start_id > end_id:
                QMessageBox.warning(self, "Error", "Start Device ID must be <= End Device ID")
                return
            
            # Clear previous results
            self.found_devices.clear()
            self.results_table.setRowCount(0)
            self.details_text.clear()
            
            # Create scanner
            self.scanner = RtuScanner(
                port=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=0.5
            )
            
            # Create and start thread
            self.scanner_thread = ScannerThread(self.scanner, start_id, end_id)
            self.scanner_thread.progress.connect(self._on_progress)
            self.scanner_thread.device_found.connect(self._on_device_found)
            self.scanner_thread.finished.connect(self._on_scan_finished)
            self.scanner_thread.start()
            
            # Update UI
            self.scan_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Scanning...")
            
        except Exception as e:
            logger.error(f"Error starting scan: {e}")
            QMessageBox.critical(self, "Error", f"Failed to start scan: {e}")
    
    def _stop_scan(self):
        """Stop scanning"""
        if self.scanner_thread:
            self.scanner_thread.stop()
            self.scanner_thread.wait()
            self.scanner_thread = None
        
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Scan stopped")
    
    def _on_progress(self, current: int, total: int, status: str):
        """Update progress"""
        if total > 0:
            progress = int((current / total) * 100)
            self.progress_bar.setValue(progress)
        self.status_label.setText(status)
    
    def _on_device_found(self, device_info: DeviceInfo):
        """Handle device found"""
        self.found_devices.append(device_info)
        
        # Add to table
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(str(device_info.device_id)))
        self.results_table.setItem(row, 1, QTableWidgetItem("Yes" if device_info.has_coils else "No"))
        self.results_table.setItem(row, 2, QTableWidgetItem("Yes" if device_info.has_discrete_inputs else "No"))
        self.results_table.setItem(row, 3, QTableWidgetItem("Yes" if device_info.has_holding_registers else "No"))
        self.results_table.setItem(row, 4, QTableWidgetItem("Yes" if device_info.has_input_registers else "No"))
        
        # Count addresses
        total_addrs = (len(device_info.coil_addresses) +
                      len(device_info.discrete_input_addresses) +
                      len(device_info.holding_register_addresses) +
                      len(device_info.input_register_addresses))
        self.results_table.setItem(row, 5, QTableWidgetItem(f"{total_addrs} addresses"))
    
    def _on_scan_finished(self, devices: list[DeviceInfo]):
        """Handle scan finished"""
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText(f"Scan complete - Found {len(devices)} device(s)")
        self.progress_bar.setValue(100)
    
    def _on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.results_table.selectedItems()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        device_id_item = self.results_table.item(row, 0)
        if not device_id_item:
            return
        
        device_id = int(device_id_item.text())
        device_info = next((d for d in self.found_devices if d.device_id == device_id), None)
        
        if device_info:
            details = f"Device ID: {device_info.device_id}\n\n"
            details += "Note: Only addresses with active values are shown:\n"
            details += "  • Coils/Discrete Inputs: Only addresses with value = 1 (True)\n"
            details += "  • Registers: Only addresses with value ≠ 0\n"
            details += "  Addresses with value 0 (False) are not included.\n\n"
            
            if device_info.has_coils:
                details += f"Coils: {len(device_info.coil_addresses)} addresses\n"
                if device_info.coil_addresses:
                    details += f"  Addresses: {', '.join(map(str, device_info.coil_addresses[:20]))}"
                    if len(device_info.coil_addresses) > 20:
                        details += f" ... (+{len(device_info.coil_addresses) - 20} more)"
                    details += "\n"
            
            if device_info.has_discrete_inputs:
                details += f"Discrete Inputs: {len(device_info.discrete_input_addresses)} addresses\n"
                if device_info.discrete_input_addresses:
                    details += f"  Addresses: {', '.join(map(str, device_info.discrete_input_addresses[:20]))}"
                    if len(device_info.discrete_input_addresses) > 20:
                        details += f" ... (+{len(device_info.discrete_input_addresses) - 20} more)"
                    details += "\n"
            
            if device_info.has_holding_registers:
                details += f"Holding Registers: {len(device_info.holding_register_addresses)} addresses\n"
                if device_info.holding_register_addresses:
                    details += f"  Addresses: {', '.join(map(str, device_info.holding_register_addresses[:20]))}"
                    if len(device_info.holding_register_addresses) > 20:
                        details += f" ... (+{len(device_info.holding_register_addresses) - 20} more)"
                    details += "\n"
            
            if device_info.has_input_registers:
                details += f"Input Registers: {len(device_info.input_register_addresses)} addresses\n"
                if device_info.input_register_addresses:
                    details += f"  Addresses: {', '.join(map(str, device_info.input_register_addresses[:20]))}"
                    if len(device_info.input_register_addresses) > 20:
                        details += f" ... (+{len(device_info.input_register_addresses) - 20} more)"
                    details += "\n"
            
            self.details_text.setText(details)
    
    def closeEvent(self, event):
        """Handle dialog close"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self._stop_scan()
        event.accept()

