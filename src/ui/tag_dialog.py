"""Dialog for creating/editing tag definitions"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QDialogButtonBox, QGroupBox
)
from PyQt6.QtCore import Qt
from src.models.tag_definition import TagDefinition, AddressType, DataType, ByteOrder


class TagDialog(QDialog):
    """Dialog for creating/editing tag definitions"""
    
    def __init__(self, parent=None, tag: TagDefinition = None, address_type: AddressType = None):
        """Initialize tag dialog"""
        super().__init__(parent)
        self.setWindowTitle("Edit Tag" if tag else "New Tag")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.tag = tag
        
        self._setup_ui()
        
        if tag:
            self._load_tag(tag)
        elif address_type:
            self.address_type_combo.setCurrentText(address_type.value)
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Basic info group
        basic_group = QGroupBox("Basic Information")
        form = QFormLayout()
        
        # Address type
        self.address_type_combo = QComboBox()
        self.address_type_combo.addItems([at.value for at in AddressType])
        form.addRow("Address Type:", self.address_type_combo)
        
        # Address
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 65535)
        form.addRow("Address:", self.address_spin)
        
        # Name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g. Temperature, Pressure, etc.")
        form.addRow("Name:", self.name_edit)
        
        basic_group.setLayout(form)
        layout.addWidget(basic_group)
        
        # Data type group
        data_group = QGroupBox("Data Type and Byte Order")
        data_form = QFormLayout()
        
        # Data type
        self.data_type_combo = QComboBox()
        data_type_items = [
            "UINT16 - 16-bit unsigned integer (1 register)",
            "INT16 - 16-bit signed integer (1 register)",
            "UINT32 - 32-bit unsigned integer (2 registers)",
            "INT32 - 32-bit signed integer/DINT (2 registers)",
            "FLOAT32 - 32-bit float (2 registers)",
            "BOOL - Boolean (1 bit)"
        ]
        self.data_type_combo.addItems(data_type_items)
        self.data_type_combo.setCurrentText("UINT16 - 16-bit unsigned integer (1 register)")
        data_form.addRow("Data Type:", self.data_type_combo)
        
        # Byte order
        self.byte_order_combo = QComboBox()
        self.byte_order_combo.addItems([bo.value for bo in ByteOrder])
        self.byte_order_combo.setCurrentText(ByteOrder.BIG_ENDIAN.value)
        data_form.addRow("Byte Order:", self.byte_order_combo)
        
        data_group.setLayout(data_form)
        layout.addWidget(data_group)
        
        # Scaling group
        scaling_group = QGroupBox("Scaling (optional)")
        scaling_form = QFormLayout()
        
        # Scale factor
        self.scale_factor_spin = QDoubleSpinBox()
        self.scale_factor_spin.setRange(-1000000.0, 1000000.0)
        self.scale_factor_spin.setValue(1.0)
        self.scale_factor_spin.setDecimals(6)
        scaling_form.addRow("Scale Factor:", self.scale_factor_spin)
        
        # Scale offset
        self.scale_offset_spin = QDoubleSpinBox()
        self.scale_offset_spin.setRange(-1000000.0, 1000000.0)
        self.scale_offset_spin.setValue(0.0)
        self.scale_offset_spin.setDecimals(6)
        scaling_form.addRow("Offset:", self.scale_offset_spin)
        
        # Unit
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("e.g. °C, bar, %, etc.")
        scaling_form.addRow("Unit:", self.unit_edit)
        
        scaling_group.setLayout(scaling_form)
        layout.addWidget(scaling_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _load_tag(self, tag: TagDefinition):
        """Load tag data into form"""
        self.address_type_combo.setCurrentText(tag.address_type.value)
        self.address_spin.setValue(tag.address)
        self.name_edit.setText(tag.name)
        
        # Set data type
        data_type_map = {
            DataType.UINT16: "UINT16 - 16-bit unsigned integer (1 register)",
            DataType.INT16: "INT16 - 16-bit signed integer (1 register)",
            DataType.UINT32: "UINT32 - 32-bit unsigned integer (2 registers)",
            DataType.INT32: "INT32 - 32-bit signed integer/DINT (2 registers)",
            DataType.FLOAT32: "FLOAT32 - 32-bit float (2 registers)",
            DataType.BOOL: "BOOL - Boolean (1 bit)"
        }
        self.data_type_combo.setCurrentText(data_type_map.get(tag.data_type, data_type_map[DataType.UINT16]))
        
        self.byte_order_combo.setCurrentText(tag.byte_order.value)
        self.scale_factor_spin.setValue(tag.scale_factor)
        self.scale_offset_spin.setValue(tag.scale_offset)
        self.unit_edit.setText(tag.unit)
    
    def get_tag(self) -> TagDefinition:
        """Get tag definition from form"""
        # Map data type string to enum
        data_type_str = self.data_type_combo.currentText()
        if "UINT16" in data_type_str:
            data_type = DataType.UINT16
        elif "INT16" in data_type_str:
            data_type = DataType.INT16
        elif "UINT32" in data_type_str:
            data_type = DataType.UINT32
        elif "INT32" in data_type_str or "DINT" in data_type_str:
            data_type = DataType.INT32
        elif "FLOAT32" in data_type_str:
            data_type = DataType.FLOAT32
        elif "BOOL" in data_type_str:
            data_type = DataType.BOOL
        else:
            data_type = DataType.UINT16
        
        return TagDefinition(
            address_type=AddressType(self.address_type_combo.currentText()),
            address=self.address_spin.value(),
            name=self.name_edit.text().strip() or f"Address {self.address_spin.value()}",
            data_type=data_type,
            byte_order=ByteOrder(self.byte_order_combo.currentText()),
            scale_factor=self.scale_factor_spin.value(),
            scale_offset=self.scale_offset_spin.value(),
            unit=self.unit_edit.text().strip()
        )

