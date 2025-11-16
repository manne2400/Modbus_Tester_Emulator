"""Session tab widget"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QLineEdit
)
from PyQt6.QtCore import Qt
from src.models.session_definition import SessionDefinition, SessionStatus
from src.models.connection_profile import ConnectionProfile
from src.models.poll_result import PollResult
from src.application.session_manager import SessionManager
from src.application.polling_engine import PollingEngine
from src.protocol.function_codes import FunctionCode, FUNCTION_CODE_NAMES
from src.ui.data_table import DataTable
from src.ui.widgets.status_bar import StatusBar
from typing import List


class SessionTab(QWidget):
    """Tab widget for a Modbus session"""
    
    def __init__(
        self,
        session: SessionDefinition,
        connections: List[ConnectionProfile],
        session_manager: SessionManager,
        polling_engine: PollingEngine
    ):
        """Initialize session tab"""
        super().__init__()
        self.session = session
        self.connections = connections
        self.session_manager = session_manager
        self.polling_engine = polling_engine
        
        self._setup_ui()
        self.update_status()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Controls panel - split into two columns
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setSpacing(15)
        
        # Left column - form fields
        left_form = QFormLayout()
        left_form.setSpacing(8)
        
        # Connection dropdown
        self.connection_combo = QComboBox()
        for conn in self.connections:
            self.connection_combo.addItem(conn.name, conn.name)
        index = self.connection_combo.findData(self.session.connection_profile_name)
        if index >= 0:
            self.connection_combo.setCurrentIndex(index)
        self.connection_combo.currentIndexChanged.connect(self._on_connection_changed)
        left_form.addRow("Forbindelse:", self.connection_combo)
        
        # Slave ID
        self.slave_id_spin = QSpinBox()
        self.slave_id_spin.setRange(1, 247)
        self.slave_id_spin.setValue(self.session.slave_id)
        self.slave_id_spin.valueChanged.connect(self._on_slave_id_changed)
        left_form.addRow("Slave ID:", self.slave_id_spin)
        
        # Function code
        self.function_combo = QComboBox()
        for code in FunctionCode:
            self.function_combo.addItem(
                f"{code.value:02X} - {FUNCTION_CODE_NAMES[code]}",
                code.value
            )
        index = self.function_combo.findData(self.session.function_code)
        if index >= 0:
            self.function_combo.setCurrentIndex(index)
        self.function_combo.currentIndexChanged.connect(self._on_function_changed)
        left_form.addRow("Function Code:", self.function_combo)
        
        left_widget = QWidget()
        left_widget.setLayout(left_form)
        controls_layout.addWidget(left_widget)
        
        # Right column - more fields
        right_form = QFormLayout()
        right_form.setSpacing(8)
        
        # Start address
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 65535)
        self.address_spin.setValue(self.session.start_address)
        self.address_spin.valueChanged.connect(self._on_address_changed)
        right_form.addRow("Startadresse:", self.address_spin)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 2000)
        self.quantity_spin.setValue(self.session.quantity)
        self.quantity_spin.valueChanged.connect(self._on_quantity_changed)
        right_form.addRow("Antal:", self.quantity_spin)
        
        # Poll interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 60000)
        self.interval_spin.setValue(self.session.poll_interval_ms)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        right_form.addRow("Poll-interval:", self.interval_spin)
        
        right_widget = QWidget()
        right_widget.setLayout(right_form)
        controls_layout.addWidget(right_widget)
        
        # Add stretch to push button to the right
        controls_layout.addStretch()
        
        # Start/Stop button - large and prominent
        self.start_stop_btn = QPushButton("Start")
        self.start_stop_btn.setMinimumSize(120, 40)
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: 600;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.start_stop_btn.clicked.connect(self._toggle_polling)
        controls_layout.addWidget(self.start_stop_btn)
        
        controls_widget.setMaximumHeight(150)
        layout.addWidget(controls_widget)
        
        # Data table
        self.data_table = DataTable()
        layout.addWidget(self.data_table)
        
        # Status bar
        self.status_bar = StatusBar()
        layout.addWidget(self.status_bar)
    
    def _on_connection_changed(self, index: int):
        """Handle connection change"""
        profile_name = self.connection_combo.currentData()
        if profile_name:
            self.session.connection_profile_name = profile_name
            self.session_manager.add_session(self.session)
    
    def _on_slave_id_changed(self, value: int):
        """Handle slave ID change"""
        self.session.slave_id = value
    
    def _on_function_changed(self, index: int):
        """Handle function code change"""
        function_code = self.function_combo.currentData()
        if function_code:
            self.session.function_code = function_code
    
    def _on_address_changed(self, value: int):
        """Handle address change"""
        self.session.start_address = value
    
    def _on_quantity_changed(self, value: int):
        """Handle quantity change"""
        self.session.quantity = value
    
    def _on_interval_changed(self, value: int):
        """Handle interval change"""
        self.session.poll_interval_ms = value
        # Reset poll timer
        self.polling_engine.reset_poll_timer(self.session.name)
    
    def _toggle_polling(self):
        """Toggle polling on/off"""
        if self.session.status == SessionStatus.RUNNING:
            self.session_manager.stop_session(self.session.name)
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """)
        else:
            # Ensure connection is established
            if not self.session_manager.connect(self.session.connection_profile_name):
                self.status_bar.update_status("Kunne ikke forbinde", error=True)
                return
            self.session_manager.start_session(self.session.name)
            self.start_stop_btn.setText("Stop")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
                QPushButton:pressed {
                    background-color: #8b0000;
                }
            """)
            # Reset poll timer to poll immediately
            self.polling_engine.reset_poll_timer(self.session.name)
        
        self.update_status()
    
    def update_status(self):
        """Update status display"""
        if self.session.status == SessionStatus.RUNNING:
            self.status_bar.update_status("Kører...", error=False)
            self.start_stop_btn.setText("Stop")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #d32f2f;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #b71c1c;
                }
                QPushButton:pressed {
                    background-color: #8b0000;
                }
            """)
        elif self.session.status == SessionStatus.ERROR:
            self.status_bar.update_status("Fejl", error=True)
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """)
        else:
            self.status_bar.update_status("Stoppet", error=False)
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0078d4;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: 600;
                    font-size: 11pt;
                }
                QPushButton:hover {
                    background-color: #106ebe;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
            """)
    
    def update_data(self, result: PollResult):
        """Update data table with poll result"""
        self.data_table.update_data(result)
        if result.status.value == "OK":
            self.status_bar.update_status(
                f"OK - {result.response_time_ms:.1f}ms" if result.response_time_ms else "OK",
                error=False
            )
        else:
            self.status_bar.update_status(
                result.error_message or result.status.value,
                error=True
            )
    
    def show_error(self, error_message: str):
        """Show error message"""
        self.status_bar.update_status(error_message, error=True)
