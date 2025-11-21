"""Dialog for editing device templates"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QLabel, QSpinBox, QTextEdit, QComboBox, QGroupBox,
    QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt
from typing import Optional
from src.models.device_template import DeviceTemplate
from src.models.tag_definition import TagDefinition, AddressType
from src.ui.tag_dialog import TagDialog
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateEditDialog(QDialog):
    """Dialog for creating/editing device templates"""
    
    def __init__(self, parent=None, template: Optional[DeviceTemplate] = None):
        """Initialize template edit dialog"""
        super().__init__(parent)
        self.setWindowTitle("Edit Template" if template else "New Template")
        self.setMinimumSize(700, 600)
        self.template = template
        
        self._setup_ui()
        self._apply_dark_theme()
        
        if template:
            self._load_template(template)
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Basic info group
        basic_group = QGroupBox("Basic Information")
        form = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Grundfos MAGNA3")
        form.addRow("Navn:", self.name_edit)
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItems(["Pump", "VFD", "VAV", "CTS", "Ventilation", "Other"])
        form.addRow("Kategori:", self.category_combo)
        
        self.manufacturer_edit = QLineEdit()
        self.manufacturer_edit.setPlaceholderText("e.g., Grundfos")
        form.addRow("Producent:", self.manufacturer_edit)
        
        self.model_edit = QLineEdit()
        self.model_edit.setPlaceholderText("e.g., MAGNA3")
        form.addRow("Model:", self.model_edit)
        
        self.version_edit = QLineEdit()
        self.version_edit.setPlaceholderText("e.g., 1.0")
        form.addRow("Version:", self.version_edit)
        
        self.default_slave_id_spin = QSpinBox()
        self.default_slave_id_spin.setRange(1, 247)
        self.default_slave_id_spin.setSpecialValueText("None")
        form.addRow("Default Slave ID:", self.default_slave_id_spin)
        
        self.note_edit = QTextEdit()
        self.note_edit.setMaximumHeight(80)
        self.note_edit.setPlaceholderText("Noter om denne template...")
        form.addRow("Note:", self.note_edit)
        
        basic_group.setLayout(form)
        layout.addWidget(basic_group)
        
        # Tags group
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout()
        
        self.tags_list = QListWidget()
        self.tags_list.setAlternatingRowColors(True)
        tags_layout.addWidget(self.tags_list)
        
        tags_buttons = QHBoxLayout()
        
        add_tag_btn = QPushButton("Add Tag")
        add_tag_btn.clicked.connect(self._add_tag)
        tags_buttons.addWidget(add_tag_btn)
        
        edit_tag_btn = QPushButton("Edit")
        edit_tag_btn.clicked.connect(self._edit_tag)
        tags_buttons.addWidget(edit_tag_btn)
        
        delete_tag_btn = QPushButton("Delete")
        delete_tag_btn.clicked.connect(self._delete_tag)
        tags_buttons.addWidget(delete_tag_btn)
        
        tags_buttons.addStretch()
        tags_layout.addLayout(tags_buttons)
        
        tags_group.setLayout(tags_layout)
        layout.addWidget(tags_group)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _load_template(self, template: DeviceTemplate):
        """Load template data into form"""
        self.name_edit.setText(template.name)
        if template.category:
            index = self.category_combo.findText(template.category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setCurrentText(template.category)
        self.manufacturer_edit.setText(template.manufacturer or "")
        self.model_edit.setText(template.model or "")
        self.version_edit.setText(template.version or "")
        if template.default_slave_id:
            self.default_slave_id_spin.setValue(template.default_slave_id)
        self.note_edit.setPlainText(template.note or "")
        
        # Load tags
        for tag in template.tags:
            self._add_tag_to_list(tag)
    
    def _add_tag(self):
        """Add a new tag"""
        # Try to determine address type from existing tags or default to HOLDING_REGISTER
        address_type = AddressType.HOLDING_REGISTER
        if self.tags_list.count() > 0:
            first_item = self.tags_list.item(0)
            if first_item:
                tag = first_item.data(Qt.ItemDataRole.UserRole)
                if isinstance(tag, TagDefinition):
                    address_type = tag.address_type
        
        tag_dialog = TagDialog(self, address_type=address_type)
        if tag_dialog.exec():
            tag = tag_dialog.get_tag()
            self._add_tag_to_list(tag)
    
    def _edit_tag(self):
        """Edit selected tag"""
        current_item = self.tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ingen tag valgt", "Vælg en tag at redigere.")
            return
        
        tag = current_item.data(Qt.ItemDataRole.UserRole)
        if not isinstance(tag, TagDefinition):
            return
        
        tag_dialog = TagDialog(self, tag=tag)
        if tag_dialog.exec():
            updated_tag = tag_dialog.get_tag()
            current_item.setData(Qt.ItemDataRole.UserRole, updated_tag)
            current_item.setText(
                f"{updated_tag.name} - Addr: {updated_tag.address}, Type: {updated_tag.data_type.value}"
            )
    
    def _delete_tag(self):
        """Delete selected tag"""
        current_item = self.tags_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Ingen tag valgt", "Vælg en tag at slette.")
            return
        
        row = self.tags_list.row(current_item)
        self.tags_list.takeItem(row)
    
    def _add_tag_to_list(self, tag: TagDefinition):
        """Add tag to list widget"""
        item_text = f"{tag.name} - Addr: {tag.address}, Type: {tag.data_type.value}"
        item = QListWidgetItem(item_text)
        item.setData(Qt.ItemDataRole.UserRole, tag)
        self.tags_list.addItem(item)
    
    def _validate_and_accept(self):
        """Validate and accept dialog"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validering", "Template navn er påkrævet.")
            return
        
        self.accept()
    
    def get_template(self) -> Optional[DeviceTemplate]:
        """Get template from form"""
        if not self.name_edit.text().strip():
            return None
        
        # Collect tags
        tags = []
        for i in range(self.tags_list.count()):
            item = self.tags_list.item(i)
            tag = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(tag, TagDefinition):
                tags.append(tag)
        
        return DeviceTemplate(
            name=self.name_edit.text().strip(),
            tags=tags,
            category=self.category_combo.currentText() or None,
            manufacturer=self.manufacturer_edit.text().strip() or None,
            model=self.model_edit.text().strip() or None,
            version=self.version_edit.text().strip() or None,
            default_slave_id=self.default_slave_id_spin.value() if self.default_slave_id_spin.value() > 0 else None,
            note=self.note_edit.toPlainText().strip() or None
        )
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

