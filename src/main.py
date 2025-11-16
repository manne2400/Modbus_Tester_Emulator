"""Main entry point for Modbus Tester application"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.utils.logger import setup_logging


def main():
    """Application entry point"""
    setup_logging()
    
    app = QApplication(sys.argv)
    app.setApplicationName("Modbus Tester")
    app.setOrganizationName("Modbus Tester")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
