"""Data table widget for displaying Modbus data"""
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from src.models.poll_result import PollResult
from typing import List, Dict, Any


class DataTable(QTableWidget):
    """Table widget for displaying Modbus register/coil data"""
    
    def __init__(self):
        """Initialize data table"""
        super().__init__()
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels([
            "Address", "Name", "Raw Value", "HEX", "Scaled Value", "Unit", "Status"
        ])
        self.setAlternatingRowColors(True)
        self.setEditTriggers(QTableWidget.EditTrigger.DoubleClicked)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setShowGrid(True)
        
        # Set column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        self.setColumnWidth(0, 80)   # Adresse
        self.setColumnWidth(1, 150)  # Navn
        self.setColumnWidth(2, 100)  # Rå værdi
        self.setColumnWidth(3, 100)  # HEX
        self.setColumnWidth(4, 120)  # Skaleret værdi
        self.setColumnWidth(5, 80)   # Enhed
        # Status column stretches
    
    def update_data(self, result: PollResult):
        """Update table with poll result"""
        self.setRowCount(len(result.decoded_values))
        
        for row, value_data in enumerate(result.decoded_values):
            if isinstance(value_data, dict):
                is_separator = value_data.get("is_separator", False)
                is_tag = value_data.get("is_tag", False)
                
                # Address
                addr_item = QTableWidgetItem(str(value_data.get("address", "")))
                addr_item.setFlags(addr_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    addr_item.setBackground(Qt.GlobalColor.darkGray)
                    addr_item.setForeground(Qt.GlobalColor.black)
                self.setItem(row, 0, addr_item)
                
                # Name
                name_item = QTableWidgetItem(str(value_data.get("name", "")))
                name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    name_item.setBackground(Qt.GlobalColor.darkGray)
                    name_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                    name_item.setForeground(Qt.GlobalColor.black)
                elif is_tag:
                    name_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                self.setItem(row, 1, name_item)
                
                # Raw value
                raw_value = value_data.get("raw", "")
                raw_item = QTableWidgetItem(str(raw_value))
                raw_item.setFlags(raw_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    raw_item.setBackground(Qt.GlobalColor.darkGray)
                    raw_item.setForeground(Qt.GlobalColor.black)
                self.setItem(row, 2, raw_item)
                
                # HEX value
                hex_value = ""
                try:
                    if isinstance(raw_value, (int, float)):
                        # Convert to integer and format as HEX
                        int_val = int(raw_value)
                        if int_val >= 0:
                            hex_value = f"0x{int_val:X}"
                        else:
                            # For negative values, show as signed hex
                            hex_value = f"-0x{abs(int_val):X}"
                    elif isinstance(raw_value, bool):
                        hex_value = "0x01" if raw_value else "0x00"
                    else:
                        # Try to convert string to int
                        try:
                            int_val = int(float(str(raw_value)))
                            hex_value = f"0x{int_val:X}" if int_val >= 0 else f"-0x{abs(int_val):X}"
                        except (ValueError, TypeError):
                            hex_value = ""
                except (ValueError, TypeError):
                    hex_value = ""
                
                hex_item = QTableWidgetItem(hex_value)
                hex_item.setFlags(hex_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    hex_item.setBackground(Qt.GlobalColor.darkGray)
                    hex_item.setForeground(Qt.GlobalColor.black)
                else:
                    hex_item.setForeground(Qt.GlobalColor.darkBlue)
                self.setItem(row, 3, hex_item)
                
                # Scaled value
                scaled = value_data.get("scaled", "")
                scaled_item = QTableWidgetItem(f"{scaled:.2f}" if isinstance(scaled, (int, float)) else str(scaled))
                scaled_item.setFlags(scaled_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    scaled_item.setBackground(Qt.GlobalColor.darkGray)
                    scaled_item.setForeground(Qt.GlobalColor.black)
                self.setItem(row, 4, scaled_item)
                
                # Unit
                unit_item = QTableWidgetItem(str(value_data.get("unit", "")))
                unit_item.setFlags(unit_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    unit_item.setBackground(Qt.GlobalColor.darkGray)
                    unit_item.setForeground(Qt.GlobalColor.black)
                self.setItem(row, 5, unit_item)
                
                # Status
                status_item = QTableWidgetItem(result.status.value)
                status_item.setFlags(status_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                if is_separator:
                    status_item.setBackground(Qt.GlobalColor.darkGray)
                    status_item.setForeground(Qt.GlobalColor.black)
                else:
                    if result.status.value == "OK":
                        status_item.setForeground(Qt.GlobalColor.green)
                    else:
                        status_item.setForeground(Qt.GlobalColor.red)
                self.setItem(row, 6, status_item)
        
        self.resizeColumnsToContents()
