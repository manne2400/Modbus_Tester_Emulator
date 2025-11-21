"""Template Manager dialog for managing device templates"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QLabel, QMessageBox, QGroupBox, QFormLayout,
    QTextEdit, QComboBox
)
from PyQt6.QtCore import Qt
from typing import Optional, List
from src.models.device_template import DeviceTemplate
from src.models.tag_definition import TagDefinition
from src.storage.template_library import TemplateLibrary
from src.ui.styles.theme import Theme
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateManagerDialog(QDialog):
    """Dialog for managing device templates"""
    
    def __init__(self, parent=None, template_library: Optional[TemplateLibrary] = None):
        """Initialize template manager dialog"""
        super().__init__(parent)
        self.setWindowTitle("Device Templates")
        self.setMinimumSize(800, 600)
        
        self.template_library = template_library or TemplateLibrary()
        self.templates: List[DeviceTemplate] = []
        
        self._setup_ui()
        self._apply_dark_theme()
        self._refresh_templates()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Toolbar
        toolbar_layout = QHBoxLayout()
        
        new_btn = QPushButton("New")
        new_btn.clicked.connect(self._new_template)
        toolbar_layout.addWidget(new_btn)
        
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self._edit_template)
        toolbar_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_template)
        toolbar_layout.addWidget(delete_btn)
        
        toolbar_layout.addStretch()
        
        # Search
        toolbar_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Søg efter navn, producent, model...")
        self.search_edit.textChanged.connect(self._on_search_changed)
        toolbar_layout.addWidget(self.search_edit)
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_templates)
        toolbar_layout.addWidget(refresh_btn)
        
        layout.addLayout(toolbar_layout)
        
        # Templates table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Navn", "Kategori", "Producent", "Model", "Antal Tags"
        ])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.table)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        import_btn = QPushButton("Import CSV/Excel...")
        import_btn.clicked.connect(self._import_template)
        buttons_layout.addWidget(import_btn)
        
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_template)
        buttons_layout.addWidget(export_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(close_btn)
        
        layout.addLayout(buttons_layout)
    
    def _refresh_templates(self):
        """Refresh templates list"""
        self.templates = self.template_library.load_all_templates()
        self._update_table()
    
    def _update_table(self):
        """Update table with templates"""
        # Apply search filter
        search_text = self.search_edit.text().lower()
        filtered_templates = self.templates
        if search_text:
            filtered_templates = [
                t for t in self.templates
                if (search_text in t.name.lower() or
                    (t.manufacturer and search_text in t.manufacturer.lower()) or
                    (t.model and search_text in t.model.lower()) or
                    (t.category and search_text in t.category.lower()))
            ]
        
        self.table.setRowCount(0)
        
        for template in filtered_templates:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(template.name)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            name_item.setData(Qt.ItemDataRole.UserRole, template)
            self.table.setItem(row, 0, name_item)
            
            # Category
            category_item = QTableWidgetItem(template.category or "")
            category_item.setFlags(category_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 1, category_item)
            
            # Manufacturer
            manufacturer_item = QTableWidgetItem(template.manufacturer or "")
            manufacturer_item.setFlags(manufacturer_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 2, manufacturer_item)
            
            # Model
            model_item = QTableWidgetItem(template.model or "")
            model_item.setFlags(model_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 3, model_item)
            
            # Tag count
            count_item = QTableWidgetItem(str(template.get_tag_count()))
            count_item.setFlags(count_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.table.setItem(row, 4, count_item)
        
        self.table.resizeColumnsToContents()
    
    def _on_search_changed(self):
        """Handle search text change"""
        self._update_table()
    
    def _get_selected_template(self) -> Optional[DeviceTemplate]:
        """Get currently selected template"""
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        name_item = self.table.item(row, 0)
        if name_item:
            return name_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def _new_template(self):
        """Create new template"""
        from src.ui.template_edit_dialog import TemplateEditDialog
        
        dialog = TemplateEditDialog(self)
        if dialog.exec():
            template = dialog.get_template()
            if template:
                if self.template_library.save_template(template):
                    self._refresh_templates()
                    QMessageBox.information(self, "Success", f"Template '{template.name}' oprettet.")
                else:
                    QMessageBox.warning(self, "Error", "Kunne ikke gemme template.")
    
    def _edit_template(self):
        """Edit selected template"""
        template = self._get_selected_template()
        if not template:
            QMessageBox.warning(self, "Ingen template valgt", "Vælg en template at redigere.")
            return
        
        from src.ui.template_edit_dialog import TemplateEditDialog
        
        dialog = TemplateEditDialog(self, template)
        if dialog.exec():
            updated_template = dialog.get_template()
            if updated_template:
                # Delete old and save new
                self.template_library.delete_template(template.name)
                if self.template_library.save_template(updated_template):
                    self._refresh_templates()
                    QMessageBox.information(self, "Success", f"Template '{updated_template.name}' opdateret.")
                else:
                    QMessageBox.warning(self, "Error", "Kunne ikke gemme template.")
    
    def _delete_template(self):
        """Delete selected template"""
        template = self._get_selected_template()
        if not template:
            QMessageBox.warning(self, "Ingen template valgt", "Vælg en template at slette.")
            return
        
        reply = QMessageBox.question(
            self,
            "Slet Template",
            f"Er du sikker på at du vil slette template '{template.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.template_library.delete_template(template.name):
                self._refresh_templates()
                QMessageBox.information(self, "Success", f"Template '{template.name}' slettet.")
            else:
                QMessageBox.warning(self, "Error", "Kunne ikke slette template.")
    
    def _import_template(self):
        """Import template from CSV/Excel"""
        from PyQt6.QtWidgets import QFileDialog
        from src.ui.csv_import_dialog import CSVImportDialog
        from src.models.device_template import DeviceTemplate
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Template from CSV/Excel",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        
        if not file_path:
            return
        
        import_dialog = CSVImportDialog(self, Path(file_path))
        if import_dialog.exec():
            tags = import_dialog.get_imported_tags()
            if tags:
                # Create template from imported tags
                from src.ui.template_edit_dialog import TemplateEditDialog
                
                template = DeviceTemplate(
                    name=Path(file_path).stem,
                    tags=tags
                )
                
                edit_dialog = TemplateEditDialog(self, template)
                if edit_dialog.exec():
                    template = edit_dialog.get_template()
                    if template:
                        if self.template_library.save_template(template):
                            self._refresh_templates()
                            QMessageBox.information(
                                self,
                                "Success",
                                f"Template '{template.name}' importeret med {len(tags)} tags."
                            )
    
    def _export_template(self):
        """Export selected template"""
        template = self._get_selected_template()
        if not template:
            QMessageBox.warning(self, "Ingen template valgt", "Vælg en template at eksportere.")
            return
        
        from PyQt6.QtWidgets import QFileDialog
        from src.utils.csv_export import export_template_to_csv
        from src.utils.excel_export import export_template_to_excel
        
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Template",
            f"{template.name}",
            "CSV Files (*.csv);;Excel Files (*.xlsx)"
        )
        
        if file_path:
            success = False
            if selected_filter and "xlsx" in selected_filter.lower():
                success = export_template_to_excel(Path(file_path), template)
            else:
                success = export_template_to_csv(Path(file_path), template)
            
            if success:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Template '{template.name}' eksporteret til {file_path}."
                )
            else:
                QMessageBox.warning(self, "Error", "Kunne ikke eksportere template.")
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)

