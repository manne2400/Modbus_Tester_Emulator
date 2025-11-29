"""Help dialog with user guide"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser, 
    QTreeWidget, QTreeWidgetItem, QSplitter, QWidget
)
from PyQt6.QtCore import Qt
from src.ui.styles.theme import Theme


class HelpDialog(QDialog):
    """Help dialog with user guide"""
    
    def __init__(self, parent=None):
        """Initialize help dialog"""
        super().__init__(parent)
        self.setWindowTitle("Help - Modbus Tester")
        self.setModal(True)
        self.setMinimumSize(900, 700)
        
        self._setup_ui()
        self._apply_dark_theme()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD, Theme.MARGIN_STANDARD)
        
        # Splitter for navigation and content
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Navigation tree
        self.nav_tree = QTreeWidget()
        self.nav_tree.setHeaderLabel("Topics")
        self.nav_tree.setMaximumWidth(250)
        self.nav_tree.setMinimumWidth(200)
        self.nav_tree.itemClicked.connect(self._on_item_selected)
        
        # Content browser
        self.content_browser = QTextBrowser()
        self.content_browser.setReadOnly(True)
        
        # Build navigation tree
        self._build_navigation_tree()
        
        # Add to splitter
        splitter.addWidget(self.nav_tree)
        splitter.addWidget(self.content_browser)
        splitter.setStretchFactor(0, 0)  # Navigation doesn't stretch
        splitter.setStretchFactor(1, 1)  # Content stretches
        splitter.setSizes([250, 650])  # Initial sizes
        
        layout.addWidget(splitter)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Show first item by default
        if self.nav_tree.topLevelItem(0):
            self.nav_tree.setCurrentItem(self.nav_tree.topLevelItem(0))
            self._on_item_selected(self.nav_tree.topLevelItem(0), 0)
    
    def _build_navigation_tree(self):
        """Build navigation tree structure"""
        # Getting Started
        getting_started = QTreeWidgetItem(self.nav_tree, ["Getting Started"])
        QTreeWidgetItem(getting_started, ["1. Simulator Setup"])
        QTreeWidgetItem(getting_started, ["2. Device Scanner"])
        QTreeWidgetItem(getting_started, ["3. Create Connection"])
        QTreeWidgetItem(getting_started, ["4. Create Session"])
        QTreeWidgetItem(getting_started, ["5. Manage Tags"])
        QTreeWidgetItem(getting_started, ["6. Start Polling"])
        QTreeWidgetItem(getting_started, ["7. Write Values"])
        getting_started.setExpanded(True)
        
        # Connections & Sessions
        connections = QTreeWidgetItem(self.nav_tree, ["Connections & Sessions"])
        QTreeWidgetItem(connections, ["TCP Connections"])
        QTreeWidgetItem(connections, ["RTU Connections"])
        QTreeWidgetItem(connections, ["Session Configuration"])
        QTreeWidgetItem(connections, ["Polling Settings"])
        
        # Tags & Templates
        tags = QTreeWidgetItem(self.nav_tree, ["Tags & Templates"])
        QTreeWidgetItem(tags, ["Creating Tags"])
        QTreeWidgetItem(tags, ["Data Types"])
        QTreeWidgetItem(tags, ["Device Templates"])
        QTreeWidgetItem(tags, ["CSV/Excel Import/Export"])
        
        # Reading & Writing
        read_write = QTreeWidgetItem(self.nav_tree, ["Reading & Writing"])
        QTreeWidgetItem(read_write, ["Reading Data"])
        QTreeWidgetItem(read_write, ["Writing Values"])
        QTreeWidgetItem(read_write, ["Table Display"])
        
        # Function Codes
        function_codes = QTreeWidgetItem(self.nav_tree, ["Function Codes"])
        QTreeWidgetItem(function_codes, ["Read Functions"])
        QTreeWidgetItem(function_codes, ["Write Functions"])
        QTreeWidgetItem(function_codes, ["Addressing"])
        QTreeWidgetItem(function_codes, ["Data Types"])
        
        # Advanced Features
        advanced = QTreeWidgetItem(self.nav_tree, ["Advanced Features"])
        QTreeWidgetItem(advanced, ["Frame Analyzer"])
        QTreeWidgetItem(advanced, ["Snapshots & Compare"])
        QTreeWidgetItem(advanced, ["Multi-view"])
        QTreeWidgetItem(advanced, ["Device Scanner"])
        
        # Troubleshooting
        troubleshooting = QTreeWidgetItem(self.nav_tree, ["Troubleshooting"])
        QTreeWidgetItem(troubleshooting, ["Connection Problems"])
        QTreeWidgetItem(troubleshooting, ["Simulator Problems"])
        QTreeWidgetItem(troubleshooting, ["Polling Problems"])
        QTreeWidgetItem(troubleshooting, ["Tag Problems"])
        QTreeWidgetItem(troubleshooting, ["Device Scanner Issues"])
        
        # Tips & Best Practices
        tips = QTreeWidgetItem(self.nav_tree, ["Tips & Best Practices"])
        QTreeWidgetItem(tips, ["Best Practices"])
        QTreeWidgetItem(tips, ["Performance"])
        QTreeWidgetItem(tips, ["Multi-view Tips"])
        QTreeWidgetItem(tips, ["Tag Management Tips"])
    
    def _on_item_selected(self, item, column):
        """Handle navigation item selection"""
        if not item:
            return
        
        topic = item.text(0)
        parent = item.parent()
        parent_text = parent.text(0) if parent else ""
        
        # Get content based on selection
        content = self._get_content_for_topic(topic, parent_text)
        self.content_browser.setHtml(content)
    
    def _get_content_for_topic(self, topic, parent):
        """Get HTML content for selected topic"""
        content_map = {
            # Getting Started
            ("1. Simulator Setup", "Getting Started"): self._get_simulator_setup(),
            ("2. Device Scanner", "Getting Started"): self._get_device_scanner(),
            ("3. Create Connection", "Getting Started"): self._get_create_connection(),
            ("4. Create Session", "Getting Started"): self._get_create_session(),
            ("5. Manage Tags", "Getting Started"): self._get_manage_tags(),
            ("6. Start Polling", "Getting Started"): self._get_start_polling(),
            ("7. Write Values", "Getting Started"): self._get_write_values(),
            
            # Connections & Sessions
            ("TCP Connections", "Connections & Sessions"): self._get_tcp_connections(),
            ("RTU Connections", "Connections & Sessions"): self._get_rtu_connections(),
            ("Session Configuration", "Connections & Sessions"): self._get_session_config(),
            ("Polling Settings", "Connections & Sessions"): self._get_polling_settings(),
            
            # Tags & Templates
            ("Creating Tags", "Tags & Templates"): self._get_creating_tags(),
            ("Data Types", "Tags & Templates"): self._get_data_types(),
            ("Device Templates", "Tags & Templates"): self._get_device_templates(),
            ("CSV/Excel Import/Export", "Tags & Templates"): self._get_csv_import_export(),
            
            # Reading & Writing
            ("Reading Data", "Reading & Writing"): self._get_reading_data(),
            ("Writing Values", "Reading & Writing"): self._get_writing_values(),
            ("Table Display", "Reading & Writing"): self._get_table_display(),
            
            # Function Codes
            ("Read Functions", "Function Codes"): self._get_read_functions(),
            ("Write Functions", "Function Codes"): self._get_write_functions(),
            ("Addressing", "Function Codes"): self._get_addressing(),
            ("Data Types", "Function Codes"): self._get_function_data_types(),
            
            # Advanced Features
            ("Frame Analyzer", "Advanced Features"): self._get_frame_analyzer(),
            ("Snapshots & Compare", "Advanced Features"): self._get_snapshots_compare(),
            ("Multi-view", "Advanced Features"): self._get_multi_view(),
            ("Device Scanner", "Advanced Features"): self._get_device_scanner_advanced(),
            
            # Troubleshooting
            ("Connection Problems", "Troubleshooting"): self._get_connection_problems(),
            ("Simulator Problems", "Troubleshooting"): self._get_simulator_problems(),
            ("Polling Problems", "Troubleshooting"): self._get_polling_problems(),
            ("Tag Problems", "Troubleshooting"): self._get_tag_problems(),
            ("Device Scanner Issues", "Troubleshooting"): self._get_scanner_issues(),
            
            # Tips
            ("Best Practices", "Tips & Best Practices"): self._get_best_practices(),
            ("Performance", "Tips & Best Practices"): self._get_performance(),
            ("Multi-view Tips", "Tips & Best Practices"): self._get_multi_view_tips(),
            ("Tag Management Tips", "Tips & Best Practices"): self._get_tag_management_tips(),
        }
        
        content = content_map.get((topic, parent), f"<h2>{topic}</h2><p>Content coming soon...</p>")
        return content
        
    def _get_simulator_setup(self):
        """Get simulator setup content"""
        return """
        <h2>Getting Started</h2>
        <h3>1. Start a simulator (optional - for testing)</h3>
        <p>To test the application, you can start a simulated Modbus server directly from the app:</p>
        <ul>
            <li>Go to <b>View → Modbus Simulator...</b></li>
            <li>Select <b>TCP</b> or <b>RTU</b> tab</li>
            <li>Configure the settings (port, baudrate, etc.)</li>
            <li>Click <b>"Start TCP Simulator"</b> or <b>"Start RTU Simulator"</b></li>
            <li>The simulator now runs in the background and can be used for testing</li>
        </ul>
        
        <p><b>Important for RTU testing:</b></p>
        <p>To test RTU connections, you must first create a virtual COM port pair using a serial port emulator:</p>
        <ul>
            <li><b>Download and install a serial port emulator:</b>
                <ul>
                    <li><b>com0com</b> (free, open source) - Download from: https://sourceforge.net/projects/com0com/</li>
                    <li><b>Virtual Serial Port Driver</b> (paid solution, signed drivers) - Download from: https://www.virtual-serial-port.org/</li>
                    <li>Or another serial port emulator of your choice</li>
                </ul>
            </li>
            <li><b>Create a COM port pair:</b>
                <ul>
                    <li>After installation, open the emulator program</li>
                    <li>Create a pair of virtual COM ports (e.g. COM10 ↔ COM11)</li>
                    <li>These ports will function as if they are connected with a cable</li>
                </ul>
            </li>
            <li><b>Use the COM port pair:</b>
                <ul>
                    <li>Start the RTU simulator on one port (e.g. COM10) via <b>View → Modbus Simulator...</b></li>
                    <li>Create an RTU connection in the app to the other port (e.g. COM11)</li>
                    <li>Now you can test RTU communication between simulator and application</li>
                </ul>
            </li>
            <li><b>Note:</b> If you get Code 52 error with com0com, you may need to disable driver signature enforcement in Windows (see "Troubleshooting" tab)</li>
        </ul>
        <p><b>Test data in the simulator:</b></p>
        <ul>
            <li>Holding registers (0-9): 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000</li>
            <li>Holding registers (20-31): DINT (INT32) test values:
                <ul>
                    <li>Address 20-21: 1,000,000</li>
                    <li>Address 22-23: -500,000</li>
                    <li>Address 24-25: 2,147,483,647 (MAX INT32)</li>
                    <li>Address 26-27: -2,147,483,648 (MIN INT32)</li>
                    <li>Address 28-29: 12,345</li>
                    <li>Address 30-31: -12,345</li>
                </ul>
            </li>
            <li><b>Dedicated write addresses:</b>
                <ul>
                    <li>Holding registers (40-49): Initialized to 0 - can be written with function code 06 or 10</li>
                    <li>Coils (20-29): Initialized to False - can be written with function code 05 or 0F</li>
                </ul>
            </li>
            <li>Input registers (0-9): 50, 150, 250, 350, 450, 550, 650, 750, 850, 950</li>
            <li>Input registers (20-31): DINT (INT32) test values:
                <ul>
                    <li>Address 20-21: 50,000</li>
                    <li>Address 22-23: -25,000</li>
                    <li>Address 24-25: 100,000</li>
                    <li>Address 26-27: -100,000</li>
                    <li>Address 28-29: 999,999</li>
                    <li>Address 30-31: -999,999</li>
                </ul>
            </li>
            <li>Coils (0-9): True, False, True, False, True, False, True, False, True, False</li>
            <li>Discrete inputs (0-9): False, True, False, True, False, True, False, True, False, True</li>
            <li>Slave ID: 1</li>
        </ul>
        
        <h3>2. Scan for devices (optional)</h3>
        <p>If you're working with Modbus devices and don't know the device IDs or IP addresses, you can use the Device Scanner:</p>
        <p><b>For RTU devices:</b></p>
        <ul>
            <li>Go to <b>Connection → Device Scanner...</b> and select the <b>RTU Scanner</b> tab</li>
            <li>Select the COM port and configure serial settings (baudrate, parity, etc.)</li>
            <li>Set the device ID range to scan (default: 1-247)</li>
            <li>Click <b>"Start Scan"</b> to automatically discover Modbus devices</li>
            <li>The scanner will find devices and show which register types are available</li>
            <li><b>Note:</b> Only addresses with active values are shown (coils/discrete inputs with value=1, registers with value≠0)</li>
        </ul>
        <p><b>For TCP/IP devices:</b></p>
        <ul>
            <li>Go to <b>Connection → Device Scanner...</b> and select the <b>TCP Scanner</b> tab</li>
            <li>Enter IP range (e.g., "192.168.1.1-254" or "192.168.1.0/24" for CIDR notation)</li>
            <li>Enter ports to scan (e.g., "502" or "502,5020" for multiple ports)</li>
            <li>Set the device ID range to scan (default: 1-247)</li>
            <li>Click <b>"Start Scan"</b> to automatically discover Modbus TCP devices on the network</li>
            <li>The scanner will test each IP:port combination and scan device IDs</li>
            <li><b>Note:</b> Only addresses with active values are shown (coils/discrete inputs with value=1, registers with value≠0)</li>
        </ul>
        <p><b>Device Scanner Features:</b></p>
        <ul>
            <li><b>Save as PDF:</b> Click "Save as PDF" button to export device information to a PDF file</li>
            <li><b>Import Connection:</b> Right-click on a found device and select "Import Connection" to automatically create a connection profile</li>
            <li><b>Import Session:</b> Right-click on a found device and select "Import Session" to automatically create a connection and session with the discovered register addresses</li>
        </ul>
        
        <h3>3. Create a connection</h3>
        <p>Go to <b>Connection → New Connection...</b> or click "New Connection" in the toolbar.</p>
        <p><b>For TCP:</b></p>
        <ul>
            <li>Name: Choose a descriptive name (e.g. "PLC1")</li>
            <li>Host/IP: Enter the IP address (e.g. 127.0.0.1 for simulator)</li>
            <li>Port: Typically 502 for Modbus TCP (or 5020 for simulator)</li>
            <li>Timeout: 3 seconds (default)</li>
        </ul>
        <p><b>For RTU:</b></p>
        <ul>
            <li>Name: Choose a descriptive name (e.g. "RS485 Bus")</li>
            <li>Port: Select COM port (e.g. COM10 or COM11)</li>
            <li>Baudrate: Typically 9600, 19200, or 38400</li>
            <li>Parity: N (None), E (Even), or O (Odd)</li>
            <li>Stop bits: 1 or 2</li>
            <li>Data bits: 7 or 8</li>
        </ul>
        <p><b>Tip:</b> Connections are automatically grouped by type (TCP/RTU) in the connection tree.</p>
        
        <h3>4. Create a session</h3>
        <p>Go to <b>Session → New Session...</b> or click "New Session" in the toolbar.</p>
        <p>Configure the session:</p>
        <ul>
            <li><b>Connection:</b> Select the connection you just created</li>
            <li><b>Slave ID:</b> Modbus slave/unit ID (typically 1-247, use 1 for simulator)</li>
            <li><b>Function Code:</b> Select read function (01-04). Write operations are done via the "Write Value..." button.</li>
            <li><b>Start Address:</b> Start address for reading/writing (start with 0 for simulator)</li>
            <li><b>Quantity:</b> Number of coils/registers (e.g. 10)</li>
            <li><b>Poll Interval:</b> How often data should be read (in milliseconds, e.g. 1000)</li>
        </ul>
        
        <h3>5. Manage Tags (optional)</h3>
        <p>To get names, data types and scaling on your data:</p>
        <ul>
            <li>Click the <b>"Manage Tags..."</b> button in the session tab</li>
            <li>Click <b>"Add Tag"</b> to create a new tag</li>
            <li>Configure the tag:
                <ul>
                    <li><b>Address Type:</b> Must match session's function code (Holding Register for function 03, Input Register for function 04)</li>
                    <li><b>Address:</b> Register address</li>
                    <li><b>Name:</b> A descriptive name (e.g. "Temperature")</li>
                    <li><b>Data Type:</b> Select data type (UINT16, INT16, INT32/DINT, UINT32, FLOAT32, BOOL)</li>
                    <li><b>Byte Order:</b> Big Endian (default), Little Endian, or Swapped</li>
                    <li><b>Scaling:</b> Scale factor and offset (optional)</li>
                    <li><b>Unit:</b> Unit designation (e.g. "°C", "bar", "%")</li>
                </ul>
            </li>
            <li><b>Important:</b> Tags with incorrect address_type will be ignored. Make sure address_type matches function code!</li>
        </ul>
        
        <h3>5a. Device Templates & Tag Library (optional)</h3>
        <p>For BMS/CTS work, you can reuse tag sets for standard equipment:</p>
        <ul>
            <li>Go to <b>Session → Device Templates...</b> to manage your template library</li>
            <li><b>Save tags as template:</b> In tag management dialog, click "Save tags as template..." to create a reusable template from current session tags</li>
            <li><b>Load from template:</b> In tag management dialog, click "Load from template..." to quickly apply a standard tag set to your session</li>
            <li><b>Import from CSV/Excel:</b> Import register overviews from suppliers (e.g., Excel files with register addresses and descriptions)</li>
            <li><b>Export to CSV/Excel:</b> Export templates or session tags for use in other systems or BMS projects</li>
            <li>Templates are perfect for standard equipment like VAV boxes, pumps, VFDs, ventilation units, etc.</li>
        </ul>
        
        <h3>6. Start polling</h3>
        <p>Click the <b>"Start"</b> button in the session tab to begin reading data.</p>
        <p>Data will be displayed in the table below with:</p>
        <ul>
            <li><b>Address:</b> Register address</li>
            <li><b>Name:</b> Tag name (if defined) or "Address X"</li>
            <li><b>Raw Value:</b> The raw value from Modbus (after data type decoding)</li>
            <li><b>HEX:</b> Hexadecimal representation of the value</li>
            <li><b>Scaled Value:</b> The value after scaling (if tag has scaling)</li>
            <li><b>Unit:</b> Unit designation from tag (e.g. "°C")</li>
            <li><b>Status:</b> OK, Timeout, Error, etc.</li>
        </ul>
        <p><b>Table Layout:</b></p>
        <ul>
            <li>First, all raw addresses are shown (based on quantity setting)</li>
            <li>Then a separator line "--- Tags ---" appears</li>
            <li>Finally, all matching tags are displayed with decoded values</li>
            <li>This allows you to see both raw addresses and tags simultaneously</li>
        </ul>
        
        <h3>6a. Write values</h3>
        <p>To write values to Modbus devices:</p>
        <ul>
            <li>Click the <b>"Write Value..."</b> button in the session tab</li>
            <li>In the write dialog:
                <ul>
                    <li><b>Function Code:</b> Select write function (05, 06, 0F, or 10)</li>
                    <li><b>Address:</b> The address to write to</li>
                    <li><b>Value:</b> The value(s) to write:
                        <ul>
                            <li>For single write (05/06): Enter a single value</li>
                            <li>For multiple write (0F/10): Enter comma-separated values (e.g., "100,200,300")</li>
                            <li>For multiple registers: You can also enter one large value that will be automatically split into multiple registers (Big Endian format)</li>
                        </ul>
                    </li>
                    <li><b>Quantity:</b> For multiple write functions, specify how many values</li>
                </ul>
            </li>
            <li>Click <b>"Write"</b> to execute the write operation</li>
            <li>Data will automatically refresh after a successful write</li>
        </ul>
        <p><b>Note:</b> Function code dropdown in session tab only shows read functions (01-04). Write operations are always done via the "Write Value..." button.</p>
        
        <h3>7. Frame Analyzer (optional - for diagnostics)</h3>
        <p>To analyze Modbus communication and diagnose issues:</p>
        <ul>
            <li>Go to <b>View → Frame Analyzer...</b></li>
            <li>The analyzer shows all TX/RX frames in a table with timestamps, direction, slave ID, function codes, and results</li>
            <li>Click on a frame to see detailed information (raw hex, decoded info, error descriptions)</li>
            <li><b>Statistics tab:</b> View aggregated statistics:
                <ul>
                    <li>Total requests/responses, timeouts per slave, CRC errors, average response times</li>
                </ul>
            </li>
            <li><b>Diagnostics tab:</b> See automatic findings:
                <ul>
                    <li>Many timeouts on a slave (check cable/ID/baudrate)</li>
                    <li>ID conflicts (multiple devices responding to same ID)</li>
                    <li>Consistent exceptions (wrong function code or unsupported function)</li>
                </ul>
            </li>
            <li>Use filters to focus on specific issues (errors only, specific slave ID, function code, etc.)</li>
            <li>This helps answer: "What's actually happening on the bus?" and "Why is it failing?"</li>
        </ul>
        
        <h3>8. Snapshots & Compare (optional - for documentation)</h3>
        <p>To capture and compare installation states:</p>
        <ul>
            <li><b>Take Snapshot:</b> Go to <b>Snapshots → Take Snapshot...</b>
                <ul>
                    <li>Choose scope: Current session or all sessions</li>
                    <li>Add a name and optional note (e.g., "Before parameter change")</li>
                    <li>Snapshots capture all current values from active sessions</li>
                </ul>
            </li>
            <li><b>Manage Snapshots:</b> Go to <b>Snapshots → Manage Snapshots...</b>
                <ul>
                    <li>View all snapshots with details (timestamp, scope, number of values)</li>
                    <li>Select 2 snapshots (hold Ctrl and click) and click "Compare..." to see differences</li>
                    <li>Export snapshots or comparisons to CSV for documentation</li>
                    <li>Delete old snapshots</li>
                </ul>
            </li>
            <li><b>Compare View:</b> When comparing two snapshots:
                <ul>
                    <li>See side-by-side comparison with changed values highlighted</li>
                    <li>View numeric differences and percentages</li>
                    <li>Filter to show only changed values</li>
                    <li>Export diff to CSV</li>
                </ul>
            </li>
            <li>Perfect for: "It worked yesterday - what's different now?" or documenting parameter changes</li>
        </ul>
        
        <h3>9. Multi-view (optional)</h3>
        <p>To see multiple sessions simultaneously side by side:</p>
        <ul>
            <li>Go to <b>View → Manage Multi-view...</b></li>
            <li>Create groups and add sessions to each group</li>
            <li>Activate <b>View → Multi-view</b> to see all groups side by side</li>
            <li>Click on a group in the connection tree to focus on it</li>
        </ul>
        """
    
    def _get_device_scanner(self):
        """Get device scanner content"""
        return """
        <h2>Device Scanner</h2>
        <p>If you're working with Modbus devices and don't know the device IDs or IP addresses, you can use the Device Scanner:</p>
        <p><b>For RTU devices:</b></p>
        <ul>
            <li>Go to <b>Connection → Device Scanner...</b> and select the <b>RTU Scanner</b> tab</li>
            <li>Select the COM port and configure serial settings (baudrate, parity, etc.)</li>
            <li>Set the device ID range to scan (default: 1-247)</li>
            <li>Click <b>"Start Scan"</b> to automatically discover Modbus devices</li>
            <li>The scanner will find devices and show which register types are available</li>
            <li><b>Note:</b> Only addresses with active values are shown (coils/discrete inputs with value=1, registers with value≠0)</li>
        </ul>
        <p><b>For TCP/IP devices:</b></p>
        <ul>
            <li>Go to <b>Connection → Device Scanner...</b> and select the <b>TCP Scanner</b> tab</li>
            <li>Enter IP range (e.g., "192.168.1.1-254" or "192.168.1.0/24" for CIDR notation)</li>
            <li>Enter ports to scan (e.g., "502" or "502,5020" for multiple ports)</li>
            <li>Set the device ID range to scan (default: 1-247)</li>
            <li>Click <b>"Start Scan"</b> to automatically discover Modbus TCP devices on the network</li>
            <li>The scanner will test each IP:port combination and scan device IDs</li>
            <li><b>Note:</b> Only addresses with active values are shown (coils/discrete inputs with value=1, registers with value≠0)</li>
        </ul>
        <p><b>Device Scanner Features:</b></p>
        <ul>
            <li><b>Save as PDF:</b> Click "Save as PDF" button to export device information to a PDF file</li>
            <li><b>Import Connection:</b> Right-click on a found device and select "Import Connection" to automatically create a connection profile</li>
            <li><b>Import Session:</b> Right-click on a found device and select "Import Session" to automatically create a connection and session with the discovered register addresses</li>
        </ul>
        """
    
    def _get_create_connection(self):
        """Get create connection content"""
        return """
        <h2>Create Connection</h2>
        <p>Go to <b>Connection → New Connection...</b> or click "New Connection" in the toolbar.</p>
        <p><b>For TCP:</b></p>
        <ul>
            <li>Name: Choose a descriptive name (e.g. "PLC1")</li>
            <li>Host/IP: Enter the IP address (e.g. 127.0.0.1 for simulator)</li>
            <li>Port: Typically 502 for Modbus TCP (or 5020 for simulator)</li>
            <li>Timeout: 3 seconds (default)</li>
        </ul>
        <p><b>For RTU:</b></p>
        <ul>
            <li>Name: Choose a descriptive name (e.g. "RS485 Bus")</li>
            <li>Port: Select COM port (e.g. COM10 or COM11)</li>
            <li>Baudrate: Typically 9600, 19200, or 38400</li>
            <li>Parity: N (None), E (Even), or O (Odd)</li>
            <li>Stop bits: 1 or 2</li>
            <li>Data bits: 7 or 8</li>
        </ul>
        <p><b>Tip:</b> Connections are automatically grouped by type (TCP/RTU) in the connection tree.</p>
        """
    
    def _get_create_session(self):
        """Get create session content"""
        return """
        <h2>Create Session</h2>
        <p>Go to <b>Session → New Session...</b> or click "New Session" in the toolbar.</p>
        <p>Configure the session:</p>
        <ul>
            <li><b>Connection:</b> Select the connection you just created</li>
            <li><b>Slave ID:</b> Modbus slave/unit ID (typically 1-247, use 1 for simulator)</li>
            <li><b>Function Code:</b> Select read function (01-04). Write operations are done via the "Write Value..." button.</li>
            <li><b>Start Address:</b> Start address for reading (start with 0 for simulator)</li>
            <li><b>Quantity:</b> Number of coils/registers to read (e.g. 10)</li>
            <li><b>Poll Interval:</b> How often data should be read (in milliseconds, e.g. 1000)</li>
        </ul>
        """
    
    def _get_manage_tags(self):
        """Get manage tags content"""
        return """
        <h2>Manage Tags</h2>
        <p>To get names, data types and scaling on your data:</p>
        <ul>
            <li>Click the <b>"Manage Tags..."</b> button in the session tab</li>
            <li>Click <b>"Add Tag"</b> to create a new tag</li>
            <li>Configure the tag:
                <ul>
                    <li><b>Address Type:</b> Must match session's function code (Holding Register for function 03, Input Register for function 04)</li>
                    <li><b>Address:</b> Register address</li>
                    <li><b>Name:</b> A descriptive name (e.g. "Temperature")</li>
                    <li><b>Data Type:</b> Select data type (UINT16, INT16, INT32/DINT, UINT32, FLOAT32, BOOL)</li>
                    <li><b>Byte Order:</b> Big Endian (default), Little Endian, or Swapped</li>
                    <li><b>Scaling:</b> Scale factor and offset (optional)</li>
                    <li><b>Unit:</b> Unit designation (e.g. "°C", "bar", "%")</li>
                </ul>
            </li>
            <li><b>Important:</b> Tags with incorrect address_type will be ignored. Make sure address_type matches function code!</li>
        </ul>
        """
    
    def _get_start_polling(self):
        """Get start polling content"""
        return """
        <h2>Start Polling</h2>
        <p>Click the <b>"Start"</b> button in the session tab to begin reading data.</p>
        <p>Data will be displayed in the table below with:</p>
        <ul>
            <li><b>Address:</b> Register address</li>
            <li><b>Name:</b> Tag name (if defined) or "Address X"</li>
            <li><b>Raw Value:</b> The raw value from Modbus (after data type decoding)</li>
            <li><b>HEX:</b> Hexadecimal representation of the value</li>
            <li><b>Scaled Value:</b> The value after scaling (if tag has scaling)</li>
            <li><b>Unit:</b> Unit designation from tag (e.g. "°C")</li>
            <li><b>Status:</b> OK, Timeout, Error, etc.</li>
        </ul>
        <p><b>Table Layout:</b></p>
        <ul>
            <li>First, all raw addresses are shown (based on quantity setting)</li>
            <li>Then a separator line "--- Tags ---" appears</li>
            <li>Finally, all matching tags are displayed with decoded values</li>
            <li>This allows you to see both raw addresses and tags simultaneously</li>
        </ul>
        """
    
    def _get_write_values(self):
        """Get write values content"""
        return """
        <h2>Write Values</h2>
        <p>To write values to Modbus devices:</p>
        <ul>
            <li>Click the <b>"Write Value..."</b> button in the session tab</li>
            <li>In the write dialog:
                <ul>
                    <li><b>Function Code:</b> Select write function (05, 06, 0F, or 10)</li>
                    <li><b>Address:</b> The address to write to</li>
                    <li><b>Value:</b> The value(s) to write:
                        <ul>
                            <li>For single write (05/06): Enter a single value</li>
                            <li>For multiple write (0F/10): Enter comma-separated values (e.g., "100,200,300")</li>
                            <li>For multiple registers: You can also enter one large value that will be automatically split into multiple registers (Big Endian format)</li>
                        </ul>
                    </li>
                    <li><b>Quantity:</b> For multiple write functions, specify how many values</li>
                </ul>
            </li>
            <li>Click <b>"Write"</b> to execute the write operation</li>
            <li>Data will automatically refresh after a successful write</li>
        </ul>
        <p><b>Note:</b> Function code dropdown in session tab only shows read functions (01-04). Write operations are always done via the "Write Value..." button.</p>
        """
    
    def _get_tcp_connections(self):
        """Get TCP connections content"""
        return """
        <h2>TCP Connections</h2>
        <p>Modbus TCP/IP connections use Ethernet to communicate with Modbus devices.</p>
        <p><b>Configuration:</b></p>
        <ul>
            <li><b>Name:</b> Choose a descriptive name (e.g. "PLC1", "Server Room")</li>
            <li><b>Host/IP:</b> Enter the IP address (e.g. 192.168.1.100) or hostname</li>
            <li><b>Port:</b> Typically 502 for Modbus TCP (or 5020 for simulator)</li>
            <li><b>Timeout:</b> Connection timeout in seconds (default: 3)</li>
        </ul>
        <p><b>Tips:</b></p>
        <ul>
            <li>Use port 5020 for the integrated simulator</li>
            <li>Check firewall settings if connection fails</li>
            <li>Multiple sessions can share the same TCP connection</li>
        </ul>
        """
    
    def _get_rtu_connections(self):
        """Get RTU connections content"""
        return """
        <h2>RTU Connections</h2>
        <p>Modbus RTU connections use serial communication (RS-485/RS-232) to communicate with Modbus devices.</p>
        <p><b>Configuration:</b></p>
        <ul>
            <li><b>Name:</b> Choose a descriptive name (e.g. "RS485 Bus", "COM Port 1")</li>
            <li><b>Port:</b> Select COM port (e.g. COM1, COM10, COM11)</li>
            <li><b>Baudrate:</b> Communication speed - typically 9600, 19200, or 38400</li>
            <li><b>Parity:</b> N (None), E (Even), or O (Odd)</li>
            <li><b>Stop bits:</b> 1 or 2</li>
            <li><b>Data bits:</b> 7 or 8</li>
        </ul>
        <p><b>Tips:</b></p>
        <ul>
            <li>Settings must match the device configuration exactly</li>
            <li>Only one session can use a COM port at a time</li>
            <li>For simulator testing, use a virtual COM port pair (see Simulator Setup)</li>
        </ul>
        """
    
    def _get_session_config(self):
        """Get session configuration content"""
        return """
        <h2>Session Configuration</h2>
        <p>A session defines what data to read from a Modbus device.</p>
        <p><b>Settings:</b></p>
        <ul>
            <li><b>Connection:</b> Select which connection to use</li>
            <li><b>Slave ID:</b> Modbus device/unit ID (1-247)</li>
            <li><b>Function Code:</b> Select read function (01-04):
                <ul>
                    <li>01 - Read Coils</li>
                    <li>02 - Read Discrete Inputs</li>
                    <li>03 - Read Holding Registers</li>
                    <li>04 - Read Input Registers</li>
                </ul>
            </li>
            <li><b>Start Address:</b> First address to read (0-based)</li>
            <li><b>Quantity:</b> Number of addresses to read</li>
            <li><b>Poll Interval:</b> How often to read data (milliseconds)</li>
        </ul>
        """
    
    def _get_polling_settings(self):
        """Get polling settings content"""
        return """
        <h2>Polling Settings</h2>
        <p>Polling settings control how often data is read from the device.</p>
        <p><b>Poll Interval:</b></p>
        <ul>
            <li>Minimum: 100 ms</li>
            <li>Maximum: 60000 ms (60 seconds)</li>
            <li>Recommended: Start with 1000 ms (1 second) and adjust as needed</li>
        </ul>
        <p><b>Best Practices:</b></p>
        <ul>
            <li>Start with slow poll interval (1000ms+) and increase gradually</li>
            <li>Faster polling = more network/device load</li>
            <li>RTU: Only one request at a time per COM port</li>
            <li>TCP: Multiple sessions can run in parallel</li>
        </ul>
        """
    
    def _get_creating_tags(self):
        """Get creating tags content"""
        return """
        <h2>Creating Tags</h2>
        <p>Tags provide meaningful names and data types to Modbus addresses.</p>
        <p><b>Steps:</b></p>
        <ol>
            <li>Click <b>"Manage Tags..."</b> in the session tab</li>
            <li>Click <b>"Add Tag"</b></li>
            <li>Configure the tag:
                <ul>
                    <li><b>Address Type:</b> Must match session's function code</li>
                    <li><b>Address:</b> Register/coil address</li>
                    <li><b>Name:</b> Descriptive name (e.g. "Temperature", "Pressure")</li>
                    <li><b>Data Type:</b> UINT16, INT16, INT32, UINT32, FLOAT32, or BOOL</li>
                    <li><b>Byte Order:</b> Big Endian (default), Little Endian, or Swapped</li>
                    <li><b>Scaling:</b> Optional scale factor and offset</li>
                    <li><b>Unit:</b> Unit designation (e.g. "°C", "bar")</li>
                </ul>
            </li>
        </ol>
        <p><b>Important:</b> Tag's address_type MUST match session's function code, otherwise the tag is ignored!</p>
        """
    
    def _get_data_types(self):
        """Get data types content"""
        return """
        <h2>Data Types</h2>
        <p>The application supports the following data types:</p>
        <table border="1" cellpadding="5">
        <tr><th>Data Type</th><th>Description</th><th>Registers</th><th>Range</th></tr>
        <tr><td>BOOL</td><td>Boolean (1 bit)</td><td>1 bit</td><td>True/False</td></tr>
        <tr><td>UINT16</td><td>16-bit unsigned integer</td><td>1 register</td><td>0 to 65535</td></tr>
        <tr><td>INT16</td><td>16-bit signed integer</td><td>1 register</td><td>-32768 to 32767</td></tr>
        <tr><td>UINT32</td><td>32-bit unsigned integer</td><td>2 registers</td><td>0 to 4,294,967,295</td></tr>
        <tr><td>INT32 (DINT)</td><td>32-bit signed integer</td><td>2 registers</td><td>-2,147,483,648 to 2,147,483,647</td></tr>
        <tr><td>FLOAT32</td><td>32-bit floating point</td><td>2 registers</td><td>IEEE 754 format</td></tr>
        </table>
        <p><b>Important:</b> Multi-register types (INT32, UINT32, FLOAT32) use 2 registers. Make sure to read enough registers!</p>
        <p><b>Byte Order:</b></p>
        <ul>
            <li><b>Big Endian:</b> Most significant byte first (default, most common)</li>
            <li><b>Little Endian:</b> Least significant byte first</li>
            <li><b>Swapped:</b> Word-swapped (for some devices)</li>
        </ul>
        """
    
    def _get_device_templates(self):
        """Get device templates content"""
        return """
        <h2>Device Templates</h2>
        <p>Device templates allow you to reuse tag sets for standard equipment.</p>
        <p><b>Save tags as template:</b></p>
        <ul>
            <li>In tag management dialog, click <b>"Save tags as template..."</b></li>
            <li>Enter a name and description for the template</li>
            <li>The template is saved and can be reused in other sessions</li>
        </ul>
        <p><b>Load from template:</b></p>
        <ul>
            <li>In tag management dialog, click <b>"Load from template..."</b></li>
            <li>Select a template from the list</li>
            <li>Only tags matching the session's address type are loaded</li>
            <li>Tags are automatically added to the session</li>
        </ul>
        <p><b>Perfect for:</b></p>
        <ul>
            <li>Standard equipment (VAV boxes, pumps, VFDs, ventilation units)</li>
            <li>Reusing tag sets across multiple projects</li>
            <li>Sharing tag configurations with team members</li>
        </ul>
        """
    
    def _get_csv_import_export(self):
        """Get CSV/Excel import/export content"""
        return """
        <h2>CSV/Excel Import/Export</h2>
        <p>Import register overviews from suppliers or export tags for use in other systems.</p>
        <p><b>Import:</b></p>
        <ul>
            <li>Go to <b>Session → Device Templates...</b></li>
            <li>Click <b>"Import"</b> and select CSV or Excel file</li>
            <li>Map your file columns to application fields (Address, Name, Data Type, etc.)</li>
            <li>Import creates a template that can be used in sessions</li>
        </ul>
        <p><b>Export:</b></p>
        <ul>
            <li>In tag management dialog, click <b>"Export"</b></li>
            <li>Or export templates from Device Templates dialog</li>
            <li>Choose CSV or Excel format</li>
            <li>Exported files can be used in BMS projects or shared with suppliers</li>
        </ul>
        """
    
    def _get_reading_data(self):
        """Get reading data content"""
        return """
        <h2>Reading Data</h2>
        <p>Data is automatically read from Modbus devices based on your session configuration.</p>
        <p><b>How it works:</b></p>
        <ul>
            <li>Click <b>"Start"</b> button to begin polling</li>
            <li>Data is read at the specified poll interval</li>
            <li>Results are displayed in the data table</li>
            <li>Status shows OK, Timeout, Error, etc.</li>
        </ul>
        <p><b>Function Codes:</b></p>
        <ul>
            <li><b>01 - Read Coils:</b> Read coil outputs (read/write)</li>
            <li><b>02 - Read Discrete Inputs:</b> Read discrete inputs (read-only)</li>
            <li><b>03 - Read Holding Registers:</b> Read holding registers (read/write)</li>
            <li><b>04 - Read Input Registers:</b> Read input registers (read-only)</li>
        </ul>
        """
    
    def _get_writing_values(self):
        """Get writing values content"""
        return """
        <h2>Writing Values</h2>
        <p>To write values to Modbus devices:</p>
        <ol>
            <li>Click the <b>"Write Value..."</b> button in the session tab</li>
            <li>Select write function code (05, 06, 0F, or 10)</li>
            <li>Enter the address to write to</li>
            <li>Enter the value(s):
                <ul>
                    <li>Single write: Enter one value</li>
                    <li>Multiple write: Enter comma-separated values or one large value (auto-split)</li>
                </ul>
            </li>
            <li>Click <b>"Write"</b> to execute</li>
        </ol>
        <p><b>Write Function Codes:</b></p>
        <ul>
            <li><b>05 - Write Single Coil:</b> Write one coil (True/False)</li>
            <li><b>06 - Write Single Register:</b> Write one register (0-65535)</li>
            <li><b>0F - Write Multiple Coils:</b> Write multiple coils</li>
            <li><b>10 - Write Multiple Registers:</b> Write multiple registers</li>
        </ul>
        <p><b>Note:</b> Data automatically refreshes after successful write.</p>
        """
    
    def _get_table_display(self):
        """Get table display content"""
        return """
        <h2>Table Display</h2>
        <p>The data table shows all read values with the following columns:</p>
        <ul>
            <li><b>Address:</b> Register/coil address</li>
            <li><b>Name:</b> Tag name (if defined) or "Address X"</li>
            <li><b>Raw Value:</b> The raw value from Modbus (after data type decoding)</li>
            <li><b>HEX:</b> Hexadecimal representation of the value</li>
            <li><b>Scaled Value:</b> The value after scaling (if tag has scaling)</li>
            <li><b>Unit:</b> Unit designation from tag (e.g. "°C")</li>
            <li><b>Status:</b> OK, Timeout, Error, etc.</li>
        </ul>
        <p><b>Table Layout:</b></p>
        <ul>
            <li>First, all raw addresses are shown (based on quantity setting)</li>
            <li>Then a separator line "--- Tags ---" appears</li>
            <li>Finally, all matching tags are displayed with decoded values</li>
            <li>This allows you to see both raw addresses and tags simultaneously</li>
        </ul>
        """
    
    def _get_read_functions(self):
        """Get read functions content"""
        return """
        <h2>Read Functions</h2>
        <table border="1" cellpadding="5">
        <tr><th>Code</th><th>Name</th><th>Description</th></tr>
        <tr><td>01</td><td>Read Coils</td><td>Read coils (outputs, read/write)</td></tr>
        <tr><td>02</td><td>Read Discrete Inputs</td><td>Read discrete inputs (read-only)</td></tr>
        <tr><td>03</td><td>Read Holding Registers</td><td>Read holding registers (read/write)</td></tr>
        <tr><td>04</td><td>Read Input Registers</td><td>Read input registers (read-only)</td></tr>
        </table>
        <p><b>Usage:</b></p>
        <ul>
            <li>Select function code in session configuration</li>
            <li>Only read functions (01-04) are shown in the function code dropdown</li>
            <li>Write operations are done via the "Write Value..." button</li>
        </ul>
        """
    
    def _get_write_functions(self):
        """Get write functions content"""
        return """
        <h2>Write Functions</h2>
        <table border="1" cellpadding="5">
        <tr><th>Code</th><th>Name</th><th>Description</th></tr>
        <tr><td>05</td><td>Write Single Coil</td><td>Write single coil (True/False)</td></tr>
        <tr><td>06</td><td>Write Single Register</td><td>Write single register (0-65535)</td></tr>
        <tr><td>0F (15)</td><td>Write Multiple Coils</td><td>Write multiple coils</td></tr>
        <tr><td>10 (16)</td><td>Write Multiple Registers</td><td>Write multiple registers</td></tr>
        </table>
        <p><b>Usage:</b></p>
        <ul>
            <li>Select write function code in the "Write Value..." dialog</li>
            <li>Write functions are not shown in session function code dropdown</li>
            <li>All write operations are done via the "Write Value..." button</li>
        </ul>
        """
    
    def _get_addressing(self):
        """Get addressing content"""
        return """
        <h2>Modbus Addressing</h2>
        <p>Modbus uses 0-based addresses. Some devices use 1-based addresses in documentation:</p>
        <table border="1" cellpadding="5">
        <tr><th>Address Type</th><th>Documentation Range</th><th>Application Range</th></tr>
        <tr><td>Coils</td><td>00001-09999</td><td>0-9998</td></tr>
        <tr><td>Discrete Inputs</td><td>10001-19999</td><td>0-9998</td></tr>
        <tr><td>Holding Registers</td><td>40001-49999</td><td>0-9998</td></tr>
        <tr><td>Input Registers</td><td>30001-39999</td><td>0-9998</td></tr>
        </table>
        <p><b>Example:</b> If documentation says "Holding Register 40001", use address 0 in the application.</p>
        """
    
    def _get_function_data_types(self):
        """Get function data types content"""
        return """
        <h2>Data Types for Function Codes</h2>
        <p>The application supports the following data types:</p>
        <table border="1" cellpadding="5">
        <tr><th>Data Type</th><th>Description</th><th>Registers</th></tr>
        <tr><td>BOOL</td><td>Boolean (1 bit)</td><td>1 bit</td></tr>
        <tr><td>UINT16</td><td>16-bit unsigned integer</td><td>1 register</td></tr>
        <tr><td>INT16</td><td>16-bit signed integer</td><td>1 register</td></tr>
        <tr><td>UINT32</td><td>32-bit unsigned integer</td><td>2 registers</td></tr>
        <tr><td>INT32 (DINT)</td><td>32-bit signed integer (also called DINT)</td><td>2 registers</td></tr>
        <tr><td>FLOAT32</td><td>32-bit floating point</td><td>2 registers</td></tr>
        </table>
        <p><b>Important:</b> Multi-register types (INT32, UINT32, FLOAT32) use 2 registers. Make sure to read enough registers!</p>
        """
    
    def _get_frame_analyzer(self):
        """Get frame analyzer content"""
        return """
        <h2>Frame Analyzer</h2>
        <p>To analyze Modbus communication and diagnose issues:</p>
        <ul>
            <li>Go to <b>View → Frame Analyzer...</b></li>
            <li>The analyzer shows all TX/RX frames in a table with timestamps, direction, slave ID, function codes, and results</li>
            <li>Click on a frame to see detailed information (raw hex, decoded info, error descriptions)</li>
            <li><b>Statistics tab:</b> View aggregated statistics:
                <ul>
                    <li>Total requests/responses, timeouts per slave, CRC errors, average response times</li>
                </ul>
            </li>
            <li><b>Diagnostics tab:</b> See automatic findings:
                <ul>
                    <li>Many timeouts on a slave (check cable/ID/baudrate)</li>
                    <li>ID conflicts (multiple devices responding to same ID)</li>
                    <li>Consistent exceptions (wrong function code or unsupported function)</li>
                </ul>
            </li>
            <li>Use filters to focus on specific issues (errors only, specific slave ID, function code, etc.)</li>
            <li>This helps answer: "What's actually happening on the bus?" and "Why is it failing?"</li>
        </ul>
        """
    
    def _get_snapshots_compare(self):
        """Get snapshots and compare content"""
        return """
        <h2>Snapshots & Compare</h2>
        <p>To capture and compare installation states:</p>
        <p><b>Take Snapshot:</b></p>
        <ul>
            <li>Go to <b>Snapshots → Take Snapshot...</b></li>
            <li>Choose scope: Current session or all sessions</li>
            <li>Add a name and optional note (e.g., "Before parameter change")</li>
            <li>Snapshots capture all current values from active sessions</li>
        </ul>
        <p><b>Manage Snapshots:</b></p>
        <ul>
            <li>Go to <b>Snapshots → Manage Snapshots...</b></li>
            <li>View all snapshots with details (timestamp, scope, number of values)</li>
            <li>Select 2 snapshots (hold Ctrl and click) and click "Compare..." to see differences</li>
            <li>Export snapshots or comparisons to CSV for documentation</li>
            <li>Delete old snapshots</li>
        </ul>
        <p><b>Compare View:</b></p>
        <ul>
            <li>See side-by-side comparison with changed values highlighted</li>
            <li>View numeric differences and percentages</li>
            <li>Filter to show only changed values</li>
            <li>Export diff to CSV</li>
        </ul>
        <p>Perfect for: "It worked yesterday - what's different now?" or documenting parameter changes</p>
        """
    
    def _get_multi_view(self):
        """Get multi-view content"""
        return """
        <h2>Multi-view</h2>
        <p>To see multiple sessions simultaneously side by side:</p>
        <ol>
            <li>Go to <b>View → Manage Multi-view...</b></li>
            <li>Create groups and add sessions to each group</li>
            <li>Activate <b>View → Multi-view</b> to see all groups side by side</li>
            <li>Click on a group in the connection tree to focus on it</li>
        </ol>
        <p><b>Features:</b></p>
        <ul>
            <li>Each group is displayed in its own column</li>
            <li>Sessions can only be in one group at a time</li>
            <li>Switch between single-view and multi-view via <b>View → Multi-view</b></li>
            <li>Multi-view configuration is saved with projects</li>
        </ul>
        """
    
    def _get_device_scanner_advanced(self):
        """Get device scanner advanced content"""
        return """
        <h2>Device Scanner</h2>
        <p>Use <b>Connection → Device Scanner...</b> to automatically discover Modbus devices.</p>
        <p><b>RTU Scanner:</b></p>
        <ul>
            <li>Discover devices on a serial bus by scanning device IDs</li>
            <li>Configure COM port and serial settings</li>
            <li>Set device ID range to scan (default: 1-247)</li>
            <li>Results show available register types and active addresses</li>
        </ul>
        <p><b>TCP Scanner:</b></p>
        <ul>
            <li>Discover devices on a network by scanning IP addresses, ports, and device IDs</li>
            <li>Enter IP range (e.g., "192.168.1.1-254" or CIDR notation)</li>
            <li>Enter ports to scan (e.g., "502" or "502,5020")</li>
            <li>Results show which devices respond and what data is available</li>
        </ul>
        <p><b>Features:</b></p>
        <ul>
            <li><b>Save as PDF:</b> Export device information to a PDF file</li>
            <li><b>Import Connection/Session:</b> Right-click on found devices to automatically import them</li>
            <li>Note: Only addresses with active values are shown (non-zero for registers, True for coils)</li>
        </ul>
        """
    
    def _get_connection_problems(self):
        """Get connection problems content"""
        return """
        <h2>Connection Problems</h2>
        <p><b>TCP - "Could not connect":</b></p>
        <ul>
            <li>Check that the IP address and port are correct</li>
            <li>Check that the Modbus server is running (or start the simulator via <b>View → Modbus Simulator...</b>)</li>
            <li>Check firewall settings</li>
            <li>Try to ping the IP address</li>
            <li>For simulator: Use port 5020 instead of standard 502</li>
        </ul>
        <p><b>RTU - "Could not connect":</b></p>
        <ul>
            <li>Check that the COM port exists (see Device Manager)</li>
            <li>Check that the port is not used by another program</li>
            <li>Check that baudrate, parity, stop bits match the device</li>
            <li>Try restarting the computer if the port is locked</li>
            <li><b>For simulator:</b> You must first create a COM port pair with a serial port emulator (e.g. com0com)</li>
        </ul>
        <p><b>Code 52 error (com0com):</b></p>
        <ul>
            <li>This happens when Windows cannot verify the driver signature</li>
            <li><b>Solution 1:</b> Disable driver signature enforcement (see Windows recovery options)</li>
            <li><b>Solution 2:</b> Use Virtual Serial Port Driver (paid solution with signed drivers)</li>
            <li><b>Solution 3:</b> Test with physical RTU equipment instead of simulator</li>
        </ul>
        """
    
    def _get_simulator_problems(self):
        """Get simulator problems content"""
        return """
        <h2>Simulator Problems</h2>
        <p><b>Simulator does not start:</b></p>
        <ul>
            <li>Check that the port is not already in use (TCP port or COM port)</li>
            <li>For RTU: Check that the COM port exists and is available</li>
            <li>See the log file for detailed error messages</li>
            <li>Try restarting the application</li>
        </ul>
        <p><b>Cannot connect to simulator:</b></p>
        <ul>
            <li>Check that the simulator is actually running (see status in simulator dialog)</li>
            <li>For TCP: Use the same port as the simulator (e.g. 5020)</li>
            <li>For RTU: Use the opposite COM port (if simulator on COM10, connect to COM11)</li>
            <li>Check that Slave ID matches (default is 1)</li>
        </ul>
        """
    
    def _get_polling_problems(self):
        """Get polling problems content"""
        return """
        <h2>Polling Problems</h2>
        <p><b>"Timeout" error:</b></p>
        <ul>
            <li>Device is not responding - check the connection</li>
            <li>Slave ID is incorrect (use 1 for simulator)</li>
            <li>Function code is not supported by the device</li>
            <li>Address is outside the device's range</li>
            <li>Check that the simulator is still running</li>
        </ul>
        <p><b>"Exception" error:</b></p>
        <ul>
            <li>Function code not supported (exception code 01)</li>
            <li>Incorrect address (exception code 02)</li>
            <li>Incorrect value (exception code 03)</li>
            <li>Server error (exception code 04)</li>
        </ul>
        """
    
    def _get_tag_problems(self):
        """Get tag problems content"""
        return """
        <h2>Tag Problems</h2>
        <p><b>Tags do not appear in the table:</b></p>
        <ul>
            <li>Check that tag's address_type matches session's function code:
                <ul>
                    <li>Function 03 (Read Holding Registers) → address_type must be "Holding Register"</li>
                    <li>Function 04 (Read Input Registers) → address_type must be "Input Register"</li>
                    <li>Function 01 (Read Coils) → address_type must be "Coil"</li>
                    <li>Function 02 (Read Discrete Inputs) → address_type must be "Discrete Input"</li>
                </ul>
            </li>
            <li>If no tags match, raw data is displayed instead</li>
            <li>Check that tag address is within session's read range</li>
            <li>For INT32/UINT32/FLOAT32 tags: Make sure session reads enough registers (minimum tag.address + 1)</li>
        </ul>
        <p><b>INT32/DINT values look incorrect:</b></p>
        <ul>
            <li>Check that Byte Order is correct (Big Endian is default)</li>
            <li>Check that session reads enough registers (INT32 uses 2 registers)</li>
            <li>Check that tag address is correct (INT32 starts at tag.address and also uses tag.address+1)</li>
        </ul>
        """
    
    def _get_scanner_issues(self):
        """Get scanner issues content"""
        return """
        <h2>Device Scanner Issues</h2>
        <p><b>RTU Scanner does not find devices:</b></p>
        <ul>
            <li>Check that the COM port is correct and available</li>
            <li>Check that baudrate, parity, stop bits match the device</li>
            <li>Try a smaller device ID range (e.g. 1-10) to speed up scanning</li>
            <li>Some devices may not respond to all function codes - this is normal</li>
            <li>Note: Scanner only shows addresses with active values (non-zero for registers, True for coils)</li>
        </ul>
        <p><b>TCP Scanner does not find devices:</b></p>
        <ul>
            <li>Check that the IP range is correct and devices are on the network</li>
            <li>Verify that the ports are correct (typically 502 for Modbus TCP)</li>
            <li>Check firewall settings - Modbus TCP uses port 502 by default</li>
            <li>Try a smaller IP range first (e.g., "192.168.1.1-10") to speed up scanning</li>
            <li>Some devices may not respond to all function codes - this is normal</li>
            <li>Note: Scanner only shows addresses with active values (non-zero for registers, True for coils)</li>
        </ul>
        """
    
    def _get_best_practices(self):
        """Get best practices content"""
        return """
        <h2>Best Practices</h2>
        <ul>
            <li>Start with slow poll interval (1000ms+) and increase gradually</li>
            <li>Use named connections to keep track of multiple devices</li>
            <li>Save projects regularly to preserve configuration</li>
            <li>Use log viewer (<b>View → Show Log</b>) to verify that messages look correct</li>
            <li>Use the simulator (<b>View → Modbus Simulator...</b>) to test before connecting to real equipment</li>
            <li>Test write operations on simulator first before writing to real devices</li>
            <li>Use tags to organize and document your Modbus addresses</li>
            <li>Save frequently used tag sets as templates for reuse</li>
        </ul>
        """
    
    def _get_performance(self):
        """Get performance content"""
        return """
        <h2>Performance</h2>
        <ul>
            <li>RTU: Only one request at a time per COM port</li>
            <li>TCP: Multiple sessions can run in parallel, but one request per connection</li>
            <li>Slow poll interval = less load on network/device</li>
            <li>Use multi-view to monitor multiple devices simultaneously</li>
            <li>For RTU: Keep poll intervals reasonable to avoid bus congestion</li>
            <li>For TCP: Multiple connections can run in parallel for better performance</li>
        </ul>
        """
    
    def _get_multi_view_tips(self):
        """Get multi-view tips content"""
        return """
        <h2>Multi-view Tips</h2>
        <ul>
            <li>Create groups with related sessions to view them together</li>
            <li>Each group is displayed in its own column side by side</li>
            <li>Sessions can only be in one group at a time</li>
            <li>Switch between single-view and multi-view via <b>View → Multi-view</b></li>
            <li>Click on a group in the connection tree to focus on it</li>
            <li>Multi-view configuration is saved with projects</li>
        </ul>
        """
    
    def _get_tag_management_tips(self):
        """Get tag management tips content"""
        return """
        <h2>Tag Management Tips</h2>
        <ul>
            <li>Tags provide names and data types to your Modbus addresses</li>
            <li>Use INT32 (DINT) for 32-bit signed integers (2 registers)</li>
            <li>Use UINT32 for 32-bit unsigned integers (2 registers)</li>
            <li>Use FLOAT32 for floating point values (2 registers)</li>
            <li>The HEX column shows hexadecimal representation of the value</li>
            <li>Scaling allows converting raw values to physical units (e.g. temperature)</li>
            <li><b>Important:</b> Tag's address_type MUST match session's function code, otherwise the tag is ignored</li>
            <li>Save frequently used tag sets as templates for reuse</li>
            <li>Import register overviews from suppliers (CSV/Excel)</li>
            <li>Export templates for use in other systems or BMS projects</li>
        </ul>
        """
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        Theme.apply_to_widget(self)
