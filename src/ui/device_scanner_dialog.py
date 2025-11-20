"""Device Scanner Dialog with tabs for RTU and TCP scanning"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QSpinBox, QGroupBox, QFormLayout, QProgressBar,
    QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QSplitter, QTabWidget, QWidget, QLineEdit, QMenu,
    QFileDialog
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QMarginsF
from PyQt6.QtGui import QAction, QTextDocument, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter
from typing import Optional, Callable
import serial.tools.list_ports
from src.application.rtu_scanner import RtuScanner, DeviceInfo
from src.application.tcp_scanner import TcpScanner, TcpDeviceInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class RtuScannerThread(QThread):
    """Thread for running RTU scanner to avoid blocking UI"""
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
            logger.error(f"RTU scanner thread error: {e}")
            self.finished.emit([])
    
    def stop(self):
        """Stop scanner"""
        self.scanner.stop()


class TcpScannerThread(QThread):
    """Thread for running TCP scanner to avoid blocking UI"""
    progress = pyqtSignal(int, int, str)  # current, total, status
    device_found = pyqtSignal(object)  # TcpDeviceInfo
    finished = pyqtSignal(list)  # list of TcpDeviceInfo
    
    def __init__(self, scanner: TcpScanner, ip_range: str, ports: list[int], start_id: int, end_id: int):
        super().__init__()
        self.scanner = scanner
        self.ip_range = ip_range
        self.ports = ports
        self.start_id = start_id
        self.end_id = end_id
        self.scanner.set_progress_callback(self._on_progress)
        self.scanner.set_result_callback(self._on_device_found)
    
    def _on_progress(self, current: int, total: int, status: str):
        """Forward progress to signal"""
        self.progress.emit(current, total, status)
    
    def _on_device_found(self, device_info: TcpDeviceInfo):
        """Forward device found to signal"""
        self.device_found.emit(device_info)
    
    def run(self):
        """Run scanner"""
        try:
            devices = self.scanner.scan(self.ip_range, self.ports, self.start_id, self.end_id)
            self.finished.emit(devices)
        except Exception as e:
            logger.error(f"TCP scanner thread error: {e}")
            self.finished.emit([])
    
    def stop(self):
        """Stop scanner"""
        self.scanner.stop()


class RtuScannerTab(QWidget):
    """RTU Scanner tab"""
    
    def __init__(self, parent=None, import_connection_callback: Optional[Callable] = None, import_session_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.scanner: Optional[RtuScanner] = None
        self.scanner_thread: Optional[RtuScannerThread] = None
        self.found_devices: list[DeviceInfo] = []
        self.import_connection_callback = import_connection_callback
        self.import_session_callback = import_session_callback
        self._setup_ui()
    
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
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        
        # Details text
        details_group = QGroupBox("Device Details")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        # Save as PDF button
        print_btn = QPushButton("Save as PDF")
        print_btn.clicked.connect(self._print_device_info)
        details_layout.addWidget(self.details_text)
        details_layout.addWidget(print_btn)
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
        
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Connect table selection
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Populate COM ports
        self._populate_com_ports()
    
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
            self.scanner_thread = RtuScannerThread(self.scanner, start_id, end_id)
            self.scanner_thread.progress.connect(self._on_progress)
            self.scanner_thread.device_found.connect(self._on_device_found)
            self.scanner_thread.finished.connect(self._on_scan_finished)
            self.scanner_thread.start()
            
            # Update UI
            self.scan_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Scanning...")
            
        except Exception as e:
            logger.error(f"Error starting RTU scan: {e}")
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
    
    def _print_device_info(self):
        """Save device info as PDF"""
        text = self.details_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "No Selection", "Please select a device from the table.")
            return
        
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Device Info as PDF",
            "device_info.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Create printer for PDF
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            margins = QMarginsF(15, 15, 15, 15)  # left, top, right, bottom in millimeters
            printer.setPageMargins(margins, QPageLayout.Unit.Millimeter)
            
            # Create document
            document = QTextDocument()
            
            # Format text with HTML for better appearance
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; font-size: 10pt; }}
                    h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 5px; }}
                    pre {{ background-color: #f5f5f5; padding: 10px; border-left: 3px solid #007acc; 
                          white-space: pre-wrap; font-family: 'Courier New', monospace; }}
                </style>
            </head>
            <body>
                <h1>Device Information</h1>
                <pre>{text}</pre>
            </body>
            </html>
            """
            
            document.setHtml(html_content)
            document.print(printer)
            
            QMessageBox.information(
                self, 
                "PDF Saved", 
                f"Device information has been saved as PDF:\n{file_path}"
            )
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save PDF:\n{str(e)}"
            )
    
    def _show_context_menu(self, position):
        """Show context menu for table items"""
        item = self.results_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        device_id_item = self.results_table.item(row, 0)
        
        if not device_id_item:
            return
        
        menu = QMenu(self)
        
        import_connection_action = QAction("Import Connection", self)
        import_connection_action.triggered.connect(lambda: self._import_connection(row))
        menu.addAction(import_connection_action)
        
        import_session_action = QAction("Import Session", self)
        import_session_action.triggered.connect(lambda: self._import_session(row))
        menu.addAction(import_session_action)
        
        menu.exec(self.results_table.viewport().mapToGlobal(position))
    
    def _import_connection(self, row: int):
        """Import connection from selected device"""
        device_id_item = self.results_table.item(row, 0)
        
        if not device_id_item:
            return
        
        device_id = int(device_id_item.text())
        
        # Get port settings from UI
        port = self.port_combo.currentData()
        if not port:
            port = self.port_combo.currentText().strip()
        
        if not port:
            QMessageBox.warning(self, "Import Error", "COM port information not available.")
            return
        
        baudrate = int(self.baudrate_combo.currentText())
        parity = self.parity_combo.currentText()
        stopbits = self.stopbits_spin.value()
        bytesize = self.bytesize_spin.value()
        
        if self.import_connection_callback:
            self.import_connection_callback(port, baudrate, parity, stopbits, bytesize)
        else:
            QMessageBox.warning(self, "Import Error", "Import callback not available. Please use the import function from the main window.")
    
    def _import_session(self, row: int):
        """Import session from selected device"""
        device_id_item = self.results_table.item(row, 0)
        
        if not device_id_item:
            return
        
        device_id = int(device_id_item.text())
        
        # Find device info
        device_info = next(
            (d for d in self.found_devices if d.device_id == device_id),
            None
        )
        
        if not device_info:
            QMessageBox.warning(self, "Import Error", "Device information not found.")
            return
        
        # Get port settings from UI
        port = self.port_combo.currentData()
        if not port:
            port = self.port_combo.currentText().strip()
        
        if not port:
            QMessageBox.warning(self, "Import Error", "COM port information not available.")
            return
        
        baudrate = int(self.baudrate_combo.currentText())
        parity = self.parity_combo.currentText()
        stopbits = self.stopbits_spin.value()
        bytesize = self.bytesize_spin.value()
        
        if self.import_session_callback:
            self.import_session_callback(device_info, port, baudrate, parity, stopbits, bytesize)
        else:
            QMessageBox.warning(self, "Import Error", "Import callback not available. Please use the import function from the main window.")
    
    def stop_scanning(self):
        """Stop scanning if active"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self._stop_scan()


class TcpScannerTab(QWidget):
    """TCP Scanner tab"""
    
    def __init__(self, parent=None, import_connection_callback: Optional[Callable] = None, import_session_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.scanner: Optional[TcpScanner] = None
        self.scanner_thread: Optional[TcpScannerThread] = None
        self.found_devices: list[TcpDeviceInfo] = []
        self.import_connection_callback = import_connection_callback
        self.import_session_callback = import_session_callback
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Settings group
        settings_group = QGroupBox("Scan Settings")
        settings_layout = QFormLayout()
        
        # IP Range
        self.ip_range_edit = QLineEdit()
        self.ip_range_edit.setPlaceholderText("e.g., 192.168.1.1-254 or 192.168.1.0/24")
        self.ip_range_edit.setText("127.0.0.1-254")
        settings_layout.addRow("IP Range:", self.ip_range_edit)
        
        # Ports
        self.ports_edit = QLineEdit()
        self.ports_edit.setPlaceholderText("e.g., 502,5020 or 502")
        self.ports_edit.setText("502")
        settings_layout.addRow("Ports:", self.ports_edit)
        
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
        self.results_table.setColumnCount(7)
        self.results_table.setHorizontalHeaderLabels([
            "IP Address",
            "Port",
            "Device ID",
            "Coils",
            "Discrete Inputs",
            "Holding Registers",
            "Input Registers"
        ])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self._show_context_menu)
        results_layout.addWidget(self.results_table)
        results_group.setLayout(results_layout)
        splitter.addWidget(results_group)
        
        # Details text
        details_group = QGroupBox("Device Details")
        details_layout = QVBoxLayout()
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        
        # Save as PDF button
        print_btn = QPushButton("Save as PDF")
        print_btn.clicked.connect(self._print_device_info)
        details_layout.addWidget(self.details_text)
        details_layout.addWidget(print_btn)
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
        
        button_layout.addWidget(self.scan_btn)
        button_layout.addWidget(self.stop_btn)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Connect table selection
        self.results_table.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _parse_ports(self, ports_str: str) -> list[int]:
        """Parse ports string (e.g., '502,5020' or '502')"""
        try:
            ports = []
            for port_str in ports_str.split(','):
                port_str = port_str.strip()
                if port_str:
                    port = int(port_str)
                    if 1 <= port <= 65535:
                        ports.append(port)
            return ports if ports else [502]
        except ValueError:
            return [502]
    
    def _start_scan(self):
        """Start scanning"""
        ip_range = self.ip_range_edit.text().strip()
        if not ip_range:
            QMessageBox.warning(self, "Error", "Please enter an IP range")
            return
        
        ports = self._parse_ports(self.ports_edit.text().strip())
        if not ports:
            QMessageBox.warning(self, "Error", "Please enter at least one valid port")
            return
        
        start_id = self.start_id_spin.value()
        end_id = self.end_id_spin.value()
        
        if start_id > end_id:
            QMessageBox.warning(self, "Error", "Start Device ID must be <= End Device ID")
            return
        
        try:
            # Clear previous results
            self.found_devices.clear()
            self.results_table.setRowCount(0)
            self.details_text.clear()
            
            # Create scanner with shorter timeout for faster scanning
            self.scanner = TcpScanner(timeout=0.5)
            
            # Create and start thread
            self.scanner_thread = TcpScannerThread(self.scanner, ip_range, ports, start_id, end_id)
            self.scanner_thread.progress.connect(self._on_progress)
            self.scanner_thread.device_found.connect(self._on_device_found)
            self.scanner_thread.finished.connect(self._on_scan_finished)
            self.scanner_thread.start()
            
            # Update UI
            self.scan_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.status_label.setText("Scanning...")
            
        except Exception as e:
            logger.error(f"Error starting TCP scan: {e}")
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
    
    def _on_device_found(self, device_info: TcpDeviceInfo):
        """Handle device found"""
        self.found_devices.append(device_info)
        
        # Add to table
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        self.results_table.setItem(row, 0, QTableWidgetItem(device_info.ip_address))
        self.results_table.setItem(row, 1, QTableWidgetItem(str(device_info.port)))
        self.results_table.setItem(row, 2, QTableWidgetItem(str(device_info.device_id)))
        self.results_table.setItem(row, 3, QTableWidgetItem("Yes" if device_info.has_coils else "No"))
        self.results_table.setItem(row, 4, QTableWidgetItem("Yes" if device_info.has_discrete_inputs else "No"))
        self.results_table.setItem(row, 5, QTableWidgetItem("Yes" if device_info.has_holding_registers else "No"))
        self.results_table.setItem(row, 6, QTableWidgetItem("Yes" if device_info.has_input_registers else "No"))
    
    def _on_scan_finished(self, devices: list[TcpDeviceInfo]):
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
        ip_item = self.results_table.item(row, 0)
        port_item = self.results_table.item(row, 1)
        device_id_item = self.results_table.item(row, 2)
        
        if not ip_item or not port_item or not device_id_item:
            return
        
        ip_address = ip_item.text()
        port = int(port_item.text())
        device_id = int(device_id_item.text())
        
        device_info = next(
            (d for d in self.found_devices 
             if d.ip_address == ip_address and d.port == port and d.device_id == device_id),
            None
        )
        
        if device_info:
            details = f"IP Address: {device_info.ip_address}\n"
            details += f"Port: {device_info.port}\n"
            details += f"Device ID: {device_info.device_id}\n\n"
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
    
    def _print_device_info(self):
        """Save device info as PDF"""
        text = self.details_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "No Selection", "Please select a device from the table.")
            return
        
        # Get file path from user
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Device Info as PDF",
            "device_info.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return  # User cancelled
        
        try:
            # Create printer for PDF
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            margins = QMarginsF(15, 15, 15, 15)  # left, top, right, bottom in millimeters
            printer.setPageMargins(margins, QPageLayout.Unit.Millimeter)
            
            # Create document
            document = QTextDocument()
            
            # Format text with HTML for better appearance
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; font-size: 10pt; }}
                    h1 {{ color: #333; border-bottom: 2px solid #333; padding-bottom: 5px; }}
                    pre {{ background-color: #f5f5f5; padding: 10px; border-left: 3px solid #007acc; 
                          white-space: pre-wrap; font-family: 'Courier New', monospace; }}
                </style>
            </head>
            <body>
                <h1>Device Information</h1>
                <pre>{text}</pre>
            </body>
            </html>
            """
            
            document.setHtml(html_content)
            document.print(printer)
            
            QMessageBox.information(
                self, 
                "PDF Saved", 
                f"Device information has been saved as PDF:\n{file_path}"
            )
        except Exception as e:
            logger.error(f"Error saving PDF: {e}")
            QMessageBox.critical(
                self, 
                "Error", 
                f"Failed to save PDF:\n{str(e)}"
            )
    
    def _show_context_menu(self, position):
        """Show context menu for table items"""
        item = self.results_table.itemAt(position)
        if not item:
            return
        
        row = item.row()
        ip_item = self.results_table.item(row, 0)
        port_item = self.results_table.item(row, 1)
        device_id_item = self.results_table.item(row, 2)
        
        if not ip_item or not port_item or not device_id_item:
            return
        
        menu = QMenu(self)
        
        import_connection_action = QAction("Import Connection", self)
        import_connection_action.triggered.connect(lambda: self._import_connection(row))
        menu.addAction(import_connection_action)
        
        import_session_action = QAction("Import Session", self)
        import_session_action.triggered.connect(lambda: self._import_session(row))
        menu.addAction(import_session_action)
        
        menu.exec(self.results_table.viewport().mapToGlobal(position))
    
    def _import_connection(self, row: int):
        """Import connection from selected device"""
        ip_item = self.results_table.item(row, 0)
        port_item = self.results_table.item(row, 1)
        
        if not ip_item or not port_item:
            return
        
        ip_address = ip_item.text()
        port = int(port_item.text())
        
        if self.import_connection_callback:
            self.import_connection_callback(ip_address, port)
        else:
            QMessageBox.warning(self, "Import Error", "Import callback not available. Please use the import function from the main window.")
    
    def _import_session(self, row: int):
        """Import session from selected device"""
        ip_item = self.results_table.item(row, 0)
        port_item = self.results_table.item(row, 1)
        device_id_item = self.results_table.item(row, 2)
        
        if not ip_item or not port_item or not device_id_item:
            return
        
        ip_address = ip_item.text()
        port = int(port_item.text())
        device_id = int(device_id_item.text())
        
        # Find device info
        device_info = next(
            (d for d in self.found_devices 
             if d.ip_address == ip_address and d.port == port and d.device_id == device_id),
            None
        )
        
        if not device_info:
            QMessageBox.warning(self, "Import Error", "Device information not found.")
            return
        
        if self.import_session_callback:
            self.import_session_callback(device_info)
        else:
            QMessageBox.warning(self, "Import Error", "Import callback not available. Please use the import function from the main window.")
    
    def stop_scanning(self):
        """Stop scanning if active"""
        if self.scanner_thread and self.scanner_thread.isRunning():
            self._stop_scan()


class DeviceScannerDialog(QDialog):
    """Dialog for device scanning with RTU and TCP tabs"""
    
    def __init__(self, parent=None, import_connection_callback: Optional[Callable] = None, import_session_callback: Optional[Callable] = None):
        super().__init__(parent)
        self.setWindowTitle("Device Scanner")
        self.setMinimumSize(900, 700)
        self.import_connection_callback = import_connection_callback
        self.import_session_callback = import_session_callback
        
        self._setup_ui()
        self._apply_dark_theme()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # RTU Scanner tab
        self.rtu_tab = RtuScannerTab(self, self.import_connection_callback, self.import_session_callback)
        self.tab_widget.addTab(self.rtu_tab, "RTU Scanner")
        
        # TCP Scanner tab
        self.tcp_tab = TcpScannerTab(self, self.import_connection_callback, self.import_session_callback)
        self.tab_widget.addTab(self.tcp_tab, "TCP Scanner")
        
        layout.addWidget(self.tab_widget)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.close_btn)
        layout.addLayout(button_layout)
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QTabWidget {
                background-color: #1e1e1e;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #1e1e1e;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 8px 16px;
                border: 1px solid #3e3e42;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                color: #ffffff;
                border-bottom: 2px solid #007acc;
            }
            QTabBar::tab:hover {
                background-color: #37373d;
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
                padding-right: 30px;
                color: #cccccc;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: #2d2d30;
                border-left: 1px solid #3e3e42;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::drop-down:hover {
                background-color: #37373d;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cccccc;
                width: 0px;
                height: 0px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
                selection-background-color: #094771;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px 8px;
                color: #cccccc;
            }
            QLineEdit:hover {
                border-color: #007acc;
            }
            QLineEdit:focus {
                border-color: #007acc;
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
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 2px;
                width: 16px;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                border-top-right-radius: 3px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                border-bottom-right-radius: 3px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #37373d;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background-color: #094771;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #cccccc;
                width: 0px;
                height: 0px;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cccccc;
                width: 0px;
                height: 0px;
            }
            QSpinBox::up-button:hover QSpinBox::up-arrow {
                border-bottom-color: #ffffff;
            }
            QSpinBox::down-button:hover QSpinBox::down-arrow {
                border-top-color: #ffffff;
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
    
    def closeEvent(self, event):
        """Handle dialog close"""
        # Stop any active scans
        self.rtu_tab.stop_scanning()
        self.tcp_tab.stop_scanning()
        event.accept()

