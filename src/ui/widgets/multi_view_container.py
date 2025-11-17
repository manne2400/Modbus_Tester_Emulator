"""Multi-view container for displaying multiple sessions simultaneously"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QTabWidget, QMenu
from PyQt6.QtCore import Qt, pyqtSignal
from src.ui.session_tab import SessionTab
from typing import Dict, List, Optional


class MultiViewContainer(QWidget):
    """Container widget that can display sessions in single or multi-view mode"""
    
    # Signal emitted when a session should be shown in multi-view
    show_with_session = pyqtSignal(str, str)  # session_name, other_session_name
    
    def __init__(self):
        """Initialize multi-view container"""
        super().__init__()
        self.single_view = QTabWidget()
        self.single_view.setTabsClosable(True)
        
        self.multi_view_splitter: Optional[QSplitter] = None
        self.multi_view_tabs: Dict[str, QTabWidget] = {}  # group_name -> QTabWidget
        self.session_groups: Dict[str, str] = {}  # session_name -> group_name
        
        self.current_mode = "single"  # "single" or "multi"
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.single_view)
    
    def add_session_tab(self, session_name: str, tab: SessionTab):
        """Add a session tab"""
        if self.current_mode == "single":
            self.single_view.addTab(tab, session_name)
        else:
            # Add to appropriate group in multi-view
            group_name = self.session_groups.get(session_name, "default")
            if group_name in self.multi_view_tabs:
                self.multi_view_tabs[group_name].addTab(tab, session_name)
    
    def remove_session_tab(self, session_name: str):
        """Remove a session tab"""
        if self.current_mode == "single":
            # Find and remove from single view
            for i in range(self.single_view.count()):
                if self.single_view.tabText(i) == session_name:
                    self.single_view.removeTab(i)
                    break
        else:
            # Remove from multi-view
            group_name = self.session_groups.get(session_name)
            if group_name and group_name in self.multi_view_tabs:
                tabs_widget = self.multi_view_tabs[group_name]
                for i in range(tabs_widget.count()):
                    if tabs_widget.tabText(i) == session_name:
                        tabs_widget.removeTab(i)
                        break
                # If group is empty, remove it (but only if we're in multi-view mode)
                if tabs_widget.count() == 0 and self.current_mode == "multi":
                    self._remove_group(group_name)
            if session_name in self.session_groups:
                del self.session_groups[session_name]
    
    def set_multi_view(self, session_groups: Dict[str, List[str]]):
        """Set multi-view mode with session groups
        
        Args:
            session_groups: Dict mapping group names to lists of session names
        """
        self.current_mode = "multi"
        
        # Clear single view
        self.single_view.hide()
        
        # Remove old splitter if it exists
        if self.multi_view_splitter:
            layout = self.layout()
            layout.removeWidget(self.multi_view_splitter)
            self.multi_view_splitter.hide()
            self.multi_view_splitter.deleteLater()
            self.multi_view_splitter = None
        
        # Create new splitter for multi-view
        self.multi_view_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.multi_view_tabs.clear()
        self.session_groups.clear()
        
        # Create tab widget for each group
        for group_name, session_names in session_groups.items():
            tabs_widget = QTabWidget()
            tabs_widget.setTabsClosable(True)
            self.multi_view_tabs[group_name] = tabs_widget
            self.multi_view_splitter.addWidget(tabs_widget)
            
            # Map sessions to groups
            for session_name in session_names:
                self.session_groups[session_name] = group_name
        
        # Set equal sizes
        if len(session_groups) > 0:
            sizes = [1000] * len(session_groups)
            self.multi_view_splitter.setSizes(sizes)
        
        # Add splitter to layout
        layout = self.layout()
        layout.addWidget(self.multi_view_splitter)
        self.multi_view_splitter.show()
    
    def set_single_view(self):
        """Set single view mode"""
        self.current_mode = "single"
        
        # Hide multi-view
        if self.multi_view_splitter:
            self.multi_view_splitter.hide()
        
        # Show single view
        self.single_view.show()
        
        # Clear multi-view data
        self.multi_view_tabs.clear()
        self.session_groups.clear()
    
    def _remove_group(self, group_name: str):
        """Remove a group from multi-view"""
        if group_name in self.multi_view_tabs and self.multi_view_splitter:
            tabs_widget = self.multi_view_tabs[group_name]
            # Find index of widget in splitter
            for i in range(self.multi_view_splitter.count()):
                if self.multi_view_splitter.widget(i) == tabs_widget:
                    # Hide and delete the widget
                    tabs_widget.hide()
                    tabs_widget.setParent(None)
                    tabs_widget.deleteLater()
                    break
            del self.multi_view_tabs[group_name]
    
    def get_tab_widget(self, session_name: str) -> Optional[QTabWidget]:
        """Get the tab widget containing a session"""
        if self.current_mode == "single":
            return self.single_view
        else:
            group_name = self.session_groups.get(session_name)
            if group_name and group_name in self.multi_view_tabs:
                return self.multi_view_tabs[group_name]
        return None
    
    def connect_tab_close(self, handler):
        """Connect tab close handler"""
        self.single_view.tabCloseRequested.connect(handler)
        # Also connect to multi-view tabs
        for tabs_widget in self.multi_view_tabs.values():
            tabs_widget.tabCloseRequested.connect(handler)
    
    def get_all_tabs(self) -> List[QTabWidget]:
        """Get all tab widgets"""
        tabs = [self.single_view]
        tabs.extend(self.multi_view_tabs.values())
        return tabs

