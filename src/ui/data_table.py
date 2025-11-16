"""Data table widget for displaying Modbus data"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from src.models.poll_result import PollResult
from typing import List, Dict, Any


class DataTable(QTableWidget):
    """Table widget for displaying Modbus register/coil data"""
    
    def __init__(self):
        """Initialize data table"""
        super().__init__()
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "Adresse", "Navn", "Rå værdi", "Skaleret værdi", "Enhed", "Status"
        ])
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.verticalHeader().setVisible(False)
    
    def update_data(self, result: PollResult):
        """Update table with poll result"""
        self.setRowCount(len(result.decoded_values))
        
        for row, value_data in enumerate(result.decoded_values):
            if isinstance(value_data, dict):
                # Address
                addr_item = QTableWidgetItem(str(value_data.get("address", "")))
                addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, 0, addr_item)
                
                # Name
                name_item = QTableWidgetItem(str(value_data.get("name", "")))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, 1, name_item)
                
                # Raw value
                raw_item = QTableWidgetItem(str(value_data.get("raw", "")))
                raw_item.setFlags(raw_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, 2, raw_item)
                
                # Scaled value
                scaled = value_data.get("scaled", "")
                scaled_item = QTableWidgetItem(f"{scaled:.2f}" if isinstance(scaled, (int, float)) else str(scaled))
                scaled_item.setFlags(scaled_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, 3, scaled_item)
                
                # Unit
                unit_item = QTableWidgetItem(str(value_data.get("unit", "")))
                unit_item.setFlags(unit_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.setItem(row, 4, unit_item)
                
                # Status
                status_item = QTableWidgetItem(result.status.value)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if result.status.value == "OK":
                    status_item.setForeground(Qt.GlobalColor.green)
                else:
                    status_item.setForeground(Qt.GlobalColor.red)
                self.setItem(row, 5, status_item)
        
        self.resizeColumnsToContents()
