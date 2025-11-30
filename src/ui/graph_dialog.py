"""Graph dialog for visualizing Modbus data over time"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QPushButton, QCheckBox, QDoubleSpinBox, QSpinBox,
    QGroupBox, QListWidget, QListWidgetItem, QWidget, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from src.models.poll_result import PollResult
from src.ui.styles.theme import Theme
import colorsys


class GraphDialog(QDialog):
    """Dialog for displaying time-series graphs of Modbus data"""
    
    def __init__(self, parent=None, session_id: str = ""):
        """Initialize graph dialog"""
        super().__init__(parent)
        self.session_id = session_id
        self.setWindowTitle(f"Graph - {session_id}" if session_id else "Graph")
        self.setMinimumSize(1000, 600)
        
        # Apply theme
        Theme.apply_to_widget(self)
        
        # Data storage: key is row_key (f"{address}_{name}"), value is dict with timestamps and values
        self.data_history: Dict[str, Dict[str, Any]] = {}
        self.tracked_rows: Dict[str, Dict[str, Any]] = {}  # row_key -> row_data
        
        # Color palette for different lines
        self.color_palette = self._generate_color_palette(20)
        self.color_index = 0
        
        # Axis settings
        self.x_auto_scale = True
        self.y_auto_scale = True
        self.x_min_time = None  # datetime or None
        self.x_max_time = None  # datetime or None
        self.y_min_value = None  # float or None
        self.y_max_value = None  # float or None
        self.x_window_seconds = 60  # Default: show last 60 seconds
        
        # Setup UI
        self._setup_ui()
        
        # Set dark theme for matplotlib
        plt.style.use('dark_background')
    
    def _generate_color_palette(self, n: int) -> List[str]:
        """Generate a color palette with n distinct colors"""
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.8
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(f"#{int(rgb[0]*255):02x}{int(rgb[1]*255):02x}{int(rgb[2]*255):02x}")
        return colors
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setSpacing(Theme.SPACING_STANDARD)
        layout.setContentsMargins(Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD)
        
        # Splitter for main content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        layout.addWidget(splitter)
        
        # Left side: Controls panel
        controls_widget = QWidget()
        controls_widget.setMaximumWidth(300)
        controls_layout = QVBoxLayout(controls_widget)
        controls_layout.setSpacing(Theme.SPACING_STANDARD)
        controls_layout.setContentsMargins(Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT, Theme.MARGIN_COMPACT)
        
        # Tracked rows list
        rows_group = QGroupBox("Tracked Rows")
        rows_layout = QVBoxLayout()
        self.rows_list = QListWidget()
        self.rows_list.setAlternatingRowColors(True)
        rows_layout.addWidget(self.rows_list)
        rows_group.setLayout(rows_layout)
        controls_layout.addWidget(rows_group)
        
        # X-axis settings
        x_axis_group = QGroupBox("X-Axis (Time)")
        x_axis_layout = QFormLayout()
        x_axis_layout.setSpacing(Theme.SPACING_FORM)
        
        self.x_auto_checkbox = QCheckBox("Auto-scale")
        self.x_auto_checkbox.setChecked(True)
        self.x_auto_checkbox.toggled.connect(self._on_x_auto_changed)
        x_axis_layout.addRow(self.x_auto_checkbox)
        
        self.x_window_spin = QSpinBox()
        self.x_window_spin.setRange(10, 3600)
        self.x_window_spin.setValue(60)
        self.x_window_spin.setSuffix(" seconds")
        self.x_window_spin.valueChanged.connect(self._on_x_window_changed)
        x_axis_layout.addRow("Window:", self.x_window_spin)
        
        x_axis_group.setLayout(x_axis_layout)
        controls_layout.addWidget(x_axis_group)
        
        # Y-axis settings
        y_axis_group = QGroupBox("Y-Axis (Value)")
        y_axis_layout = QFormLayout()
        y_axis_layout.setSpacing(Theme.SPACING_FORM)
        
        self.y_auto_checkbox = QCheckBox("Auto-scale")
        self.y_auto_checkbox.setChecked(True)
        self.y_auto_checkbox.toggled.connect(self._on_y_auto_changed)
        y_axis_layout.addRow(self.y_auto_checkbox)
        
        self.y_min_spin = QDoubleSpinBox()
        self.y_min_spin.setRange(-1e10, 1e10)
        self.y_min_spin.setDecimals(2)
        self.y_min_spin.setEnabled(False)
        self.y_min_spin.valueChanged.connect(self._on_y_limits_changed)
        y_axis_layout.addRow("Min:", self.y_min_spin)
        
        self.y_max_spin = QDoubleSpinBox()
        self.y_max_spin.setRange(-1e10, 1e10)
        self.y_max_spin.setDecimals(2)
        self.y_max_spin.setEnabled(False)
        self.y_max_spin.valueChanged.connect(self._on_y_limits_changed)
        y_axis_layout.addRow("Max:", self.y_max_spin)
        
        y_axis_group.setLayout(y_axis_layout)
        controls_layout.addWidget(y_axis_group)
        
        # Buttons
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(Theme.SPACING_COMPACT)
        
        self.clear_btn = QPushButton("Clear History")
        self.clear_btn.clicked.connect(self._clear_history)
        buttons_layout.addWidget(self.clear_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        buttons_layout.addWidget(self.close_btn)
        
        controls_layout.addStretch()
        controls_layout.addLayout(buttons_layout)
        
        splitter.addWidget(controls_widget)
        
        # Right side: Graph
        graph_widget = QWidget()
        graph_layout = QVBoxLayout(graph_widget)
        graph_layout.setContentsMargins(0, 0, 0, 0)
        
        # Matplotlib figure
        self.figure = Figure(figsize=(10, 6), facecolor='#1e1e1e')
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='#cccccc')
        self.ax.spines['bottom'].set_color('#cccccc')
        self.ax.spines['top'].set_color('#cccccc')
        self.ax.spines['right'].set_color('#cccccc')
        self.ax.spines['left'].set_color('#cccccc')
        self.ax.xaxis.label.set_color('#cccccc')
        self.ax.yaxis.label.set_color('#cccccc')
        self.ax.title.set_color('#cccccc')
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Scaled Value")
        self.ax.set_title("Modbus Data Over Time")
        self.ax.grid(True, alpha=0.3, color='#3e3e42')
        
        graph_layout.addWidget(self.canvas)
        splitter.addWidget(graph_widget)
        
        # Set splitter stretch factors
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([300, 700])
    
    def set_tracked_rows(self, row_data_list: List[Dict[str, Any]]):
        """Set which rows to track from the data table
        
        Args:
            row_data_list: List of dicts with keys: address, name, raw, scaled, unit, is_tag, is_separator
        """
        # Clear existing tracked rows
        self.tracked_rows.clear()
        self.data_history.clear()
        self.rows_list.clear()
        self.color_index = 0
        
        # Filter out separators and invalid rows
        valid_rows = [row for row in row_data_list 
                     if not row.get("is_separator", False) 
                     and row.get("address") != "" 
                     and row.get("scaled") != ""]
        
        # Add valid rows
        for row_data in valid_rows:
            address = row_data.get("address", "")
            name = row_data.get("name", "")
            row_key = f"{address}_{name}"
            
            # Create tracked row entry
            self.tracked_rows[row_key] = {
                "address": address,
                "name": name,
                "unit": row_data.get("unit", ""),
                "color": self.color_palette[self.color_index % len(self.color_palette)]
            }
            self.color_index += 1
            
            # Initialize data history
            self.data_history[row_key] = {
                "timestamps": [],
                "values": [],
                "label": f"Addr {address} - {name}",
                "color": self.tracked_rows[row_key]["color"]
            }
            
            # Add to list widget
            item_text = f"Addr {address}: {name}"
            if row_data.get("unit"):
                item_text += f" ({row_data.get('unit')})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, row_key)
            self.rows_list.addItem(item)
        
        # Update graph
        self._update_graph()
    
    def add_data_point(self, poll_result: PollResult):
        """Add a new data point from a poll result
        
        Args:
            poll_result: PollResult containing new data
        """
        if poll_result.status.value != "OK":
            return  # Only plot successful polls
        
        # Extract data for each tracked row
        for row_key, tracked_info in self.tracked_rows.items():
            address = tracked_info["address"]
            name = tracked_info["name"]
            
            # Find matching value in decoded_values
            matching_value = None
            for value_data in poll_result.decoded_values:
                if isinstance(value_data, dict):
                    # Skip separators
                    if value_data.get("is_separator", False):
                        continue
                    
                    # Match by address and name
                    value_address = str(value_data.get("address", ""))
                    value_name = str(value_data.get("name", ""))
                    
                    if value_address == str(address) and value_name == str(name):
                        scaled = value_data.get("scaled", "")
                        if scaled != "":
                            try:
                                matching_value = float(scaled)
                                break
                            except (ValueError, TypeError):
                                pass
            
            # If we found a value, add it to history
            if matching_value is not None:
                timestamp = poll_result.timestamp
                self.data_history[row_key]["timestamps"].append(timestamp)
                self.data_history[row_key]["values"].append(matching_value)
        
        # Update graph
        self._update_graph()
    
    def _update_graph(self):
        """Update the graph with current data"""
        self.ax.clear()
        self.ax.set_facecolor('#1e1e1e')
        self.ax.tick_params(colors='#cccccc')
        self.ax.spines['bottom'].set_color('#cccccc')
        self.ax.spines['top'].set_color('#cccccc')
        self.ax.spines['right'].set_color('#cccccc')
        self.ax.spines['left'].set_color('#cccccc')
        self.ax.xaxis.label.set_color('#cccccc')
        self.ax.yaxis.label.set_color('#cccccc')
        self.ax.title.set_color('#cccccc')
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Scaled Value")
        self.ax.set_title("Modbus Data Over Time")
        self.ax.grid(True, alpha=0.3, color='#3e3e42')
        
        # Plot each tracked row
        all_timestamps = []
        all_values = []
        first_timestamp = None
        
        # Find the earliest timestamp across all data
        for history in self.data_history.values():
            if history["timestamps"]:
                for ts in history["timestamps"]:
                    if first_timestamp is None or ts < first_timestamp:
                        first_timestamp = ts
        
        # Plot each tracked row
        for row_key, history in self.data_history.items():
            if not history["timestamps"]:
                continue
            
            timestamps = history["timestamps"]
            values = history["values"]
            label = history["label"]
            color = history["color"]
            
            # Convert timestamps to relative time (seconds since first timestamp)
            if timestamps and first_timestamp:
                relative_times = [(t - first_timestamp).total_seconds() for t in timestamps]
                self.ax.plot(relative_times, values, label=label, color=color, linewidth=1.5)
                all_timestamps.extend(relative_times)
                all_values.extend(values)
        
        # Set axis limits
        if all_timestamps:
            if self.x_auto_scale:
                # Auto-scroll: show last x_window_seconds
                if len(all_timestamps) > 0:
                    # All timestamps are now relative (seconds)
                    latest_relative = max(all_timestamps)
                    x_min = max(0, latest_relative - self.x_window_seconds)
                    x_max = latest_relative
                    self.ax.set_xlim(x_min, x_max)
            else:
                # Manual X limits (in seconds)
                if self.x_min_time is not None and self.x_max_time is not None:
                    self.ax.set_xlim(self.x_min_time, self.x_max_time)
            
            if self.y_auto_scale:
                if all_values:
                    y_min = min(all_values)
                    y_max = max(all_values)
                    # Add some padding
                    y_range = y_max - y_min
                    if y_range > 0:
                        padding = y_range * 0.1
                        self.ax.set_ylim(y_min - padding, y_max + padding)
                    elif y_min == y_max:
                        # Single value - add small range
                        self.ax.set_ylim(y_min - 1, y_max + 1)
            else:
                # Manual Y limits
                if self.y_min_value is not None and self.y_max_value is not None:
                    self.ax.set_ylim(self.y_min_value, self.y_max_value)
        
        # Add legend
        if self.data_history:
            self.ax.legend(loc='upper left', facecolor='#252526', edgecolor='#3e3e42', labelcolor='#cccccc')
        
        # Set x-axis label
        self.ax.set_xlabel("Time (seconds)")
        
        self.canvas.draw()
    
    def _on_x_auto_changed(self, checked: bool):
        """Handle X-axis auto-scale checkbox change"""
        self.x_auto_scale = checked
        self.x_window_spin.setEnabled(checked)
        self._update_graph()
    
    def _on_x_window_changed(self, value: int):
        """Handle X-axis window size change"""
        self.x_window_seconds = value
        if self.x_auto_scale:
            self._update_graph()
    
    def _on_y_auto_changed(self, checked: bool):
        """Handle Y-axis auto-scale checkbox change"""
        self.y_auto_scale = checked
        self.y_min_spin.setEnabled(not checked)
        self.y_max_spin.setEnabled(not checked)
        if not checked:
            # Set current min/max from data
            all_values = []
            for history in self.data_history.values():
                all_values.extend(history["values"])
            if all_values:
                self.y_min_spin.setValue(min(all_values))
                self.y_max_spin.setValue(max(all_values))
        self._update_graph()
    
    def _on_y_limits_changed(self):
        """Handle Y-axis min/max change"""
        if not self.y_auto_scale:
            self.y_min_value = self.y_min_spin.value()
            self.y_max_value = self.y_max_spin.value()
            self._update_graph()
    
    def _clear_history(self):
        """Clear all data history"""
        for row_key in self.data_history:
            self.data_history[row_key]["timestamps"] = []
            self.data_history[row_key]["values"] = []
        self._update_graph()
    
    def closeEvent(self, event):
        """Handle dialog close - accept close but keep data history"""
        event.accept()
        # Data history is preserved, so graph can be reopened with same data

