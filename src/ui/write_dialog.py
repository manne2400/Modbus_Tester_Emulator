"""Dialog for writing Modbus values"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QSpinBox, QLineEdit, QPushButton, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt
from src.protocol.function_codes import FunctionCode, FUNCTION_CODE_NAMES, is_write_function
from src.models.tag_definition import AddressType


class WriteDialog(QDialog):
    """Dialog for writing a single value to Modbus"""
    
    # Class variable to store last address per function code
    _last_addresses = {}  # function_code -> last_address
    
    def __init__(self, parent, session_function_code: int, default_address: int = 0):
        """Initialize write dialog"""
        super().__init__(parent)
        self.setWindowTitle("Write Value")
        self.setModal(True)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        form = QFormLayout()
        form.setSpacing(10)
        
        # Function code (only writable function codes)
        self.function_combo = QComboBox()
        write_functions = [
            FunctionCode.WRITE_SINGLE_COIL,
            FunctionCode.WRITE_SINGLE_REGISTER,
            FunctionCode.WRITE_MULTIPLE_COILS,
            FunctionCode.WRITE_MULTIPLE_REGISTERS,
        ]
        
        # Set default based on session function code if it's a write function
        default_index = 0
        for i, fc in enumerate(write_functions):
            self.function_combo.addItem(
                f"{fc.value:02X} - {FUNCTION_CODE_NAMES[fc]}",
                fc.value
            )
            if fc.value == session_function_code and is_write_function(session_function_code):
                default_index = i
        
        self.function_combo.setCurrentIndex(default_index)
        self.function_combo.currentIndexChanged.connect(self._on_function_changed)
        form.addRow("Function Code:", self.function_combo)
        
        # Address - use last address for this function code if available, otherwise use default_address
        self.address_spin = QSpinBox()
        self.address_spin.setRange(0, 65535)
        initial_function_code = self.function_combo.currentData()
        if initial_function_code in self._last_addresses:
            self.address_spin.setValue(self._last_addresses[initial_function_code])
        else:
            self.address_spin.setValue(default_address)
        form.addRow("Address:", self.address_spin)
        
        # Value input (changes based on function code)
        self.value_input = QLineEdit()
        self.value_input.setPlaceholderText("Enter value...")
        form.addRow("Value:", self.value_input)
        
        # Quantity (for multiple write functions)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 2000)
        self.quantity_spin.setValue(1)
        self.quantity_label = QLabel("Quantity:")
        form.addRow(self.quantity_label, self.quantity_spin)
        
        # Update UI based on initial function code
        self._on_function_changed()
        
        layout.addLayout(form)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        write_btn = QPushButton("Write")
        write_btn.setDefault(True)
        write_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(write_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _on_function_changed(self):
        """Update UI based on selected function code"""
        function_code = self.function_combo.currentData()
        
        # Update address to last used address for this function code
        if function_code in self._last_addresses:
            self.address_spin.setValue(self._last_addresses[function_code])
        
        if function_code in [FunctionCode.WRITE_SINGLE_COIL, FunctionCode.WRITE_SINGLE_REGISTER]:
            # Single write - hide quantity
            self.quantity_label.setVisible(False)
            self.quantity_spin.setVisible(False)
            
            if function_code == FunctionCode.WRITE_SINGLE_COIL:
                self.value_input.setPlaceholderText("Enter 0 or 1 (False/True)")
            else:  # WRITE_SINGLE_REGISTER
                self.value_input.setPlaceholderText("Enter value (0-65535)")
        else:
            # Multiple write - show quantity
            self.quantity_label.setVisible(True)
            self.quantity_spin.setVisible(True)
            
            # Set quantity to 2 for function codes 10 and 0F
            if function_code in [FunctionCode.WRITE_MULTIPLE_COILS, FunctionCode.WRITE_MULTIPLE_REGISTERS]:
                self.quantity_spin.setValue(2)
            
            if function_code == FunctionCode.WRITE_MULTIPLE_COILS:
                self.value_input.setPlaceholderText("Enter values separated by comma (e.g. 1,0,1,0)")
            else:  # WRITE_MULTIPLE_REGISTERS
                self.value_input.setPlaceholderText("Enter values separated by comma (e.g. 100,200) or one large value")
        
        # Clear value input when function code changes
        self.value_input.setText("")
    
    def get_write_params(self):
        """Get write parameters"""
        function_code = self.function_combo.currentData()
        address = self.address_spin.value()
        value_text = self.value_input.text().strip()
        quantity = self.quantity_spin.value()
        
        # Parse value(s) based on function code
        if function_code == FunctionCode.WRITE_SINGLE_COIL:
            # Single coil - bool value
            try:
                val = int(value_text)
                if val not in [0, 1]:
                    return None, None, None, "Value must be 0 or 1"
                return function_code, address, bool(val), None
            except ValueError:
                return None, None, None, "Invalid value. Use 0 or 1"
        
        elif function_code == FunctionCode.WRITE_SINGLE_REGISTER:
            # Single register - int value
            try:
                val = int(value_text)
                if val < 0 or val > 65535:
                    return None, None, None, "Value must be between 0 and 65535"
                return function_code, address, val, None
            except ValueError:
                return None, None, None, "Invalid value. Use a number between 0 and 65535"
        
        elif function_code == FunctionCode.WRITE_MULTIPLE_COILS:
            # Multiple coils - list of bool
            try:
                values_str = value_text.split(',')
                if len(values_str) != quantity:
                    return None, None, None, f"Number of values must match quantity ({quantity})"
                values = []
                for v in values_str:
                    val = int(v.strip())
                    if val not in [0, 1]:
                        return None, None, None, "All values must be 0 or 1"
                    values.append(bool(val))
                return function_code, address, values, None
            except ValueError:
                return None, None, None, "Invalid value. Use comma-separated values (0 or 1)"
        
        else:  # WRITE_MULTIPLE_REGISTERS
            # Multiple registers - list of int
            try:
                values_str = value_text.split(',')
                
                # If only one value provided but quantity > 1, try to auto-split large values
                if len(values_str) == 1 and quantity > 1:
                    single_val = int(values_str[0].strip())
                    
                    # Auto-split into registers (Big Endian format)
                    # Convert negative values to unsigned representation
                    if single_val < 0:
                        # For negative values, convert to unsigned 32-bit (or larger)
                        max_bits = 16 * quantity
                        if max_bits > 32:
                            max_bits = 32  # Limit to 32-bit for now
                        unsigned_val = single_val + (1 << max_bits)
                    else:
                        unsigned_val = single_val
                    
                    # Split into 16-bit words (Big Endian - most significant word first)
                    values = []
                    for i in range(quantity):
                        shift = 16 * (quantity - i - 1)
                        word = (unsigned_val >> shift) & 0xFFFF
                        values.append(word)
                    
                    return function_code, address, values, None
                
                # Multiple values provided
                if len(values_str) != quantity:
                    return None, None, None, f"Enter {quantity} values separated by comma (e.g. 100,200) or one large value that will be automatically split into {quantity} registers"
                
                values = []
                for v in values_str:
                    val = int(v.strip())
                    if val < 0 or val > 65535:
                        return None, None, None, "All values must be between 0 and 65535"
                    values.append(val)
                return function_code, address, values, None
            except ValueError as e:
                return None, None, None, f"Invalid value. Use comma-separated numbers (0-65535) or one large value that will be automatically split: {str(e)}"
    
    def accept(self):
        """Validate and accept"""
        function_code, address, value, error = self.get_write_params()
        if error:
            QMessageBox.warning(self, "Invalid Value", error)
            return
        
        # Save the address for this function code
        self._last_addresses[function_code] = address
        
        super().accept()

