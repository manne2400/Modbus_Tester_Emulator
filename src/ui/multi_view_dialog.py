"""Dialog for managing multi-view session groups"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton,
    QListWidgetItem, QMessageBox, QInputDialog
)
from PyQt6.QtCore import Qt
from typing import Dict, List


class MultiViewDialog(QDialog):
    """Dialog for configuring which sessions to show together in multi-view"""
    
    def __init__(self, session_names: List[str], current_groups: Dict[str, List[str]], parent=None):
        """Initialize dialog
        
        Args:
            session_names: List of all available session names
            current_groups: Current multi-view groups (group_name -> [session_names])
            parent: Parent widget
        """
        super().__init__(parent)
        self.setWindowTitle("Manage Multi-view")
        self.setMinimumSize(600, 500)
        self.setModal(True)
        
        self.session_names = session_names
        self.groups: Dict[str, List[str]] = current_groups.copy()
        
        self._setup_ui()
        self._apply_dark_theme()
        self._update_group_list()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        
        # Instructions
        info_label = QLabel(
            "Create groups of sessions that should be displayed side by side.\n"
            "Each group is displayed in its own column in multi-view mode."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Groups list
        groups_label = QLabel("Groups:")
        layout.addWidget(groups_label)
        
        self.groups_list = QListWidget()
        self.groups_list.itemSelectionChanged.connect(self._on_group_selected)
        layout.addWidget(self.groups_list)
        
        # Group buttons
        group_buttons_layout = QHBoxLayout()
        
        self.new_group_btn = QPushButton("New Group")
        self.new_group_btn.clicked.connect(self._new_group)
        group_buttons_layout.addWidget(self.new_group_btn)
        
        self.delete_group_btn = QPushButton("Delete Group")
        self.delete_group_btn.clicked.connect(self._delete_group)
        group_buttons_layout.addWidget(self.delete_group_btn)
        
        group_buttons_layout.addStretch()
        layout.addLayout(group_buttons_layout)
        
        # Sessions in group
        sessions_label = QLabel("Sessions in selected group:")
        layout.addWidget(sessions_label)
        
        self.sessions_list = QListWidget()
        layout.addWidget(self.sessions_list)
        
        # Session buttons
        session_buttons_layout = QHBoxLayout()
        
        self.add_session_btn = QPushButton("Add Session")
        self.add_session_btn.clicked.connect(self._add_session_to_group)
        session_buttons_layout.addWidget(self.add_session_btn)
        
        self.remove_session_btn = QPushButton("Remove Session")
        self.remove_session_btn.clicked.connect(self._remove_session_from_group)
        session_buttons_layout.addWidget(self.remove_session_btn)
        
        session_buttons_layout.addStretch()
        layout.addLayout(session_buttons_layout)
        
        # Dialog buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(ok_btn)
        
        layout.addLayout(buttons_layout)
    
    def _update_group_list(self):
        """Update the groups list widget"""
        self.groups_list.clear()
        for group_name in sorted(self.groups.keys()):
            session_count = len(self.groups[group_name])
            item = QListWidgetItem(f"{group_name} ({session_count} sessions)")
            item.setData(Qt.ItemDataRole.UserRole, group_name)
            self.groups_list.addItem(item)
    
    def _on_group_selected(self):
        """Handle group selection"""
        selected_items = self.groups_list.selectedItems()
        if selected_items:
            group_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
            self._update_sessions_list(group_name)
            self.delete_group_btn.setEnabled(True)
            self.add_session_btn.setEnabled(True)
        else:
            self.sessions_list.clear()
            self.delete_group_btn.setEnabled(False)
            self.add_session_btn.setEnabled(False)
        self.remove_session_btn.setEnabled(False)
    
    def _update_sessions_list(self, group_name: str):
        """Update sessions list for a group"""
        self.sessions_list.clear()
        if group_name in self.groups:
            for session_name in self.groups[group_name]:
                item = QListWidgetItem(session_name)
                self.sessions_list.addItem(item)
    
    def _new_group(self):
        """Create a new group"""
        name, ok = QInputDialog.getText(
            self,
            "New Group",
            "Enter group name:",
            text=f"Group {len(self.groups) + 1}"
        )
        if ok and name:
            if name in self.groups:
                QMessageBox.warning(self, "Error", f"Group '{name}' already exists.")
                return
            self.groups[name] = []
            self._update_group_list()
            # Select the new group
            for i in range(self.groups_list.count()):
                item = self.groups_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == name:
                    self.groups_list.setCurrentItem(item)
                    break
    
    def _delete_group(self):
        """Delete selected group"""
        selected_items = self.groups_list.selectedItems()
        if not selected_items:
            return
        
        group_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Delete Group",
            f"Are you sure you want to delete the group '{group_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            del self.groups[group_name]
            self._update_group_list()
            self.sessions_list.clear()
    
    def _add_session_to_group(self):
        """Add a session to the selected group"""
        selected_items = self.groups_list.selectedItems()
        if not selected_items:
            return
        
        group_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        # Get available sessions (not already in any group)
        used_sessions = set()
        for sessions in self.groups.values():
            used_sessions.update(sessions)
        available = [s for s in self.session_names if s not in used_sessions]
        
        if not available:
            QMessageBox.information(self, "Info", "All sessions are already in groups.")
            return
        
        # Let user select session
        session, ok = QInputDialog.getItem(
            self,
            "Add Session",
            "Select session:",
            available,
            0,
            False
        )
        if ok and session:
            self.groups[group_name].append(session)
            self._update_sessions_list(group_name)
            self._update_group_list()
    
    def _remove_session_from_group(self):
        """Remove selected session from group"""
        selected_items = self.groups_list.selectedItems()
        if not selected_items:
            return
        
        group_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        session_items = self.sessions_list.selectedItems()
        if not session_items:
            return
        
        session_name = session_items[0].text()
        if session_name in self.groups[group_name]:
            self.groups[group_name].remove(session_name)
            self._update_sessions_list(group_name)
            self._update_group_list()
    
    def get_groups(self) -> Dict[str, List[str]]:
        """Get configured groups"""
        # Only return groups with at least one session
        return {name: sessions for name, sessions in self.groups.items() if sessions}
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                color: #cccccc;
            }
            QListWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                color: #cccccc;
            }
            QListWidget::item:selected {
                background-color: #094771;
                color: white;
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
        """)

