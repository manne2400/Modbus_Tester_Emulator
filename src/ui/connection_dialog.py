"""Connection dialog for creating/editing connection profiles"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QSpinBox, QComboBox, QPushButton, QDialogButtonBox,
    QFormLayout
)
from PyQt6.QtCore import Qt
import serial.tools.list_ports
from src.models.connection_profile import ConnectionProfile, ConnectionType


class ConnectionDialog(QDialog):
    """Dialog for connection profile configuration"""
    
    def __init__(self, parent=None, profile: ConnectionProfile = None):
        """Initialize dialog"""
        super().__init__(parent)
        self.setWindowTitle("Forbindelsesprofil" if not profile else "Rediger forbindelsesprofil")
        self.setModal(True)
        self.profile = profile
        
        self._setup_ui()
        
        if profile:
            self._load_profile(profile)
    
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
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Store tab reference
        self.tabs = tabs
    
    def _create_tcp_tab(self) -> QWidget:
        """Create TCP configuration tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Store as instance variables
        self.tcp_name = QLineEdit()
        self.tcp_name.setPlaceholderText("fx. PLC1")
        layout.addRow("Navn:", self.tcp_name)
        
        self.tcp_host = QLineEdit()
        self.tcp_host.setPlaceholderText("192.168.1.100")
        layout.addRow("Host/IP:", self.tcp_host)
        
        self.tcp_port = QSpinBox()
        self.tcp_port.setRange(1, 65535)
        self.tcp_port.setValue(502)
        layout.addRow("Port:", self.tcp_port)
        
        self.tcp_timeout = QSpinBox()
        self.tcp_timeout.setRange(1, 60)
        self.tcp_timeout.setValue(3)
        self.tcp_timeout.setSuffix(" sek")
        layout.addRow("Timeout:", self.tcp_timeout)
        
        self.tcp_retries = QSpinBox()
        self.tcp_retries.setRange(0, 10)
        self.tcp_retries.setValue(3)
        layout.addRow("Forsøg:", self.tcp_retries)
        
        return widget
    
    def _create_rtu_tab(self) -> QWidget:
        """Create RTU configuration tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Store as instance variables
        self.rtu_name = QLineEdit()
        self.rtu_name.setPlaceholderText("fx. RS485 Bus")
        layout.addRow("Navn:", self.rtu_name)
        
        # COM port selection
        self.rtu_port = QComboBox()
        self._refresh_com_ports()
        refresh_btn = QPushButton("Opdater")
        refresh_btn.clicked.connect(self._refresh_com_ports)
        port_layout = QHBoxLayout()
        port_layout.addWidget(self.rtu_port)
        port_layout.addWidget(refresh_btn)
        port_widget = QWidget()
        port_widget.setLayout(port_layout)
        layout.addRow("Port:", port_widget)
        
        self.rtu_baudrate = QComboBox()
        self.rtu_baudrate.addItems(["9600", "19200", "38400", "57600", "115200"])
        self.rtu_baudrate.setCurrentText("9600")
        layout.addRow("Baudrate:", self.rtu_baudrate)
        
        self.rtu_parity = QComboBox()
        self.rtu_parity.addItems(["N", "E", "O"])
        layout.addRow("Parity:", self.rtu_parity)
        
        self.rtu_stopbits = QSpinBox()
        self.rtu_stopbits.setRange(1, 2)
        self.rtu_stopbits.setValue(1)
        layout.addRow("Stop bits:", self.rtu_stopbits)
        
        self.rtu_bytesize = QSpinBox()
        self.rtu_bytesize.setRange(7, 8)
        self.rtu_bytesize.setValue(8)
        layout.addRow("Data bits:", self.rtu_bytesize)
        
        self.rtu_timeout = QSpinBox()
        self.rtu_timeout.setRange(1, 60)
        self.rtu_timeout.setValue(3)
        self.rtu_timeout.setSuffix(" sek")
        layout.addRow("Timeout:", self.rtu_timeout)
        
        self.rtu_retries = QSpinBox()
        self.rtu_retries.setRange(0, 10)
        self.rtu_retries.setValue(3)
        layout.addRow("Forsøg:", self.rtu_retries)
        
        return widget
    
    def _refresh_com_ports(self):
        """Refresh COM port list"""
        self.rtu_port.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.rtu_port.addItem(port.device, port.device)
    
    def _load_profile(self, profile: ConnectionProfile):
        """Load profile into dialog"""
        if profile.connection_type == ConnectionType.TCP:
            self.tabs.setCurrentIndex(0)
            self.tcp_name.setText(profile.name)
            self.tcp_host.setText(profile.host or "")
            self.tcp_port.setValue(profile.port or 502)
            self.tcp_timeout.setValue(int(profile.timeout))
            self.tcp_retries.setValue(profile.retries)
        else:
            self.tabs.setCurrentIndex(1)
            self.rtu_name.setText(profile.name)
            port_index = self.rtu_port.findData(profile.port_name)
            if port_index >= 0:
                self.rtu_port.setCurrentIndex(port_index)
            baud_index = self.rtu_baudrate.findText(str(profile.baudrate or 9600))
            if baud_index >= 0:
                self.rtu_baudrate.setCurrentIndex(baud_index)
            parity_index = self.rtu_parity.findText(profile.parity or "N")
            if parity_index >= 0:
                self.rtu_parity.setCurrentIndex(parity_index)
            self.rtu_stopbits.setValue(profile.stopbits or 1)
            self.rtu_bytesize.setValue(profile.bytesize or 8)
            self.rtu_timeout.setValue(int(profile.timeout))
            self.rtu_retries.setValue(profile.retries)
    
    def get_connection_profile(self) -> ConnectionProfile:
        """Get connection profile from dialog"""
        if self.tabs.currentIndex() == 0:  # TCP
            if not hasattr(self, 'tcp_name') or self.tcp_name is None:
                # Fallback if TCP tab wasn't created
                return ConnectionProfile(
                    name="TCP Connection",
                    connection_type=ConnectionType.TCP,
                    host="192.168.1.100",
                    port=502,
                    timeout=3.0,
                    retries=3
                )
            return ConnectionProfile(
                name=self.tcp_name.text() or "TCP Connection",
                connection_type=ConnectionType.TCP,
                host=self.tcp_host.text() or None,
                port=self.tcp_port.value(),
                timeout=float(self.tcp_timeout.value()),
                retries=self.tcp_retries.value()
            )
        else:  # RTU
            if not hasattr(self, 'rtu_name') or self.rtu_name is None:
                # Fallback if RTU tab wasn't created
                return ConnectionProfile(
                    name="RTU Connection",
                    connection_type=ConnectionType.RTU,
                    port_name=None,
                    baudrate=9600,
                    parity="N",
                    stopbits=1,
                    bytesize=8,
                    timeout=3.0,
                    retries=3
                )
            port_data = self.rtu_port.currentData()
            return ConnectionProfile(
                name=self.rtu_name.text() or "RTU Connection",
                connection_type=ConnectionType.RTU,
                port_name=port_data if port_data else None,
                baudrate=int(self.rtu_baudrate.currentText()),
                parity=self.rtu_parity.currentText(),
                stopbits=self.rtu_stopbits.value(),
                bytesize=self.rtu_bytesize.value(),
                timeout=float(self.rtu_timeout.value()),
                retries=self.rtu_retries.value()
            )
