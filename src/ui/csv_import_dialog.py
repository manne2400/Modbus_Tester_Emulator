"""Dialog for CSV/Excel import with column mapping"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QLabel, QPushButton, QMessageBox, QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from pathlib import Path
from typing import Dict, List, Optional
from src.models.tag_definition import AddressType
from src.utils.csv_import import detect_csv_columns, import_tags_from_csv, CSVImportError
from src.utils.excel_import import detect_excel_columns, import_tags_from_excel, get_excel_sheet_names, ExcelImportError
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CSVImportDialog(QDialog):
    """Dialog for mapping CSV/Excel columns to tag fields"""
    
    # Field definitions
    REQUIRED_FIELDS = ["address"]
    OPTIONAL_FIELDS = [
        "name", "data_type", "byte_order", "scale_factor",
        "scale_offset", "unit", "address_type"
    ]
    ALL_FIELDS = REQUIRED_FIELDS + OPTIONAL_FIELDS
    
    FIELD_LABELS = {
        "address": "Address (required)",
        "name": "Name",
        "data_type": "Data Type",
        "byte_order": "Byte Order",
        "scale_factor": "Scale Factor",
        "scale_offset": "Scale Offset",
        "unit": "Unit",
        "address_type": "Address Type"
    }
    
    def __init__(self, parent=None, csv_file: Optional[Path] = None, address_type: Optional[AddressType] = None):
        """Initialize CSV/Excel import dialog"""
        super().__init__(parent)
        self.setWindowTitle("Import CSV/Excel")
        self.setMinimumSize(600, 500)
        
        self.import_file = csv_file
        self.address_type = address_type
        self.file_columns: List[str] = []
        self.column_mapping: Dict[str, str] = {}  # field -> file_column
        self.imported_tags = None
        self.is_excel = False
        self.sheet_name: Optional[str] = None
        
        self._setup_ui()
        self._apply_dark_theme()
        
        if csv_file:
            self._load_file_columns()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # File info
        file_group = QGroupBox("File")
        file_layout = QVBoxLayout()
        
        if self.import_file:
            file_label = QLabel(f"File: {self.import_file.name}")
            file_layout.addWidget(file_label)
            
            # Sheet selector for Excel
            if self.is_excel:
                sheet_layout = QHBoxLayout()
                sheet_layout.addWidget(QLabel("Sheet:"))
                self.sheet_combo = QComboBox()
                self.sheet_combo.currentTextChanged.connect(self._on_sheet_changed)
                sheet_layout.addWidget(self.sheet_combo)
                file_layout.addLayout(sheet_layout)
        else:
            file_label = QLabel("No file selected")
            file_layout.addWidget(file_label)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Column mapping
        mapping_group = QGroupBox("Column Mapping")
        mapping_layout = QFormLayout()
        
        self.field_combos: Dict[str, QComboBox] = {}
        
        for field in self.ALL_FIELDS:
            combo = QComboBox()
            combo.addItem("(None)", None)
            combo.setEditable(False)
            self.field_combos[field] = combo
            mapping_layout.addRow(self.FIELD_LABELS.get(field, field) + ":", combo)
        
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Preview
        preview_group = QGroupBox("Preview (first 5 rows)")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self._preview_import)
        buttons_layout.addWidget(preview_btn)
        
        import_btn = QPushButton("Import")
        import_btn.clicked.connect(self._do_import)
        buttons_layout.addWidget(import_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def _load_file_columns(self):
        """Load CSV/Excel columns and populate combos"""
        if not self.import_file:
            return
        
        # Detect file type
        self.is_excel = self.import_file.suffix.lower() in ['.xlsx', '.xls']
        
        if self.is_excel:
            # Load sheet names
            sheet_names = get_excel_sheet_names(self.import_file)
            if hasattr(self, 'sheet_combo'):
                self.sheet_combo.clear()
                for sheet in sheet_names:
                    self.sheet_combo.addItem(sheet)
                if sheet_names:
                    self.sheet_name = sheet_names[0]
            
            self.file_columns = detect_excel_columns(self.import_file, self.sheet_name)
        else:
            self.file_columns = detect_csv_columns(self.import_file)
        
        # Populate all combos
        for field, combo in self.field_combos.items():
            combo.clear()
            combo.addItem("(None)", None)
            for col in self.file_columns:
                combo.addItem(col, col)
        
        # Try to auto-detect common column names
        self._auto_detect_mapping()
    
    def _on_sheet_changed(self, sheet_name: str):
        """Handle sheet selection change"""
        self.sheet_name = sheet_name
        self._load_file_columns()
    
    def _auto_detect_mapping(self):
        """Auto-detect column mappings based on common names"""
        column_lower = {col.lower(): col for col in self.file_columns}
        
        # Common mappings
        auto_mappings = {
            "address": ["address", "addr", "adresse", "regaddr", "register"],
            "name": ["name", "navn", "tag", "label", "description", "beskrivelse"],
            "data_type": ["datatype", "type", "datatype", "data type"],
            "byte_order": ["byteorder", "byte order", "endian", "byteorder"],
            "scale_factor": ["scalefactor", "scale factor", "scale", "factor"],
            "scale_offset": ["scaleoffset", "scale offset", "offset"],
            "unit": ["unit", "enhed", "units"],
            "address_type": ["addresstype", "address type", "register type"]
        }
        
        for field, possible_names in auto_mappings.items():
            if field in self.field_combos:
                combo = self.field_combos[field]
                for name in possible_names:
                    if name in column_lower:
                        csv_col = column_lower[name]
                        index = combo.findData(csv_col)
                        if index >= 0:
                            combo.setCurrentIndex(index)
                            break
    
    def _preview_import(self):
        """Preview import without actually importing"""
        if not self._validate_mapping():
            return
        
        if not self.import_file:
            QMessageBox.warning(self, "No file", "No file selected.")
            return
        
        try:
            if self.is_excel:
                tags = import_tags_from_excel(
                    self.import_file,
                    self._get_column_mapping(),
                    self.address_type,
                    self.sheet_name
                )
            else:
                tags = import_tags_from_csv(
                    self.import_file,
                    self._get_column_mapping(),
                    self.address_type
                )
            
            # Show preview
            preview_lines = []
            preview_lines.append(f"Will import {len(tags)} tags:\n")
            for i, tag in enumerate(tags[:5], 1):
                preview_lines.append(
                    f"{i}. {tag.name} - Addr: {tag.address}, Type: {tag.data_type.value}"
                )
            if len(tags) > 5:
                preview_lines.append(f"... and {len(tags) - 5} more")
            
            self.preview_text.setPlainText("\n".join(preview_lines))
            
        except (CSVImportError, ExcelImportError) as e:
            QMessageBox.warning(self, "Import Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to preview: {e}")
    
    def _do_import(self):
        """Perform import"""
        if not self._validate_mapping():
            return
        
        if not self.import_file:
            QMessageBox.warning(self, "No file", "No file selected.")
            return
        
        try:
            if self.is_excel:
                self.imported_tags = import_tags_from_excel(
                    self.import_file,
                    self._get_column_mapping(),
                    self.address_type,
                    self.sheet_name
                )
            else:
                self.imported_tags = import_tags_from_csv(
                    self.import_file,
                    self._get_column_mapping(),
                    self.address_type
                )
            
            if self.imported_tags:
                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Imported {len(self.imported_tags)} tags successfully."
                )
                self.accept()
            else:
                QMessageBox.warning(self, "No tags", "No tags were imported.")
        
        except (CSVImportError, ExcelImportError) as e:
            QMessageBox.warning(self, "Import Error", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to import: {e}")
    
    def _validate_mapping(self) -> bool:
        """Validate column mapping"""
        # Check required fields
        for field in self.REQUIRED_FIELDS:
            combo = self.field_combos[field]
            if not combo.currentData():
                QMessageBox.warning(
                    self,
                    "Validation Error",
                    f"Required field '{self.FIELD_LABELS[field]}' must be mapped."
                )
                return False
        
        return True
    
    def _get_column_mapping(self) -> Dict[str, str]:
        """Get column mapping (CSV column -> field)"""
        mapping = {}
        for field, combo in self.field_combos.items():
            csv_col = combo.currentData()
            if csv_col:
                mapping[csv_col] = field
        return mapping
    
    def get_imported_tags(self):
        """Get imported tags"""
        return self.imported_tags
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

