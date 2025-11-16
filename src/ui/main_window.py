"""Main window for Modbus Tester application"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QTabWidget, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction
from pathlib import Path
from src.ui.widgets.connection_tree import ConnectionTree
from src.ui.log_viewer import LogViewer
from src.ui.connection_dialog import ConnectionDialog
from src.ui.session_tab import SessionTab
from src.storage.config_manager import ConfigManager
from src.storage.project_manager import ProjectManager
from src.application.session_manager import SessionManager
from src.application.polling_engine import PollingEngine
from src.models.connection_profile import ConnectionProfile
from src.models.session_definition import SessionDefinition
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.setWindowTitle("Modbus Tester")
        self.setGeometry(100, 100, 1400, 800)
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.project_manager = ProjectManager(self.config_manager)
        self.session_manager = SessionManager()
        self.polling_engine = PollingEngine(self.session_manager)
        
        # Connect polling engine signals
        self.polling_engine.poll_result.connect(self._on_poll_result)
        self.polling_engine.session_error.connect(self._on_session_error)
        
        # Set log callback
        self.log_viewer = None
        self.session_manager.set_log_callback(self._on_log_entry)
        
        # UI components
        self.connection_tree = None
        self.session_tabs = QTabWidget()
        self.session_tabs.setTabsClosable(True)
        self.session_tabs.tabCloseRequested.connect(self._close_session_tab)
        
        # Data
        self.connections: list[ConnectionProfile] = []
        self.sessions: dict[str, SessionDefinition] = {}
        self.session_tab_widgets: dict[str, SessionTab] = {}
        
        self._setup_ui()
        self._load_configuration()
        
        # Start polling engine
        self.polling_engine.start()
    
    def _setup_ui(self):
        """Setup user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left side: Connection tree
        self.connection_tree = ConnectionTree()
        self.connection_tree.connection_selected.connect(self._on_connection_selected)
        self.connection_tree.new_connection_requested.connect(self._on_new_connection)
        self.connection_tree.edit_connection_requested.connect(self._on_edit_connection)
        self.connection_tree.delete_connection_requested.connect(self._on_delete_connection)
        self.connection_tree.new_session_requested.connect(self._on_new_session)
        splitter.addWidget(self.connection_tree)
        splitter.setStretchFactor(0, 0)
        
        # Right side: Session tabs
        splitter.addWidget(self.session_tabs)
        splitter.setStretchFactor(1, 1)
        
        # Menu bar
        self._create_menu_bar()
        
        # Toolbar
        self._create_toolbar()
        
        # Status bar
        self.statusBar().showMessage("Klar")
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("Filer")
        
        new_project_action = QAction("Nyt projekt", self)
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Åbn projekt...", self)
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction("Gem projekt...", self)
        save_project_action.triggered.connect(self._save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Afslut", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Connection menu
        connection_menu = menubar.addMenu("Forbindelse")
        
        new_connection_action = QAction("Ny forbindelse...", self)
        new_connection_action.triggered.connect(self._on_new_connection)
        connection_menu.addAction(new_connection_action)
        
        # Session menu
        session_menu = menubar.addMenu("Session")
        
        new_session_action = QAction("Ny session...", self)
        new_session_action.triggered.connect(self._on_new_session)
        session_menu.addAction(new_session_action)
        
        start_all_action = QAction("Start alle", self)
        start_all_action.triggered.connect(self._start_all_sessions)
        session_menu.addAction(start_all_action)
        
        stop_all_action = QAction("Stop alle", self)
        stop_all_action.triggered.connect(self._stop_all_sessions)
        session_menu.addAction(stop_all_action)
        
        # View menu
        view_menu = menubar.addMenu("Vis")
        
        self.show_log_action = QAction("Vis log", self)
        self.show_log_action.setCheckable(True)
        self.show_log_action.setChecked(False)
        self.show_log_action.triggered.connect(self._toggle_log_viewer)
        view_menu.addAction(self.show_log_action)
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        new_connection_action = QAction("Ny forbindelse", self)
        new_connection_action.triggered.connect(self._on_new_connection)
        toolbar.addAction(new_connection_action)
        
        new_session_action = QAction("Ny session", self)
        new_session_action.triggered.connect(self._on_new_session)
        toolbar.addAction(new_session_action)
    
    def _load_configuration(self):
        """Load saved configuration"""
        # Load connections
        self.connections = self.config_manager.load_connections()
        for conn in self.connections:
            self.session_manager.add_connection(conn)
        
        # Load sessions
        sessions = self.config_manager.load_sessions()
        for session in sessions:
            self.sessions[session.name] = session
            self.session_manager.add_session(session)
            self._create_session_tab(session)
        
        # Update connection tree
        self.connection_tree.update_connections(self.connections, self.sessions)
        
        # Try to load last project
        last_project = self.project_manager.get_last_project_path()
        if last_project and last_project.exists():
            reply = QMessageBox.question(
                self,
                "Genåbn projekt",
                f"Vil du genåbne sidste projekt?\n{last_project}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._load_project_file(last_project)
    
    def _new_project(self):
        """Create new project"""
        reply = QMessageBox.question(
            self,
            "Nyt projekt",
            "Dette vil slette alle nuværende forbindelser og sessions. Fortsæt?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all
            self.connections.clear()
            self.sessions.clear()
            self.session_tabs.clear()
            self.session_tab_widgets.clear()
            self.connection_tree.update_connections([], {})
            self.session_manager = SessionManager()
            self.polling_engine = PollingEngine(self.session_manager)
            self.polling_engine.start()
    
    def _open_project(self):
        """Open project file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Åbn projekt",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            self._load_project_file(Path(file_path))
    
    def _load_project_file(self, file_path: Path):
        """Load project from file"""
        connections, sessions = self.project_manager.load_project(file_path)
        
        # Clear current
        self.connections.clear()
        self.sessions.clear()
        self.session_tabs.clear()
        self.session_tab_widgets.clear()
        
        # Load new
        self.connections = connections
        for conn in connections:
            self.session_manager.add_connection(conn)
        
        for session in sessions:
            self.sessions[session.name] = session
            self.session_manager.add_session(session)
            self._create_session_tab(session)
        
        self.connection_tree.update_connections(self.connections, self.sessions)
    
    def _save_project(self):
        """Save project to file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Gem projekt",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            sessions = list(self.sessions.values())
            self.project_manager.save_project(Path(file_path), self.connections, sessions)
            QMessageBox.information(self, "Projekt gemt", f"Projekt gemt til {file_path}")
    
    def _on_new_connection(self):
        """Handle new connection request"""
        dialog = ConnectionDialog(self)
        if dialog.exec():
            profile = dialog.get_connection_profile()
            if profile:
                self.connections.append(profile)
                self.session_manager.add_connection(profile)
                self.config_manager.save_connections(self.connections)
                self.connection_tree.update_connections(self.connections, self.sessions)
    
    def _on_edit_connection(self, profile_name: str):
        """Handle edit connection request"""
        profile = next((c for c in self.connections if c.name == profile_name), None)
        if profile:
            dialog = ConnectionDialog(self, profile)
            if dialog.exec():
                updated_profile = dialog.get_connection_profile()
                if updated_profile:
                    # Update
                    index = next(i for i, c in enumerate(self.connections) if c.name == profile_name)
                    self.connections[index] = updated_profile
                    self.session_manager.remove_connection(profile_name)
                    self.session_manager.add_connection(updated_profile)
                    self.config_manager.save_connections(self.connections)
                    self.connection_tree.update_connections(self.connections, self.sessions)
    
    def _on_delete_connection(self, profile_name: str):
        """Handle delete connection request"""
        reply = QMessageBox.question(
            self,
            "Slet forbindelse",
            f"Er du sikker på at du vil slette '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.connections = [c for c in self.connections if c.name != profile_name]
            self.session_manager.remove_connection(profile_name)
            self.config_manager.save_connections(self.connections)
            self.connection_tree.update_connections(self.connections, self.sessions)
    
    def _on_new_session(self):
        """Handle new session request"""
        if not self.connections:
            QMessageBox.warning(self, "Ingen forbindelse", "Opret først en forbindelse.")
            return
        
        # Create default session
        session = SessionDefinition(
            name=f"Session {len(self.sessions) + 1}",
            connection_profile_name=self.connections[0].name,
            slave_id=1,
            function_code=3,
            start_address=0,
            quantity=10,
            poll_interval_ms=1000
        )
        
        self.sessions[session.name] = session
        self.session_manager.add_session(session)
        self.config_manager.save_sessions(list(self.sessions.values()))
        self._create_session_tab(session)
        self.connection_tree.update_connections(self.connections, self.sessions)
    
    def _create_session_tab(self, session: SessionDefinition):
        """Create a session tab"""
        tab = SessionTab(session, self.connections, self.session_manager, self.polling_engine)
        self.session_tabs.addTab(tab, session.name)
        self.session_tab_widgets[session.name] = tab
    
    def _close_session_tab(self, index: int):
        """Close a session tab"""
        tab = self.session_tabs.widget(index)
        if tab and isinstance(tab, SessionTab):
            session_id = tab.session.name
            self.session_manager.stop_session(session_id)
            self.session_manager.remove_session(session_id)
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.session_tab_widgets:
                del self.session_tab_widgets[session_id]
            self.config_manager.save_sessions(list(self.sessions.values()))
            self.connection_tree.update_connections(self.connections, self.sessions)
    
    def _on_connection_selected(self, profile_name: str):
        """Handle connection selection"""
        pass
    
    def _start_all_sessions(self):
        """Start all sessions"""
        for session in self.sessions.values():
            self.session_manager.start_session(session.name)
            if session.name in self.session_tab_widgets:
                self.session_tab_widgets[session.name].update_status()
    
    def _stop_all_sessions(self):
        """Stop all sessions"""
        for session in self.sessions.values():
            self.session_manager.stop_session(session.name)
            if session.name in self.session_tab_widgets:
                self.session_tab_widgets[session.name].update_status()
    
    def _toggle_log_viewer(self):
        """Toggle log viewer visibility"""
        if self.show_log_action.isChecked():
            if not self.log_viewer:
                self.log_viewer = LogViewer()
            self.log_viewer.show()
        else:
            if self.log_viewer:
                self.log_viewer.hide()
    
    def _on_log_entry(self, entry):
        """Handle log entry from transport"""
        if self.log_viewer:
            self.log_viewer.add_entry(entry)
    
    def _on_poll_result(self, session_id: str, result):
        """Handle poll result"""
        if session_id in self.session_tab_widgets:
            self.session_tab_widgets[session_id].update_data(result)
    
    def _on_session_error(self, session_id: str, error_message: str):
        """Handle session error"""
        if session_id in self.session_tab_widgets:
            self.session_tab_widgets[session_id].show_error(error_message)
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save configuration
        self.config_manager.save_connections(self.connections)
        self.config_manager.save_sessions(list(self.sessions.values()))
        
        # Stop polling
        self.polling_engine.stop()
        
        # Disconnect all
        for conn in self.connections:
            self.session_manager.disconnect(conn.name)
        
        event.accept()
