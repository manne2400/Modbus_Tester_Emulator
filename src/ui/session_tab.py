"""Session tab widget"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QLineEdit,
    QListWidget, QListWidgetItem, QMessageBox, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from src.models.session_definition import SessionDefinition, SessionStatus
from src.models.connection_profile import ConnectionProfile
from src.models.poll_result import PollResult
from src.application.session_manager import SessionManager
from src.application.polling_engine import PollingEngine
from src.protocol.function_codes import FunctionCode, FUNCTION_CODE_NAMES
from src.ui.data_table import DataTable
from src.ui.widgets.status_bar import StatusBar
from src.ui.tag_dialog import TagDialog
from src.ui.write_dialog import WriteDialog
from src.models.tag_definition import TagDefinition, AddressType
from src.storage.template_library import TemplateLibrary
from src.models.device_template import DeviceTemplate
from src.protocol.function_codes import is_write_function
from src.ui.styles.theme import Theme
from typing import List, Optional


class SessionTab(QWidget):
    """Tab widget for a Modbus session"""
    
    # Signal emitted when connection changes
    connection_changed = pyqtSignal(str)  # session_name
    
    def __init__(
        self,
        session: SessionDefinition,
        connections: List[ConnectionProfile],
        session_manager: SessionManager,
        polling_engine: PollingEngine,
        config_manager=None,
        template_library: Optional[TemplateLibrary] = None
    ):
        """Initialize session tab"""
        super().__init__()
        self.session = session
        self.connections = connections
        self.session_manager = session_manager
        self.polling_engine = polling_engine
        self.config_manager = config_manager
        self.template_library = template_library or TemplateLibrary()
        
        self._setup_ui()
        self.update_status()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_STANDARD)
        layout.setContentsMargins(Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD)
        
        # Controls panel - split into two columns
        controls_widget = QWidget()
        controls_layout = QHBoxLayout(controls_widget)
        controls_layout.setSpacing(Theme.SPACING_STANDARD)
        
        # Left column - form fields
        left_form = QFormLayout()
        left_form.setSpacing(Theme.SPACING_FORM)
        
        # Connection dropdown
        self.connection_combo = QComboBox()
        for conn in self.connections:
            self.connection_combo.addItem(conn.name, conn.name)
        index = self.connection_combo.findData(self.session.connection_profile_name)
        if index >= 0:
            self.connection_combo.setCurrentIndex(index)
        self.connection_combo.currentIndexChanged.connect(self._on_connection_changed)
        left_form.addRow("Connection:", self.connection_combo)
        
        # Slave ID
        self.slave_id_spin = QSpinBox()
        self.slave_id_spin.setRange(1, 247)
        self.slave_id_spin.setValue(self.session.slave_id)
        self.slave_id_spin.valueChanged.connect(self._on_slave_id_changed)
        left_form.addRow("Slave ID:", self.slave_id_spin)
        
        # Function code (only read functions - write is done via "Skriv værdi" button)
        self.function_combo = QComboBox()
        from src.protocol.function_codes import is_read_function
        for code in FunctionCode:
            # Only show read function codes (01-04)
            if is_read_function(code.value):
                self.function_combo.addItem(
                    f"{code.value:02X} - {FUNCTION_CODE_NAMES[code]}",
                    code.value
                )
        index = self.function_combo.findData(self.session.function_code)
        if index >= 0:
            self.function_combo.setCurrentIndex(index)
        else:
            # If current function code is not a read function, default to Read Holding Registers
            default_index = self.function_combo.findData(FunctionCode.READ_HOLDING_REGISTERS)
            if default_index >= 0:
                self.function_combo.setCurrentIndex(default_index)
                self.session.function_code = FunctionCode.READ_HOLDING_REGISTERS
        self.function_combo.currentIndexChanged.connect(self._on_function_changed)
        left_form.addRow("Function Code:", self.function_combo)
        
        left_widget = QWidget()
        left_widget.setLayout(left_form)
        controls_layout.addWidget(left_widget)
        
        # Right column - more fields
        right_form = QFormLayout()
        right_form.setSpacing(Theme.SPACING_FORM)
        
        # Start address
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 65535)
        self.address_spin.setValue(self.session.start_address)
        self.address_spin.valueChanged.connect(self._on_address_changed)
        right_form.addRow("Start Address:", self.address_spin)
        
        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 2000)
        self.quantity_spin.setValue(self.session.quantity)
        self.quantity_spin.valueChanged.connect(self._on_quantity_changed)
        right_form.addRow("Quantity:", self.quantity_spin)
        
        # Poll interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(100, 60000)
        self.interval_spin.setValue(self.session.poll_interval_ms)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.valueChanged.connect(self._on_interval_changed)
        right_form.addRow("Poll Interval:", self.interval_spin)
        
        right_widget = QWidget()
        right_widget.setLayout(right_form)
        controls_layout.addWidget(right_widget)
        
        # Add stretch to push button to the right
        controls_layout.addStretch()
        
        # Start/Stop button - large and prominent
        self.start_stop_btn = QPushButton("Start")
        self.start_stop_btn.setMinimumSize(120, 40)
        # Apply base styling with larger size for start/stop button
        self.start_stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #0e639c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 3px;
                font-weight: 600;
                font-size: 11pt;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
            QPushButton[status="running"] {
                background-color: #d32f2f;
            }
            QPushButton[status="running"]:hover {
                background-color: #f44336;
            }
            QPushButton[status="running"]:pressed {
                background-color: #b71c1c;
            }
        """)
        self.start_stop_btn.clicked.connect(self._toggle_polling)
        controls_layout.addWidget(self.start_stop_btn)
        
        controls_widget.setMaximumHeight(150)
        layout.addWidget(controls_widget)
        
        # Tags and Write buttons
        tags_layout = QHBoxLayout()
        tags_layout.addStretch()
        self.write_btn = QPushButton("Write Value...")
        self.write_btn.clicked.connect(self._write_value)
        tags_layout.addWidget(self.write_btn)
        self.tags_btn = QPushButton("Manage Tags...")
        self.tags_btn.clicked.connect(self._manage_tags)
        tags_layout.addWidget(self.tags_btn)
        layout.addLayout(tags_layout)
        
        # Data table
        self.data_table = DataTable()
        layout.addWidget(self.data_table)
        
        # Status bar - wrap in horizontal layout to prevent expansion
        status_layout = QHBoxLayout()
        status_layout.setContentsMargins(0, 0, 0, 0)
        status_layout.setSpacing(0)
        self.status_bar = StatusBar()
        # Add status bar without stretch factor
        status_layout.addWidget(self.status_bar, 0)  # 0 = no stretch
        status_layout.addStretch()  # Push status bar to left, fill remaining space
        layout.addLayout(status_layout)
    
    def _on_connection_changed(self, index: int):
        """Handle connection change"""
        profile_name = self.connection_combo.currentData()
        if profile_name:
            self.session.connection_profile_name = profile_name
            self.session_manager.add_session(self.session)
            # Emit signal to notify main window
            self.connection_changed.emit(self.session.name)
    
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
    
    def _manage_tags(self):
        """Open tag management dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Manage Tags")
        dialog.setModal(True)
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # List of tags
        tags_list = QListWidget()
        tags_list.setAlternatingRowColors(True)
        
        # Populate list
        for tag in self.session.tags:
            item_text = f"{tag.name} - Addr: {tag.address}, Type: {tag.data_type.value}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, tag)
            tags_list.addItem(item)
        
        layout.addWidget(tags_list)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        add_btn = QPushButton("Add Tag")
        add_btn.clicked.connect(lambda: self._add_tag(dialog, tags_list))
        buttons_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(lambda: self._edit_tag(dialog, tags_list))
        buttons_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(lambda: self._delete_tag(tags_list))
        buttons_layout.addWidget(delete_btn)
        
        buttons_layout.addStretch()
        
        # Template buttons
        load_template_btn = QPushButton("Load from Template...")
        load_template_btn.clicked.connect(lambda: self._load_from_template(dialog, tags_list))
        buttons_layout.addWidget(load_template_btn)
        
        save_template_btn = QPushButton("Save as Template...")
        save_template_btn.clicked.connect(lambda: self._save_as_template(dialog, tags_list))
        buttons_layout.addWidget(save_template_btn)
        
        buttons_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def _add_tag(self, parent_dialog, tags_list):
        """Add a new tag"""
        # Determine address type from function code
        # Convert write function codes to read function codes for address type mapping
        from src.protocol.function_codes import get_read_function_for_write, is_write_function
        function_code_for_mapping = self.session.function_code
        if is_write_function(self.session.function_code):
            read_fc = get_read_function_for_write(self.session.function_code)
            if read_fc:
                function_code_for_mapping = read_fc
        
        address_type_map = {
            FunctionCode.READ_COILS: AddressType.COIL,
            FunctionCode.READ_DISCRETE_INPUTS: AddressType.DISCRETE_INPUT,
            FunctionCode.READ_HOLDING_REGISTERS: AddressType.HOLDING_REGISTER,
            FunctionCode.READ_INPUT_REGISTERS: AddressType.INPUT_REGISTER,
        }
        address_type = address_type_map.get(
            FunctionCode(function_code_for_mapping),
            AddressType.HOLDING_REGISTER
        )
        
        tag_dialog = TagDialog(parent_dialog, address_type=address_type)
        if tag_dialog.exec():
            tag = tag_dialog.get_tag()
            self.session.tags.append(tag)
            self.session_manager.add_session(self.session)
            # Save to config if available
            if self.config_manager:
                self.config_manager.save_sessions([self.session])
            
            # Refresh list
            item_text = f"{tag.name} - Addr: {tag.address}, Type: {tag.data_type.value}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, tag)
            tags_list.addItem(item)
    
    def _edit_tag(self, parent_dialog, tags_list):
        """Edit selected tag"""
        current_item = tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(parent_dialog, "Ingen tag valgt", "Vælg en tag at redigere.")
            return
        
        tag = current_item.data(Qt.ItemDataRole.UserRole)
        tag_dialog = TagDialog(parent_dialog, tag=tag)
        if tag_dialog.exec():
            new_tag = tag_dialog.get_tag()
            # Update tag in session
            index = self.session.tags.index(tag)
            self.session.tags[index] = new_tag
            self.session_manager.add_session(self.session)
            # Save to config if available
            if self.config_manager:
                self.config_manager.save_sessions([self.session])
            
            # Update list item
            item_text = f"{new_tag.name} - Adr: {new_tag.address}, Type: {new_tag.data_type.value}"
            current_item.setText(item_text)
            current_item.setData(Qt.ItemDataRole.UserRole, new_tag)
    
    def _delete_tag(self, tags_list):
        """Delete selected tag"""
        current_item = tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No tag selected", "Please select a tag to delete.")
            return
        
        reply = QMessageBox.question(
            self,
            "Delete tag",
            "Are you sure you want to delete this tag?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            tag = current_item.data(Qt.ItemDataRole.UserRole)
            self.session.tags.remove(tag)
            self.session_manager.add_session(self.session)
            # Save to config if available
            if self.config_manager:
                self.config_manager.save_sessions([self.session])
            tags_list.takeItem(tags_list.row(current_item))
    
    def _load_from_template(self, parent_dialog, tags_list):
        """Load tags from template"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QLabel
        
        # Show template selection dialog
        select_dialog = QDialog(parent_dialog)
        select_dialog.setWindowTitle("Load from Template")
        select_dialog.setModal(True)
        select_dialog.setMinimumSize(500, 400)
        
        layout = QVBoxLayout(select_dialog)
        
        layout.addWidget(QLabel("Vælg template:"))
        
        template_list = QListWidget()
        templates = self.template_library.load_all_templates()
        for template in templates:
            item_text = f"{template.get_display_name()} ({template.get_tag_count()} tags)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, template)
            template_list.addItem(item)
        
        layout.addWidget(template_list)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        load_btn = QPushButton("Load Selected Tags")
        load_btn.clicked.connect(select_dialog.accept)
        buttons_layout.addWidget(load_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(select_dialog.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
        
        if select_dialog.exec():
            current_item = template_list.currentItem()
            if not current_item:
                QMessageBox.warning(parent_dialog, "Ingen template valgt", "Vælg en template.")
                return
            
            template = current_item.data(Qt.ItemDataRole.UserRole)
            if not isinstance(template, DeviceTemplate):
                return
            
            # Determine address type from session function code
            # Convert write function codes to read function codes for address type mapping
            from src.protocol.function_codes import get_read_function_for_write, is_write_function
            function_code_for_mapping = self.session.function_code
            if is_write_function(self.session.function_code):
                read_fc = get_read_function_for_write(self.session.function_code)
                if read_fc:
                    function_code_for_mapping = read_fc
            
            address_type_map = {
                FunctionCode.READ_COILS: AddressType.COIL,
                FunctionCode.READ_DISCRETE_INPUTS: AddressType.DISCRETE_INPUT,
                FunctionCode.READ_HOLDING_REGISTERS: AddressType.HOLDING_REGISTER,
                FunctionCode.READ_INPUT_REGISTERS: AddressType.INPUT_REGISTER,
            }
            session_address_type = address_type_map.get(
                FunctionCode(function_code_for_mapping),
                AddressType.HOLDING_REGISTER
            )
            
            # Filter tags that match session address type
            matching_tags = [tag for tag in template.tags if tag.address_type == session_address_type]
            
            if not matching_tags:
                QMessageBox.warning(
                    parent_dialog,
                    "Ingen matchende tags",
                    f"Template '{template.name}' har ingen tags af typen {session_address_type.value}."
                )
                return
            
            # Add tags to session
            for tag in matching_tags:
                # Check if tag with same address already exists
                if not any(t.address == tag.address and t.address_type == tag.address_type for t in self.session.tags):
                    self.session.tags.append(tag)
                    # Add to list
                    item_text = f"{tag.name} - Addr: {tag.address}, Type: {tag.data_type.value}"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, tag)
                    tags_list.addItem(item)
            
            self.session_manager.add_session(self.session)
            if self.config_manager:
                self.config_manager.save_sessions([self.session])
            
            QMessageBox.information(
                parent_dialog,
                "Tags loaded",
                f"{len(matching_tags)} tags loaded fra template '{template.name}'."
            )
    
    def _save_as_template(self, parent_dialog, tags_list):
        """Save current tags as template"""
        if not self.session.tags:
            QMessageBox.warning(parent_dialog, "Ingen tags", "Der er ingen tags at gemme som template.")
            return
        
        from src.ui.template_edit_dialog import TemplateEditDialog
        
        # Create template from current tags
        template = DeviceTemplate(
            name=f"{self.session.name}_Template",
            tags=self.session.tags.copy()
        )
        
        dialog = TemplateEditDialog(parent_dialog, template)
        if dialog.exec():
            template = dialog.get_template()
            if template:
                if self.template_library.save_template(template):
                    QMessageBox.information(
                        parent_dialog,
                        "Success",
                        f"Template '{template.name}' gemt med {len(template.tags)} tags."
                    )
                else:
                    QMessageBox.warning(parent_dialog, "Error", "Kunne ikke gemme template.")
    
    def _toggle_polling(self):
        """Toggle polling on/off"""
        if self.session.status == SessionStatus.RUNNING:
            self.session_manager.stop_session(self.session.name)
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setProperty("status", "")
        else:
            # Ensure connection is established
            if not self.session_manager.connect(self.session.connection_profile_name):
                self.status_bar.update_status("Kunne ikke forbinde", error=True)
                return
            self.session_manager.start_session(self.session.name)
            self.start_stop_btn.setText("Stop")
            self.start_stop_btn.setProperty("status", "running")
            # Reset poll timer to poll immediately
            self.polling_engine.reset_poll_timer(self.session.name)
        
        # Refresh style to apply property changes
        self.start_stop_btn.style().unpolish(self.start_stop_btn)
        self.start_stop_btn.style().polish(self.start_stop_btn)
        self.update_status()
    
    def update_status(self):
        """Update status display"""
        if self.session.status == SessionStatus.RUNNING:
            self.status_bar.update_status("Kører...", error=False)
            self.start_stop_btn.setText("Stop")
            self.start_stop_btn.setProperty("status", "running")
        elif self.session.status == SessionStatus.ERROR:
            self.status_bar.update_status("Error", error=True)
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setProperty("status", "")
        else:
            self.status_bar.update_status("Stoppet", error=False)
            self.start_stop_btn.setText("Start")
            self.start_stop_btn.setProperty("status", "")
            # Refresh style to apply property changes
            self.start_stop_btn.style().unpolish(self.start_stop_btn)
            self.start_stop_btn.style().polish(self.start_stop_btn)
    
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
    
    def _write_value(self):
        """Open write dialog and write value"""
        # Ensure connection is established
        if not self.session_manager.connect(self.session.connection_profile_name):
            QMessageBox.warning(self, "No Connection", "Could not connect to device.")
            return
        
        # Get protocol
        protocol = self.session_manager.get_protocol(self.session.connection_profile_name)
        if not protocol:
            QMessageBox.warning(self, "Error", "Could not access protocol.")
            return
        
        # Open write dialog
        default_address = self.session.start_address
        dialog = WriteDialog(self, self.session.function_code, default_address)
        
        if dialog.exec():
            function_code, address, value, error = dialog.get_write_params()
            if error:
                QMessageBox.warning(self, "Fejl", error)
                return
            
            # Execute write
            try:
                success, error_msg = protocol.execute_write(
                    function_code,
                    self.session.slave_id,
                    address,
                    value
                )
                
                if success:
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Value written to address {address}."
                    )
                    # Reset poll timer to refresh data immediately
                    self.polling_engine.reset_poll_timer(self.session.name)
                else:
                    QMessageBox.warning(
                        self,
                        "Write Error",
                        error_msg or "Could not write value."
                    )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Unexpected error during write: {str(e)}"
                )
