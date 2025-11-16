"""Connection tree widget"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from src.models.connection_profile import ConnectionProfile
from src.models.session_definition import SessionDefinition
from typing import List, Dict


class ConnectionTree(QTreeWidget):
    """Tree widget showing connections and sessions"""
    
    connection_selected = pyqtSignal(str)  # profile_name
    new_connection_requested = pyqtSignal()
    edit_connection_requested = pyqtSignal(str)  # profile_name
    delete_connection_requested = pyqtSignal(str)  # profile_name
    new_session_requested = pyqtSignal()
    
    def __init__(self):
        """Initialize connection tree"""
        super().__init__()
        self.setHeaderLabel("Forbindelser")
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
    
    def update_connections(
        self,
        connections: List[ConnectionProfile],
        sessions: Dict[str, SessionDefinition]
    ):
        """Update tree with connections and sessions"""
        self.clear()
        
        for conn in connections:
            conn_item = QTreeWidgetItem(self)
            conn_item.setText(0, conn.name)
            conn_item.setData(0, Qt.ItemDataRole.UserRole, ("connection", conn.name))
            
            # Add sessions for this connection
            for session in sessions.values():
                if session.connection_profile_name == conn.name:
                    session_item = QTreeWidgetItem(conn_item)
                    session_item.setText(0, session.name)
                    session_item.setData(0, Qt.ItemDataRole.UserRole, ("session", session.name))
            
            conn_item.setExpanded(True)
    
    def _show_context_menu(self, position):
        """Show context menu"""
        item = self.itemAt(position)
        menu = QMenu(self)
        
        if item:
            data = item.data(0, Qt.ItemDataRole.UserRole)
            if data:
                item_type, item_name = data
                
                if item_type == "connection":
                    new_session_action = menu.addAction("Ny session")
                    new_session_action.triggered.connect(
                        lambda: self.new_session_requested.emit()
                    )
                    menu.addSeparator()
                    edit_action = menu.addAction("Rediger")
                    edit_action.triggered.connect(
                        lambda: self.edit_connection_requested.emit(item_name)
                    )
                    delete_action = menu.addAction("Slet")
                    delete_action.triggered.connect(
                        lambda: self.delete_connection_requested.emit(item_name)
                    )
                elif item_type == "session":
                    # Session context menu could be added here
                    pass
        else:
            # Root level menu
            new_connection_action = menu.addAction("Ny forbindelse")
            new_connection_action.triggered.connect(
                lambda: self.new_connection_requested.emit()
            )
        
        if menu.actions():
            menu.exec(self.mapToGlobal(position))
    
    def _on_item_double_clicked(self, item, column):
        """Handle item double click"""
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            item_type, item_name = data
            if item_type == "connection":
                self.connection_selected.emit(item_name)
