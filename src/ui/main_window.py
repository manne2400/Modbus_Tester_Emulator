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
from src.ui.rtu_scanner_dialog import RtuScannerDialog
from src.application.simulator_manager import SimulatorManager
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
        
        # Apply professional styling
        self._apply_styling()
        
        # Initialize managers
        self.config_manager = ConfigManager()
        self.project_manager = ProjectManager(self.config_manager)
        self.session_manager = SessionManager()
        self.polling_engine = PollingEngine(self.session_manager)
        self.simulator_manager = SimulatorManager()
        
        # Connect polling engine signals
        self.polling_engine.poll_result.connect(self._on_poll_result)
        self.polling_engine.session_error.connect(self._on_session_error)
        
        # Set log callback
        self.log_viewer = None
        self.session_manager.set_log_callback(self._on_log_entry)
        
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
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Splitter
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.main_splitter)
        
        # Left side: Connection tree in GroupBox
        connections_group = QGroupBox("Connections")
        connections_layout = QVBoxLayout()
        connections_layout.setContentsMargins(5, 5, 5, 5)
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
        sessions_layout.setContentsMargins(5, 5, 5, 5)
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
        
        rtu_scanner_action = QAction("RTU Device Scanner...", self)
        rtu_scanner_action.triggered.connect(self._show_rtu_scanner)
        connection_menu.addAction(rtu_scanner_action)
        
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
        
        view_menu.addSeparator()
        
        simulator_action = QAction("Modbus Simulator...", self)
        simulator_action.triggered.connect(self._show_simulator_dialog)
        view_menu.addAction(simulator_action)
        
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
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QMenuBar {
                background-color: #252526;
                border-bottom: 1px solid #3e3e42;
                padding: 2px;
                color: #cccccc;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QMenuBar::item:selected {
                background-color: #2a2d2e;
            }
            QMenuBar::item:pressed {
                background-color: #37373d;
            }
            QMenu {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            QToolBar {
                background-color: #252526;
                border: none;
                border-bottom: 1px solid #3e3e42;
                spacing: 3px;
                padding: 3px;
            }
            QToolBar::separator {
                background-color: #3e3e42;
                width: 1px;
                margin: 3px;
            }
            QStatusBar {
                background-color: #252526;
                border-top: 1px solid #3e3e42;
                color: #cccccc;
            }
            QTabWidget::pane {
                border: 1px solid #3e3e42;
                background-color: #1e1e1e;
                border-radius: 3px;
            }
            QTabBar::tab {
                background-color: #2d2d30;
                color: #cccccc;
                padding: 6px 12px;
                margin-right: 2px;
                border-top-left-radius: 3px;
                border-top-right-radius: 3px;
            }
            QTabBar::tab:selected {
                background-color: #1e1e1e;
                border-bottom: 2px solid #007acc;
                color: #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #37373d;
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
            QTreeWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                alternate-background-color: #2d2d30;
                color: #cccccc;
            }
            QTreeWidget::item {
                padding: 3px;
                color: #cccccc;
            }
            QTreeWidget::item:selected {
                background-color: #094771;
                color: white;
            }
            QTreeWidget::item:has-children {
                font-weight: 600;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                gridline-color: #3e3e42;
                alternate-background-color: #2d2d30;
                color: #cccccc;
            }
            QTableWidget::item {
                padding: 4px;
                color: #cccccc;
            }
            QTableWidget::item:selected {
                background-color: #094771;
                color: white;
            }
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #3e3e42;
                font-weight: 600;
                color: #cccccc;
            }
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px 8px;
                min-width: 120px;
                color: #cccccc;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
                selection-background-color: #094771;
            }
            QSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px;
                min-width: 80px;
                color: #cccccc;
            }
            QSpinBox:hover {
                border-color: #007acc;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #2d2d30;
                border: 1px solid #3e3e42;
                border-radius: 2px;
                width: 16px;
            }
            QSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                border-top-right-radius: 3px;
            }
            QSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                border-bottom-right-radius: 3px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #37373d;
            }
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {
                background-color: #094771;
            }
            QSpinBox::up-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 5px solid #cccccc;
                width: 0px;
                height: 0px;
            }
            QSpinBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cccccc;
                width: 0px;
                height: 0px;
            }
            QSpinBox::up-button:hover QSpinBox::up-arrow {
                border-bottom-color: #ffffff;
            }
            QSpinBox::down-button:hover QSpinBox::down-arrow {
                border-top-color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px 8px;
                color: #cccccc;
            }
            QLineEdit:hover {
                border-color: #007acc;
            }
            QLineEdit:focus {
                border: 2px solid #007acc;
            }
            QFormLayout {
                spacing: 8px;
            }
            QGroupBox {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                margin-top: 10px;
                padding-top: 10px;
                color: #cccccc;
                font-weight: 500;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QLabel {
                color: #cccccc;
            }
            QTextEdit, QTextBrowser {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                color: #cccccc;
            }
            QProgressBar {
                border: 1px solid #3e3e42;
                border-radius: 3px;
                text-align: center;
                color: #cccccc;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 2px;
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
            QSplitter::handle {
                background-color: #3e3e42;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:vertical {
                height: 3px;
            }
            QMessageBox QLabel {
                color: #000000;
            }
        """)
    
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
        tab = SessionTab(session, self.connections, self.session_manager, self.polling_engine, self.config_manager)
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
    
    def _on_poll_result(self, session_id: str, result):
        """Handle poll result"""
        if session_id in self.session_tab_widgets:
            self.session_tab_widgets[session_id].update_data(result)
    
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
    
    def _show_simulator_dialog(self):
        """Show simulator configuration dialog"""
        dialog = SimulatorDialog(self, self.simulator_manager)
        dialog.exec()
    
    def _show_rtu_scanner(self):
        """Show RTU device scanner dialog"""
        dialog = RtuScannerDialog(self)
        dialog.exec()
    
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
