"""Main window for Modbus Tester application"""
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QMenuBar, QMenu, QToolBar, QStatusBar, QTabWidget, QMessageBox,
    QGroupBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QIcon, QFont
from pathlib import Path
from src.ui.widgets.connection_tree import ConnectionTree
from src.ui.widgets.multi_view_container import MultiViewContainer
from src.ui.log_viewer import LogViewer
from src.ui.connection_dialog import ConnectionDialog
from src.ui.session_tab import SessionTab
from src.ui.about_dialog import AboutDialog
from src.ui.help_dialog import HelpDialog
from src.ui.multi_view_dialog import MultiViewDialog
from src.ui.simulator_dialog import SimulatorDialog
from src.ui.device_scanner_dialog import DeviceScannerDialog
from src.ui.frame_analyzer_dialog import FrameAnalyzerDialog
from src.ui.template_manager_dialog import TemplateManagerDialog
from src.storage.template_library import TemplateLibrary
from src.application.snapshot_manager import SnapshotManager
from src.storage.snapshot_store import SnapshotStore
from src.ui.styles.theme import Theme
from src.application.simulator_manager import SimulatorManager
from src.storage.config_manager import ConfigManager
from src.storage.project_manager import ProjectManager
from src.application.session_manager import SessionManager
from src.application.polling_engine import PollingEngine
from src.application.trace_store import TraceStore
from src.models.connection_profile import ConnectionProfile, ConnectionType
from src.models.session_definition import SessionDefinition
from src.protocol.function_codes import FunctionCode
from src.application.tcp_scanner import TcpDeviceInfo
from src.application.rtu_scanner import DeviceInfo
from src.utils.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        """Initialize main window"""
        super().__init__()
        self.setWindowTitle("Modbus Tester")
        self.setGeometry(100, 100, 1400, 800)
        
        # Apply professional styling
        self._apply_styling()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.project_manager = ProjectManager(self.config_manager)
        self.session_manager = SessionManager()
        self.polling_engine = PollingEngine(self.session_manager)
        self.simulator_manager = SimulatorManager()
        self.trace_store = TraceStore()
        self.template_library = TemplateLibrary()
        self.snapshot_store = SnapshotStore()
        self.snapshot_manager = SnapshotManager(self.session_manager)
        
        # Connect polling engine signals
        self.polling_engine.poll_result.connect(self._on_poll_result)
        self.polling_engine.session_error.connect(self._on_session_error)
        
        # Set log callback
        self.log_viewer = None
        self.session_manager.set_log_callback(self._on_log_entry)
        
        # Set trace callback
        self.session_manager.set_trace_callback(self._on_trace_entry)
        
        # UI components
        self.connection_tree = None
        self.session_container = MultiViewContainer()
        self.session_container.single_view.tabCloseRequested.connect(self._close_session_tab)
        self.session_container.show_with_session.connect(self._show_sessions_together)
        
        # Multi-view state
        self.multi_view_active = False
        self.multi_view_groups: dict[str, list[str]] = {}  # group_name -> [session_names]
        
        # Data
        self.connections: list[ConnectionProfile] = []
        self.sessions: dict[str, SessionDefinition] = {}
        self.session_tab_widgets: dict[str, SessionTab] = {}
        
        self._setup_ui()
        self._load_ui_settings()
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
        main_layout.setContentsMargins(Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD)
        main_layout.setSpacing(Theme.SPACING_STANDARD)
        
        # Splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Left side: Connection tree in GroupBox
        connections_group = QGroupBox("Connections")
        connections_layout = QVBoxLayout()
        connections_layout.setContentsMargins(Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT)
        self.connection_tree = ConnectionTree()
        self.connection_tree.connection_selected.connect(self._on_connection_selected)
        self.connection_tree.new_connection_requested.connect(self._on_new_connection)
        self.connection_tree.edit_connection_requested.connect(self._on_edit_connection)
        self.connection_tree.delete_connection_requested.connect(self._on_delete_connection)
        self.connection_tree.new_session_requested.connect(self._on_new_session)
        self.connection_tree.multi_view_group_selected.connect(self._on_multi_view_group_selected)
        connections_layout.addWidget(self.connection_tree)
        connections_group.setLayout(connections_layout)
        self.main_splitter.addWidget(connections_group)
        self.main_splitter.setStretchFactor(0, 0)
        
        # Right side: Session container in GroupBox
        sessions_group = QGroupBox("Sessions")
        sessions_layout = QVBoxLayout()
        sessions_layout.setContentsMargins(Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT)
        sessions_layout.addWidget(self.session_container)
        sessions_group.setLayout(sessions_layout)
        self.main_splitter.addWidget(sessions_group)
        self.main_splitter.setStretchFactor(1, 1)
        
        # Menu bar
        self._create_menu_bar()
        
        # Toolbar
        self._create_toolbar()
        
        # Hide status bar (remove blue line)
        self.statusBar().hide()
    
    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_project_action = QAction("New Project", self)
        new_project_action.triggered.connect(self._new_project)
        file_menu.addAction(new_project_action)
        
        open_project_action = QAction("Open Project...", self)
        open_project_action.triggered.connect(self._open_project)
        file_menu.addAction(open_project_action)
        
        save_project_action = QAction("Save Project...", self)
        save_project_action.triggered.connect(self._save_project)
        file_menu.addAction(save_project_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Connection menu
        connection_menu = menubar.addMenu("Connection")
        
        new_connection_action = QAction("New Connection...", self)
        new_connection_action.triggered.connect(self._on_new_connection)
        connection_menu.addAction(new_connection_action)
        
        connection_menu.addSeparator()
        
        device_scanner_action = QAction("Device Scanner...", self)
        device_scanner_action.triggered.connect(self._show_device_scanner)
        connection_menu.addAction(device_scanner_action)
        
        # Session menu
        session_menu = menubar.addMenu("Session")
        
        new_session_action = QAction("New Session...", self)
        new_session_action.triggered.connect(self._on_new_session)
        session_menu.addAction(new_session_action)
        
        start_all_action = QAction("Start All", self)
        start_all_action.triggered.connect(self._start_all_sessions)
        session_menu.addAction(start_all_action)
        
        stop_all_action = QAction("Stop All", self)
        stop_all_action.triggered.connect(self._stop_all_sessions)
        session_menu.addAction(stop_all_action)
        
        session_menu.addSeparator()
        
        device_templates_action = QAction("Device Templates...", self)
        device_templates_action.triggered.connect(self._show_device_templates)
        session_menu.addAction(device_templates_action)
        
        # Advanced menu
        advanced_menu = menubar.addMenu("Advanced")
        
        frame_analyzer_action = QAction("Frame Analyzer...", self)
        frame_analyzer_action.triggered.connect(self._show_frame_analyzer)
        advanced_menu.addAction(frame_analyzer_action)
        
        simulator_action = QAction("Modbus Simulator...", self)
        simulator_action.triggered.connect(self._show_simulator_dialog)
        advanced_menu.addAction(simulator_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        self.show_log_action = QAction("Show Log", self)
        self.show_log_action.setCheckable(True)
        self.show_log_action.setChecked(False)
        self.show_log_action.triggered.connect(self._toggle_log_viewer)
        view_menu.addAction(self.show_log_action)
        
        view_menu.addSeparator()
        
        self.multi_view_action = QAction("Multi-view", self)
        self.multi_view_action.setCheckable(True)
        self.multi_view_action.setChecked(False)
        self.multi_view_action.triggered.connect(self._toggle_multi_view)
        view_menu.addAction(self.multi_view_action)
        
        manage_multi_view_action = QAction("Manage Multi-view...", self)
        manage_multi_view_action.triggered.connect(self._manage_multi_view)
        view_menu.addAction(manage_multi_view_action)

                # Snapshots menu
        snapshots_menu = menubar.addMenu("Snapshots")
        
        take_snapshot_action = QAction("Take Snapshot...", self)
        take_snapshot_action.triggered.connect(self._take_snapshot)
        snapshots_menu.addAction(take_snapshot_action)
        
        manage_snapshots_action = QAction("Manage Snapshots...", self)
        manage_snapshots_action.triggered.connect(self._manage_snapshots)
        snapshots_menu.addAction(manage_snapshots_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        help_action = QAction("User Guide", self)
        help_action.triggered.connect(self._show_help)
        help_menu.addAction(help_action)
        
        help_menu.addSeparator()
        
        about_action = QAction("About Modbus Tester", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
        
    
    def _create_toolbar(self):
        """Create toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        new_connection_action = QAction("New Connection", self)
        new_connection_action.triggered.connect(self._on_new_connection)
        toolbar.addAction(new_connection_action)
        
        toolbar.addSeparator()
        
        new_session_action = QAction("New Session", self)
        new_session_action.triggered.connect(self._on_new_session)
        toolbar.addAction(new_session_action)
    
    def _apply_styling(self):
        """Apply dark theme styling to the application"""
        Theme.apply_to_widget(self)
    
    def _load_ui_settings(self):
        """Load UI settings (window geometry and splitter sizes)"""
        window_geometry, splitter_sizes = self.config_manager.load_ui_settings()
        
        if window_geometry:
            x = window_geometry.get("x", 100)
            y = window_geometry.get("y", 100)
            width = window_geometry.get("width", 1400)
            height = window_geometry.get("height", 800)
            self.setGeometry(x, y, width, height)
        
        if splitter_sizes and len(splitter_sizes) >= 2:
            self.main_splitter.setSizes(splitter_sizes)
    
    def _save_ui_settings(self):
        """Save UI settings (window geometry and splitter sizes)"""
        geometry = {
            "x": self.geometry().x(),
            "y": self.geometry().y(),
            "width": self.geometry().width(),
            "height": self.geometry().height()
        }
        splitter_sizes = self.main_splitter.sizes()
        self.config_manager.save_ui_settings(geometry, splitter_sizes)
    
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
        self.connection_tree.update_connections(
            self.connections, 
            self.sessions,
            self.multi_view_groups,
            self.multi_view_active
        )
        
        # Try to load last project
        last_project = self.project_manager.get_last_project_path()
        if last_project and last_project.exists():
            reply = QMessageBox.question(
                self,
                "Reopen Project",
                f"Do you want to reopen the last project?\n{last_project}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._load_project_file(last_project)
    
    def _new_project(self):
        """Create new project"""
        reply = QMessageBox.question(
            self,
            "New Project",
            "This will delete all current connections and sessions. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all
            self.connections.clear()
            self.sessions.clear()
            # Clear container
            for tabs in self.session_container.get_all_tabs():
                tabs.clear()
            self.session_tab_widgets.clear()
            self.multi_view_groups.clear()
            self.multi_view_active = False
            self.multi_view_action.setChecked(False)
            self.session_container.set_single_view()
            self.connection_tree.update_connections([], {}, {}, False)
            self.session_manager = SessionManager()
            self.polling_engine = PollingEngine(self.session_manager)
            self.polling_engine.start()
    
    def _open_project(self):
        """Open project file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Project",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            self._load_project_file(Path(file_path))
    
    def _load_project_file(self, file_path: Path):
        """Load project from file"""
        connections, sessions, multi_view_groups, multi_view_active = self.project_manager.load_project(file_path)
        
        # Clear current
        self.connections.clear()
        self.sessions.clear()
        # Clear container
        for tabs in self.session_container.get_all_tabs():
            tabs.clear()
        self.session_tab_widgets.clear()
        self.multi_view_groups.clear()
        self.multi_view_active = False
        self.multi_view_action.setChecked(False)
        self.session_container.set_single_view()
        
        # Load new
        self.connections = connections
        for conn in connections:
            self.session_manager.add_connection(conn)
        
        for session in sessions:
            self.sessions[session.name] = session
            self.session_manager.add_session(session)
            self._create_session_tab(session)
        
        # Load multi-view configuration
        self.multi_view_groups = multi_view_groups
        self.multi_view_active = multi_view_active
        self.multi_view_action.setChecked(multi_view_active)
        
        # Apply multi-view if active
        if self.multi_view_active and self.multi_view_groups:
            self.session_container.set_multi_view(self.multi_view_groups)
        
        self.connection_tree.update_connections(
            self.connections, 
            self.sessions,
            self.multi_view_groups,
            self.multi_view_active
        )
    
    def _save_project(self):
        """Save project to file"""
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Project",
            "",
            "JSON Files (*.json)"
        )
        if file_path:
            sessions = list(self.sessions.values())
            self.project_manager.save_project(
                Path(file_path), 
                self.connections, 
                sessions,
                self.multi_view_groups,
                self.multi_view_active
            )
            QMessageBox.information(self, "Project Saved", f"Project saved to {file_path}")
    
    def _on_new_connection(self):
        """Handle new connection request"""
        dialog = ConnectionDialog(self)
        if dialog.exec():
            profile = dialog.get_connection_profile()
            if profile:
                self.connections.append(profile)
                self.session_manager.add_connection(profile)
                self.config_manager.save_connections(self.connections)
                self.connection_tree.update_connections(
                    self.connections, 
                    self.sessions,
                    self.multi_view_groups,
                    self.multi_view_active
                )
    
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
                    self.connection_tree.update_connections(
                    self.connections, 
                    self.sessions,
                    self.multi_view_groups,
                    self.multi_view_active
                )
    
    def _on_delete_connection(self, profile_name: str):
        """Handle delete connection request"""
        reply = QMessageBox.question(
            self,
            "Delete Connection",
            f"Are you sure you want to delete '{profile_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.connections = [c for c in self.connections if c.name != profile_name]
            self.session_manager.remove_connection(profile_name)
            self.config_manager.save_connections(self.connections)
            self.connection_tree.update_connections(
                self.connections, 
                self.sessions,
                self.multi_view_groups,
                self.multi_view_active
            )
    
    def _on_new_session(self):
        """Handle new session request"""
        if not self.connections:
            QMessageBox.warning(self, "No Connection", "Please create a connection first.")
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
        self.connection_tree.update_connections(
            self.connections, 
            self.sessions,
            self.multi_view_groups,
            self.multi_view_active
        )
    
    def _create_session_tab(self, session: SessionDefinition):
        """Create a session tab"""
        tab = SessionTab(session, self.connections, self.session_manager, self.polling_engine, self.config_manager, self.template_library)
        # Connect signal to update tree when connection changes
        tab.connection_changed.connect(self._on_session_connection_changed)
        # Add to container
        self.session_container.add_session_tab(session.name, tab)
        # Connect tab close for this tab widget
        tab_widget = self.session_container.get_tab_widget(session.name)
        if tab_widget:
            tab_widget.tabCloseRequested.connect(self._close_session_tab)
        self.session_tab_widgets[session.name] = tab
    
    def _close_session_tab(self, index: int):
        """Close a session tab"""
        # Find which tab widget this is from
        sender = self.sender()
        if not sender:
            return
        
        tab = sender.widget(index)
        if tab and isinstance(tab, SessionTab):
            session_id = tab.session.name
            # Stop session if running
            self.session_manager.stop_session(session_id)
            # Remove from session manager
            self.session_manager.remove_session(session_id)
            # Remove from dictionaries
            if session_id in self.sessions:
                del self.sessions[session_id]
            if session_id in self.session_tab_widgets:
                del self.session_tab_widgets[session_id]
            # Remove from multi-view groups if present
            if self.multi_view_active:
                for group_name, session_names in list(self.multi_view_groups.items()):
                    if session_id in session_names:
                        session_names.remove(session_id)
                        if not session_names:
                            del self.multi_view_groups[group_name]
            # Remove tab from UI
            self.session_container.remove_session_tab(session_id)
            # Save updated sessions
            self.config_manager.save_sessions(list(self.sessions.values()))
            # Update connection tree
            self.connection_tree.update_connections(
                self.connections, 
                self.sessions,
                self.multi_view_groups,
                self.multi_view_active
            )
    
    def _on_connection_selected(self, profile_name: str):
        """Handle connection selection"""
        pass
    
    def _on_multi_view_group_selected(self, group_name: str):
        """Handle multi-view group selection - ensure all groups are visible, focus on selected"""
        if not self.multi_view_active or group_name not in self.multi_view_groups:
            return
        
        # If multi-view is not showing all groups, rebuild it
        # Store all tabs
        tabs_to_move = {}
        for session_name, tab in list(self.session_tab_widgets.items()):
            tabs_to_move[session_name] = tab
        
        # Clear and set multi-view with ALL groups
        self.session_container.set_single_view()
        for tabs in self.session_container.get_all_tabs():
            tabs.clear()
        
        self.session_container.set_multi_view(self.multi_view_groups)
        
        # Add all tabs to appropriate groups
        for session_name, tab in tabs_to_move.items():
            self.session_container.add_session_tab(session_name, tab)
            tab_widget = self.session_container.get_tab_widget(session_name)
            if tab_widget:
                tab_widget.tabCloseRequested.connect(self._close_session_tab)
        
        # Focus on the selected group's tab widget (make it active)
        if group_name in self.session_container.multi_view_tabs:
            tab_widget = self.session_container.multi_view_tabs[group_name]
            if tab_widget.count() > 0:
                tab_widget.setCurrentIndex(0)
    
    def _on_session_connection_changed(self, session_name: str):
        """Handle session connection change - update tree view"""
        # Save sessions to ensure connection change is persisted
        self.config_manager.save_sessions(list(self.sessions.values()))
        # Update connection tree to reflect new grouping
        self.connection_tree.update_connections(
            self.connections, 
            self.sessions,
            self.multi_view_groups,
            self.multi_view_active
        )
    
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
                self.log_viewer = LogViewer(self)  # Pass parent to ensure same thread
            self.log_viewer.show()
        else:
            if self.log_viewer:
                self.log_viewer.hide()
    
    def _on_log_entry(self, entry):
        """Handle log entry from transport"""
        if self.log_viewer:
            self.log_viewer.add_entry(entry)
    
    def _on_trace_entry(self, entry):
        """Handle trace entry from transport"""
        self.trace_store.add_entry(entry)
    
    def _on_poll_result(self, session_id: str, result):
        """Handle poll result"""
        if session_id in self.session_tab_widgets:
            self.session_tab_widgets[session_id].update_data(result)
        
        # Register poll result for snapshot manager
        if hasattr(self, 'snapshot_manager'):
            self.snapshot_manager.register_poll_result(session_id, result)
    
    def _on_session_error(self, session_id: str, error_message: str):
        """Handle session error"""
        if session_id in self.session_tab_widgets:
            self.session_tab_widgets[session_id].show_error(error_message)
    
    def _show_help(self):
        """Show help dialog"""
        dialog = HelpDialog(self)
        dialog.exec()
    
    def _show_about(self):
        """Show about dialog"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def _toggle_multi_view(self, checked: bool):
        """Toggle multi-view mode"""
        self.multi_view_active = checked
        
        if checked:
            # Activate multi-view if groups exist
            if self.multi_view_groups:
                # Store all tabs
                tabs_to_move = {}
                for session_name, tab in list(self.session_tab_widgets.items()):
                    tabs_to_move[session_name] = tab
                
                # Clear and set multi-view
                self.session_container.set_single_view()
                for tabs in self.session_container.get_all_tabs():
                    tabs.clear()
                
                self.session_container.set_multi_view(self.multi_view_groups)
                
                # Add all tabs to appropriate groups
                for session_name, tab in tabs_to_move.items():
                    self.session_container.add_session_tab(session_name, tab)
                    tab_widget = self.session_container.get_tab_widget(session_name)
                    if tab_widget:
                        tab_widget.tabCloseRequested.connect(self._close_session_tab)
                
                # Update connection tree to show multi-view groups
                self.connection_tree.update_connections(
                    self.connections, 
                    self.sessions,
                    self.multi_view_groups,
                    self.multi_view_active
                )
            else:
                # No groups, show dialog to create them
                QMessageBox.information(
                    self,
                    "Multi-view",
                    "No groups have been created yet.\n"
                    "Use 'Manage Multi-view...' to create groups."
                )
                self.multi_view_action.setChecked(False)
                self.multi_view_active = False
        else:
            # Deactivate multi-view
            self.session_container.set_single_view()
            # Move all tabs back to single view
            tabs_to_move = {}
            for session_name, tab in list(self.session_tab_widgets.items()):
                tabs_to_move[session_name] = tab
            
            # Clear multi-view tabs
            for tabs in self.session_container.get_all_tabs():
                tabs.clear()
            
            # Add all tabs to single view
            for session_name, tab in tabs_to_move.items():
                self.session_container.add_session_tab(session_name, tab)
                tab_widget = self.session_container.get_tab_widget(session_name)
                if tab_widget:
                    tab_widget.tabCloseRequested.connect(self._close_session_tab)
            
            # Update connection tree
            self.connection_tree.update_connections(
                self.connections, 
                self.sessions,
                self.multi_view_groups,
                self.multi_view_active
            )
    
    def _manage_multi_view(self):
        """Open dialog to manage multi-view groups"""
        session_names = list(self.sessions.keys())
        dialog = MultiViewDialog(session_names, self.multi_view_groups, self)
        if dialog.exec():
            self.multi_view_groups = dialog.get_groups()
            # If multi-view is active, update it
            if self.multi_view_active and self.multi_view_groups:
                # Store all tabs temporarily
                tabs_to_move = {}
                for session_name, tab in list(self.session_tab_widgets.items()):
                    tabs_to_move[session_name] = tab
                
                # Clear container and rebuild
                self.session_container.set_single_view()
                for tabs in self.session_container.get_all_tabs():
                    tabs.clear()
                
                # Set multi-view with new groups
                self.session_container.set_multi_view(self.multi_view_groups)
                
                # Add tabs to appropriate groups
                for session_name, tab in tabs_to_move.items():
                    self.session_container.add_session_tab(session_name, tab)
                    tab_widget = self.session_container.get_tab_widget(session_name)
                    if tab_widget:
                        tab_widget.tabCloseRequested.connect(self._close_session_tab)
            elif self.multi_view_active and not self.multi_view_groups:
                # No groups, disable multi-view
                self.multi_view_action.setChecked(False)
                self._toggle_multi_view(False)
    
    def _show_sessions_together(self, session_name: str, other_session_name: str):
        """Show two sessions together in multi-view"""
        # Create a group for these two sessions
        group_name = f"{session_name} & {other_session_name}"
        self.multi_view_groups[group_name] = [session_name, other_session_name]
        
        # Enable multi-view if not already
        if not self.multi_view_active:
            self.multi_view_action.setChecked(True)
            self._toggle_multi_view(True)
        else:
            # Update multi-view
            self.session_container.set_multi_view(self.multi_view_groups)
            # Rebuild tabs
            tabs_to_move = {}
            for name, tab in list(self.session_tab_widgets.items()):
                self.session_container.remove_session_tab(name)
                tabs_to_move[name] = tab
            
            for name, tab in tabs_to_move.items():
                self.session_container.add_session_tab(name, tab)
                tab_widget = self.session_container.get_tab_widget(name)
                if tab_widget:
                    tab_widget.tabCloseRequested.connect(self._close_session_tab)
    
    def _show_frame_analyzer(self):
        """Show frame analyzer dialog"""
        dialog = FrameAnalyzerDialog(self, self.trace_store)
        dialog.exec()
    
    def _show_simulator_dialog(self):
        """Show simulator configuration dialog"""
        dialog = SimulatorDialog(self, self.simulator_manager)
        dialog.exec()
    
    def _take_snapshot(self):
        """Take snapshot"""
        from src.ui.snapshot_dialog import SnapshotDialog
        
        # Get current session if any tab is selected
        current_session = None
        if self.session_container.single_view.currentWidget():
            current_tab = self.session_container.single_view.currentWidget()
            if isinstance(current_tab, SessionTab):
                current_session = current_tab.session
        
        all_sessions = list(self.sessions.values())
        
        dialog = SnapshotDialog(
            self,
            self.snapshot_manager,
            current_session,
            all_sessions
        )
        
        if dialog.exec():
            snapshot = dialog.get_snapshot()
            if snapshot:
                if self.snapshot_store.save_snapshot(snapshot):
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Snapshot '{snapshot.name}' gemt."
                    )
                else:
                    QMessageBox.warning(self, "Error", "Kunne ikke gemme snapshot.")
    
    def _manage_snapshots(self):
        """Manage snapshots"""
        from src.ui.snapshot_manager_dialog import SnapshotManagerDialog
        
        dialog = SnapshotManagerDialog(self, self.snapshot_store)
        dialog.exec()
    
    def _show_device_templates(self):
        """Show device templates manager dialog"""
        dialog = TemplateManagerDialog(self, self.template_library)
        dialog.exec()
    
    def _show_device_scanner(self):
        """Show device scanner dialog (RTU and TCP)"""
        dialog = DeviceScannerDialog(
            self,
            import_connection_callback=self._import_connection_from_scanner,
            import_session_callback=self._import_session_from_scanner
        )
        dialog.exec()
    
    def _import_connection_from_scanner(self, *args, **kwargs):
        """Import connection from scanner - handles both TCP and RTU"""
        # Check if it's TCP (2 args: ip_address, port) or RTU (5 args: port, baudrate, parity, stopbits, bytesize)
        if len(args) == 2:
            # TCP connection
            ip_address, port = args
            connection_name = f"TCP_{ip_address}_{port}"
            counter = 1
            while any(c.name == connection_name for c in self.connections):
                connection_name = f"TCP_{ip_address}_{port}_{counter}"
                counter += 1
            
            profile = ConnectionProfile(
                name=connection_name,
                connection_type=ConnectionType.TCP,
                host=ip_address,
                port=port,
                timeout=3.0,
                retries=3
            )
        elif len(args) == 5:
            # RTU connection
            port, baudrate, parity, stopbits, bytesize = args
            connection_name = f"RTU_{port}"
            counter = 1
            while any(c.name == connection_name for c in self.connections):
                connection_name = f"RTU_{port}_{counter}"
                counter += 1
            
            profile = ConnectionProfile(
                name=connection_name,
                connection_type=ConnectionType.RTU,
                port_name=port,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=3.0,
                retries=3
            )
        else:
            QMessageBox.warning(self, "Import Error", "Invalid parameters for connection import.")
            return
        
        # Add connection
        self.connections.append(profile)
        self.session_manager.add_connection(profile)
        self.config_manager.save_connections(self.connections)
        self.connection_tree.update_connections(
            self.connections, 
            self.sessions,
            self.multi_view_groups,
            self.multi_view_active
        )
        
        QMessageBox.information(
            self, 
            "Connection Imported", 
            f"Connection '{profile.name}' has been imported successfully."
        )
    
    def _import_session_from_scanner(self, device_info, *args):
        """Import session from scanner device info - handles both TCP and RTU"""
        # Check if it's TCP or RTU device info
        if isinstance(device_info, TcpDeviceInfo):
            # TCP device
            connection_name = f"TCP_{device_info.ip_address}_{device_info.port}"
            connection = next((c for c in self.connections if c.name == connection_name), None)
            
            if not connection:
                counter = 1
                while any(c.name == connection_name for c in self.connections):
                    connection_name = f"TCP_{device_info.ip_address}_{device_info.port}_{counter}"
                    counter += 1
                
                connection = ConnectionProfile(
                    name=connection_name,
                    connection_type=ConnectionType.TCP,
                    host=device_info.ip_address,
                    port=device_info.port,
                    timeout=3.0,
                    retries=3
                )
                
                self.connections.append(connection)
                self.session_manager.add_connection(connection)
                self.config_manager.save_connections(self.connections)
            
            device_id = device_info.device_id
            
            # Determine which register type to use
            if device_info.has_holding_registers and device_info.holding_register_addresses:
                function_code = FunctionCode.READ_HOLDING_REGISTERS
                addresses = device_info.holding_register_addresses
                register_type = "Holding Registers"
            elif device_info.has_input_registers and device_info.input_register_addresses:
                function_code = FunctionCode.READ_INPUT_REGISTERS
                addresses = device_info.input_register_addresses
                register_type = "Input Registers"
            elif device_info.has_coils and device_info.coil_addresses:
                function_code = FunctionCode.READ_COILS
                addresses = device_info.coil_addresses
                register_type = "Coils"
            elif device_info.has_discrete_inputs and device_info.discrete_input_addresses:
                function_code = FunctionCode.READ_DISCRETE_INPUTS
                addresses = device_info.discrete_input_addresses
                register_type = "Discrete Inputs"
            else:
                QMessageBox.warning(self, "Import Error", "No active registers found to import.")
                return
                
        elif isinstance(device_info, DeviceInfo) and len(args) == 5:
            # RTU device
            port, baudrate, parity, stopbits, bytesize = args
            connection_name = f"RTU_{port}"
            connection = next((c for c in self.connections if c.name == connection_name), None)
            
            if not connection:
                counter = 1
                while any(c.name == connection_name for c in self.connections):
                    connection_name = f"RTU_{port}_{counter}"
                    counter += 1
                
                connection = ConnectionProfile(
                    name=connection_name,
                    connection_type=ConnectionType.RTU,
                    port_name=port,
                    baudrate=baudrate,
                    parity=parity,
                    stopbits=stopbits,
                    bytesize=bytesize,
                    timeout=3.0,
                    retries=3
                )
                
                self.connections.append(connection)
                self.session_manager.add_connection(connection)
                self.config_manager.save_connections(self.connections)
            
            device_id = device_info.device_id
            
            # Determine which register type to use
            if device_info.has_holding_registers and device_info.holding_register_addresses:
                function_code = FunctionCode.READ_HOLDING_REGISTERS
                addresses = device_info.holding_register_addresses
                register_type = "Holding Registers"
            elif device_info.has_input_registers and device_info.input_register_addresses:
                function_code = FunctionCode.READ_INPUT_REGISTERS
                addresses = device_info.input_register_addresses
                register_type = "Input Registers"
            elif device_info.has_coils and device_info.coil_addresses:
                function_code = FunctionCode.READ_COILS
                addresses = device_info.coil_addresses
                register_type = "Coils"
            elif device_info.has_discrete_inputs and device_info.discrete_input_addresses:
                function_code = FunctionCode.READ_DISCRETE_INPUTS
                addresses = device_info.discrete_input_addresses
                register_type = "Discrete Inputs"
            else:
                QMessageBox.warning(self, "Import Error", "No active registers found to import.")
                return
        else:
            QMessageBox.warning(self, "Import Error", "Invalid parameters for session import.")
            return
        
        # Calculate start address and quantity
        start_address = min(addresses)
        max_address = max(addresses)
        quantity = max_address - start_address + 1
        
        # Generate session name
        session_name = f"{connection.name}_Device{device_id}_{register_type}"
        counter = 1
        while session_name in self.sessions:
            session_name = f"{connection.name}_Device{device_id}_{register_type}_{counter}"
            counter += 1
        
        # Create session
        session = SessionDefinition(
            name=session_name,
            connection_profile_name=connection.name,
            slave_id=device_id,
            function_code=function_code,
            start_address=start_address,
            quantity=quantity,
            poll_interval_ms=1000
        )
        
        # Add session
        self.sessions[session.name] = session
        self.session_manager.add_session(session)
        self.config_manager.save_sessions(list(self.sessions.values()))
        self._create_session_tab(session)
        self.connection_tree.update_connections(
            self.connections, 
            self.sessions,
            self.multi_view_groups,
            self.multi_view_active
        )
        
        QMessageBox.information(
            self, 
            "Session Imported", 
            f"Session '{session_name}' has been imported successfully.\n"
            f"Reading {register_type} from address {start_address} to {max_address}."
        )
    
    def closeEvent(self, event):
        """Handle window close"""
        # Save UI settings
        self._save_ui_settings()
        
        # Save configuration
        self.config_manager.save_connections(self.connections)
        self.config_manager.save_sessions(list(self.sessions.values()))
        
        # Stop polling
        self.polling_engine.stop()
        
        # Stop simulators
        if self.simulator_manager.is_tcp_running():
            self.simulator_manager.stop_tcp_simulator()
        if self.simulator_manager.is_rtu_running():
            self.simulator_manager.stop_rtu_simulator()
        
        # Disconnect all
        for conn in self.connections:
            self.session_manager.disconnect(conn.name)
        
        event.accept()
