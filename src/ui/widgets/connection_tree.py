"""Connection tree widget"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from src.models.connection_profile import ConnectionProfile, ConnectionType
from src.models.session_definition import SessionDefinition
from typing import List, Dict


class ConnectionTree(QTreeWidget):
    """Tree widget showing connections and sessions"""
    
    connection_selected = pyqtSignal(str)  # profile_name
    new_connection_requested = pyqtSignal()
    edit_connection_requested = pyqtSignal(str)  # profile_name
    delete_connection_requested = pyqtSignal(str)  # profile_name
    new_session_requested = pyqtSignal()
    multi_view_group_selected = pyqtSignal(str)  # group_name
    
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
        sessions: Dict[str, SessionDefinition],
        multi_view_groups: Dict[str, List[str]] = None,
        multi_view_active: bool = False
    ):
        """Update tree with connections and sessions, grouped by type
        
        Args:
            connections: List of connection profiles
            sessions: Dict of session definitions
            multi_view_groups: Dict of multi-view groups (group_name -> [session_names])
            multi_view_active: Whether multi-view mode is active
        """
        self.clear()
        
        # If multi-view is active, show multi-view groups first
        if multi_view_active and multi_view_groups:
            multi_view_group = QTreeWidgetItem(self)
            multi_view_group.setText(0, "Multi-view Grupper")
            multi_view_group.setData(0, Qt.ItemDataRole.UserRole, ("multi_view_group", ""))
            # Make group item bold
            font = multi_view_group.font(0)
            font.setBold(True)
            multi_view_group.setFont(0, font)
            multi_view_group.setExpanded(True)
            
            for group_name, session_names in multi_view_groups.items():
                group_item = QTreeWidgetItem(multi_view_group)
                group_item.setText(0, f"📊 {group_name}")
                group_item.setData(0, Qt.ItemDataRole.UserRole, ("multi_view", group_name))
                
                # Add sessions in this group
                for session_name in session_names:
                    if session_name in sessions:
                        session_item = QTreeWidgetItem(group_item)
                        session_item.setText(0, session_name)
                        session_item.setData(0, Qt.ItemDataRole.UserRole, ("session", session_name))
                
                group_item.setExpanded(True)
        
        # Group connections by type
        tcp_connections = [c for c in connections if c.connection_type == ConnectionType.TCP]
        rtu_connections = [c for c in connections if c.connection_type == ConnectionType.RTU]
        
        # Create TCP group
        if tcp_connections:
            tcp_group = QTreeWidgetItem(self)
            tcp_group.setText(0, "Modbus TCP")
            tcp_group.setData(0, Qt.ItemDataRole.UserRole, ("type_group", "TCP"))
            # Make group item bold
            font = tcp_group.font(0)
            font.setBold(True)
            tcp_group.setFont(0, font)
            tcp_group.setExpanded(True)
            
            for conn in tcp_connections:
                conn_item = QTreeWidgetItem(tcp_group)
                conn_item.setText(0, conn.name)
                conn_item.setData(0, Qt.ItemDataRole.UserRole, ("connection", conn.name))
                
                # Add sessions for this connection (only if not in multi-view or multi-view is off)
                if not multi_view_active:
                    for session in sessions.values():
                        if session.connection_profile_name == conn.name:
                            session_item = QTreeWidgetItem(conn_item)
                            session_item.setText(0, session.name)
                            session_item.setData(0, Qt.ItemDataRole.UserRole, ("session", session.name))
                else:
                    # Only show sessions not in any multi-view group
                    sessions_in_groups = set()
                    for group_sessions in (multi_view_groups or {}).values():
                        sessions_in_groups.update(group_sessions)
                    
                    for session in sessions.values():
                        if (session.connection_profile_name == conn.name and 
                            session.name not in sessions_in_groups):
                            session_item = QTreeWidgetItem(conn_item)
                            session_item.setText(0, session.name)
                            session_item.setData(0, Qt.ItemDataRole.UserRole, ("session", session.name))
                
                conn_item.setExpanded(True)
        
        # Create RTU group
        if rtu_connections:
            rtu_group = QTreeWidgetItem(self)
            rtu_group.setText(0, "Modbus RTU")
            rtu_group.setData(0, Qt.ItemDataRole.UserRole, ("type_group", "RTU"))
            # Make group item bold
            font = rtu_group.font(0)
            font.setBold(True)
            rtu_group.setFont(0, font)
            rtu_group.setExpanded(True)
            
            for conn in rtu_connections:
                conn_item = QTreeWidgetItem(rtu_group)
                conn_item.setText(0, conn.name)
                conn_item.setData(0, Qt.ItemDataRole.UserRole, ("connection", conn.name))
                
                # Add sessions for this connection (only if not in multi-view or multi-view is off)
                if not multi_view_active:
                    for session in sessions.values():
                        if session.connection_profile_name == conn.name:
                            session_item = QTreeWidgetItem(conn_item)
                            session_item.setText(0, session.name)
                            session_item.setData(0, Qt.ItemDataRole.UserRole, ("session", session.name))
                else:
                    # Only show sessions not in any multi-view group
                    sessions_in_groups = set()
                    for group_sessions in (multi_view_groups or {}).values():
                        sessions_in_groups.update(group_sessions)
                    
                    for session in sessions.values():
                        if (session.connection_profile_name == conn.name and 
                            session.name not in sessions_in_groups):
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
                
                if item_type == "multi_view":
                    # Multi-view group selected - emit signal to show this group
                    self.multi_view_group_selected.emit(item_name)
                elif item_type == "type_group":
                    # Group level menu - can add new connection of this type
                    new_connection_action = menu.addAction("Ny forbindelse")
                    new_connection_action.triggered.connect(
                        lambda: self.new_connection_requested.emit()
                    )
                elif item_type == "connection":
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
            elif item_type == "multi_view":
                # Double-click on multi-view group to show it
                self.multi_view_group_selected.emit(item_name)
