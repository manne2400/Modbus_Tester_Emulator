"""Dialog for configuring and starting Modbus simulators"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton, QFormLayout,
    QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt
import serial.tools.list_ports
from src.ui.styles.theme import Theme


class SimulatorDialog(QDialog):
    """Dialog for configuring Modbus simulators"""
    
    def __init__(self, parent=None, simulator_manager=None):
        """Initialize simulator dialog"""
        super().__init__(parent)
        self.setWindowTitle("Modbus Simulator")
        self.setModal(True)
        self.setMinimumSize(500, 400)
        self.simulator_manager = simulator_manager
        
        self._setup_ui()
        self._apply_dark_theme()
        self._update_status()
        self._update_button_states()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Tabs for TCP and RTU
        tabs = QTabWidget()
        
        # TCP tab
        tcp_tab = self._create_tcp_tab()
        tabs.addTab(tcp_tab, "Modbus TCP")
        
        # RTU tab
        rtu_tab = self._create_rtu_tab()
        tabs.addTab(rtu_tab, "Modbus RTU")
        
        layout.addWidget(tabs)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("padding: 10px; font-weight: 500;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _create_tcp_tab(self) -> QWidget:
        """Create TCP simulator tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("TCP Simulator Settings")
        form = QFormLayout()
        
        self.tcp_host = QLineEdit("127.0.0.1")
        form.addRow("Host/IP:", self.tcp_host)
        
        self.tcp_port = QSpinBox()
        self.tcp_port.setRange(1, 65535)
        self.tcp_port.setValue(5020)
        form.addRow("Port:", self.tcp_port)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.tcp_start_btn = QPushButton("Start TCP Simulator")
        self.tcp_start_btn.clicked.connect(self._start_tcp)
        button_layout.addWidget(self.tcp_start_btn)
        
        self.tcp_stop_btn = QPushButton("Stop TCP Simulator")
        self.tcp_stop_btn.clicked.connect(self._stop_tcp)
        self.tcp_stop_btn.setEnabled(False)
        button_layout.addWidget(self.tcp_stop_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _create_rtu_tab(self) -> QWidget:
        """Create RTU simulator tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        group = QGroupBox("RTU Simulator Settings")
        form = QFormLayout()
        
        # Port selection
        self.rtu_port = QComboBox()
        self.rtu_port.setEditable(True)
        # Populate with available COM ports
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.rtu_port.addItems(ports if ports else ["COM1", "COM3", "COM10"])
        if "COM10" in ports:
            self.rtu_port.setCurrentText("COM10")
        form.addRow("COM Port:", self.rtu_port)
        
        # Baudrate
        self.rtu_baudrate = QComboBox()
        self.rtu_baudrate.setEditable(True)
        self.rtu_baudrate.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.rtu_baudrate.setCurrentText("9600")
        form.addRow("Baudrate:", self.rtu_baudrate)
        
        # Parity
        self.rtu_parity = QComboBox()
        self.rtu_parity.addItems(["N (None)", "E (Even)", "O (Odd)"])
        form.addRow("Parity:", self.rtu_parity)
        
        # Stop bits
        self.rtu_stopbits = QComboBox()
        self.rtu_stopbits.addItems(["1", "2"])
        form.addRow("Stop Bits:", self.rtu_stopbits)
        
        # Data bits
        self.rtu_bytesize = QComboBox()
        self.rtu_bytesize.addItems(["7", "8"])
        self.rtu_bytesize.setCurrentText("8")
        form.addRow("Data Bits:", self.rtu_bytesize)
        
        group.setLayout(form)
        layout.addWidget(group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.rtu_start_btn = QPushButton("Start RTU Simulator")
        self.rtu_start_btn.clicked.connect(self._start_rtu)
        button_layout.addWidget(self.rtu_start_btn)
        
        self.rtu_stop_btn = QPushButton("Stop RTU Simulator")
        self.rtu_stop_btn.clicked.connect(self._stop_rtu)
        self.rtu_stop_btn.setEnabled(False)
        button_layout.addWidget(self.rtu_stop_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        return widget
    
    def _start_tcp(self):
        """Start TCP simulator"""
        if not self.simulator_manager:
            return
        
        host = self.tcp_host.text().strip()
        port = self.tcp_port.value()
        
        if self.simulator_manager.start_tcp_simulator(host, port):
            self._update_button_states()
            self._update_status()
        else:
            QMessageBox.warning(self, "Error", "TCP simulator is already running or could not be started.")
    
    def _stop_tcp(self):
        """Stop TCP simulator"""
        if not self.simulator_manager:
            return
        
        self.simulator_manager.stop_tcp_simulator()
        self._update_button_states()
        self._update_status()
    
    def _start_rtu(self):
        """Start RTU simulator"""
        if not self.simulator_manager:
            return
        
        port = self.rtu_port.currentText().strip()
        try:
            baudrate = int(self.rtu_baudrate.currentText())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid baudrate.")
            return
        
        parity_map = {"N (None)": "N", "E (Even)": "E", "O (Odd)": "O"}
        parity = parity_map.get(self.rtu_parity.currentText(), "N")
        
        try:
            stopbits = int(self.rtu_stopbits.currentText())
            bytesize = int(self.rtu_bytesize.currentText())
        except ValueError:
            QMessageBox.warning(self, "Error", "Invalid stop bits or data bits.")
            return
        
        if self.simulator_manager.start_rtu_simulator(port, baudrate, parity, stopbits, bytesize):
            self._update_button_states()
            self._update_status()
        else:
            QMessageBox.warning(
                self, 
                "Error", 
                f"RTU simulator is already running or could not be started on {port}.\n"
                f"Check that the port is available and not used by another program."
            )
    
    def _stop_rtu(self):
        """Stop RTU simulator"""
        if not self.simulator_manager:
            return
        
        self.simulator_manager.stop_rtu_simulator()
        self._update_button_states()
        self._update_status()
    
    def _update_status(self):
        """Update status label"""
        if not self.simulator_manager:
            self.status_label.setText("Simulator manager not available")
            self.status_label.setStyleSheet("padding: 10px; color: #666;")
            return
        
        tcp_status = "Running" if self.simulator_manager.is_tcp_running() else "Stopped"
        rtu_status = "Running" if self.simulator_manager.is_rtu_running() else "Stopped"
        
        status_text = f"TCP: {tcp_status} | RTU: {rtu_status}"
        self.status_label.setText(status_text)
        
        if self.simulator_manager.is_tcp_running() or self.simulator_manager.is_rtu_running():
            self.status_label.setStyleSheet("padding: 10px; color: #4caf50; font-weight: 500;")
        else:
            self.status_label.setStyleSheet("padding: 10px; color: #cccccc;")
    
    def _update_button_states(self):
        """Update button states based on simulator status"""
        if not self.simulator_manager:
            return
        
        tcp_running = self.simulator_manager.is_tcp_running()
        rtu_running = self.simulator_manager.is_rtu_running()
        
        self.tcp_start_btn.setEnabled(not tcp_running)
        self.tcp_stop_btn.setEnabled(tcp_running)
        
        self.rtu_start_btn.setEnabled(not rtu_running)
        self.rtu_stop_btn.setEnabled(rtu_running)
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

