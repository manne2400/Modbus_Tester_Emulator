"""Centralized theme styling for the application"""
from typing import Optional


class Theme:
    """Centralized theme class for consistent styling across the application"""
    
    # Standard spacing constants
    MARGIN_STANDARD = 10
    MARGIN_COMPACT = 5
    SPACING_STANDARD = 10
    SPACING_COMPACT = 5
    SPACING_FORM = 8
    
    @staticmethod
    def get_stylesheet() -> str:
        """Returns complete dark theme stylesheet for the application"""
        return """
            /* Main Windows and Dialogs */
            QMainWindow, QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            
            /* Menu Bar */
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
            
            /* Menus */
            QMenu {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
            }
            QMenu::item:selected {
                background-color: #094771;
            }
            
            /* Tool Bar */
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
            
            /* Status Bar */
            QStatusBar {
                background-color: #252526;
                border-top: 1px solid #3e3e42;
                color: #cccccc;
            }
            
            /* Tab Widget */
            QTabWidget {
                background-color: #1e1e1e;
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
            
            /* Buttons */
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
            
            /* Status-based button styling (for start/stop buttons) */
            QPushButton[status="running"] {
                background-color: #d32f2f;
            }
            QPushButton[status="running"]:hover {
                background-color: #f44336;
            }
            QPushButton[status="running"]:pressed {
                background-color: #b71c1c;
            }
            
            /* Tree Widget */
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
            
            /* Table Widget */
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
            
            /* Header View */
            QHeaderView::section {
                background-color: #2d2d30;
                padding: 6px;
                border: none;
                border-bottom: 2px solid #3e3e42;
                font-weight: 600;
                color: #cccccc;
            }
            
            /* Combo Box */
            QComboBox {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px 8px;
                padding-right: 30px;
                min-width: 120px;
                color: #cccccc;
            }
            QComboBox:hover {
                border-color: #007acc;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
                background-color: #2d2d30;
                border-left: 1px solid #3e3e42;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }
            QComboBox::drop-down:hover {
                background-color: #37373d;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #cccccc;
                width: 0px;
                height: 0px;
            }
            QComboBox::down-arrow:hover {
                border-top-color: #ffffff;
            }
            QComboBox QAbstractItemView {
                background-color: #252526;
                border: 1px solid #3e3e42;
                color: #cccccc;
                selection-background-color: #094771;
            }
            
            /* Spin Box */
            QSpinBox, QDoubleSpinBox {
                background-color: #3c3c3c;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                padding: 4px;
                min-width: 80px;
                color: #cccccc;
            }
            QSpinBox:hover, QDoubleSpinBox:hover {
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
            
            /* Line Edit */
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
            
            /* Form Layout */
            QFormLayout {
                spacing: 8px;
            }
            
            /* Group Box */
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
            
            /* Label */
            QLabel {
                color: #cccccc;
            }
            
            /* Text Edit and Text Browser */
            QTextEdit, QTextBrowser {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                color: #cccccc;
            }
            
            /* Progress Bar */
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
            
            /* List Widget */
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
            
            /* Splitter */
            QSplitter::handle {
                background-color: #3e3e42;
            }
            QSplitter::handle:horizontal {
                width: 3px;
            }
            QSplitter::handle:vertical {
                height: 3px;
            }
            
            /* Message Box */
            QMessageBox QLabel {
                color: #000000;
                background-color: #ffffff;
                padding: 10px;
            }
        """
    
    @staticmethod
    def apply_to_widget(widget) -> None:
        """Apply theme stylesheet to a widget"""
        widget.setStyleSheet(Theme.get_stylesheet())

