"""Help dialog with user guide"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser, QTabWidget, QWidget
from PyQt6.QtCore import Qt


class HelpDialog(QDialog):
    """Help dialog with user guide"""
    
    def __init__(self, parent=None):
        """Initialize help dialog"""
        super().__init__(parent)
        self.setWindowTitle("Help - Modbus Tester")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        self._setup_ui()
        self._apply_dark_theme()
    
    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tabs
        tabs = QTabWidget()
        
        # Getting Started tab
        getting_started = QTextBrowser()
        getting_started.setReadOnly(True)
        getting_started.setHtml("""
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
        
        <h3>2. Scan for RTU devices (optional)</h3>
        <p>If you're working with RTU devices and don't know the device IDs, you can use the RTU Device Scanner:</p>
        <ul>
            <li>Go to <b>Connection → RTU Device Scanner...</b></li>
            <li>Select the COM port and configure serial settings (baudrate, parity, etc.)</li>
            <li>Set the device ID range to scan (default: 1-247)</li>
            <li>Click <b>"Start Scan"</b> to automatically discover Modbus devices</li>
            <li>The scanner will find devices and show which register types are available</li>
            <li><b>Note:</b> Only addresses with active values are shown (coils/discrete inputs with value=1, registers with value≠0)</li>
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
            <li><b>Function Code:</b> Select function (01-04 for read, 05-06, 0F-10 for write)</li>
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
        
        <h3>7. Multi-view (optional)</h3>
        <p>To see multiple sessions simultaneously side by side:</p>
        <ul>
            <li>Go to <b>View → Manage Multi-view...</b></li>
            <li>Create groups and add sessions to each group</li>
            <li>Activate <b>View → Multi-view</b> to see all groups side by side</li>
            <li>Click on a group in the connection tree to focus on it</li>
        </ul>
        """)
        tabs.addTab(getting_started, "Getting Started")
        
        # Function Codes tab
        function_codes = QTextBrowser()
        function_codes.setReadOnly(True)
        function_codes.setHtml("""
        <h2>Modbus Function Codes</h2>
        <h3>Read functions:</h3>
        <table border="1" cellpadding="5">
        <tr><th>Code</th><th>Name</th><th>Description</th></tr>
        <tr><td>01</td><td>Read Coils</td><td>Read coils (outputs)</td></tr>
        <tr><td>02</td><td>Read Discrete Inputs</td><td>Read discrete inputs</td></tr>
        <tr><td>03</td><td>Read Holding Registers</td><td>Read holding registers (read/write)</td></tr>
        <tr><td>04</td><td>Read Input Registers</td><td>Read input registers (read-only)</td></tr>
        </table>
        
        <h3>Write functions:</h3>
        <table border="1" cellpadding="5">
        <tr><th>Code</th><th>Name</th><th>Description</th></tr>
        <tr><td>05</td><td>Write Single Coil</td><td>Write single coil</td></tr>
        <tr><td>06</td><td>Write Single Register</td><td>Write single register</td></tr>
        <tr><td>0F (15)</td><td>Write Multiple Coils</td><td>Write multiple coils</td></tr>
        <tr><td>10 (16)</td><td>Write Multiple Registers</td><td>Write multiple registers</td></tr>
        </table>
        
        <h3>Addressing:</h3>
        <p>Modbus uses 0-based addresses. Some devices use 1-based addresses in documentation:</p>
        <ul>
            <li>Coils: 00001-09999 (0-9998 in application)</li>
            <li>Discrete Inputs: 10001-19999 (0-9998 in application)</li>
            <li>Holding Registers: 40001-49999 (0-9998 in application)</li>
            <li>Input Registers: 30001-39999 (0-9998 in application)</li>
        </ul>
        
        <h3>Data Types:</h3>
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
        """)
        tabs.addTab(function_codes, "Function Codes")
        
        # Troubleshooting tab
        troubleshooting = QTextBrowser()
        troubleshooting.setReadOnly(True)
        troubleshooting.setHtml("""
        <h2>Troubleshooting</h2>
        <h3>Connection problems</h3>
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
            <li><b>For simulator:</b> You must first create a COM port pair with a serial port emulator (e.g. com0com):
                <ul>
                    <li>Create a pair (e.g. COM10 ↔ COM11)</li>
                    <li>Start the RTU simulator on one port (e.g. COM10) via <b>View → Modbus Simulator...</b></li>
                    <li>Connect from the app to the other port (e.g. COM11)</li>
                </ul>
            </li>
            <li>If you get Code 52 error with com0com, you may need to disable driver signature enforcement in Windows (see below)</li>
        </ul>
        
        <p><b>Code 52 error (com0com):</b></p>
        <ul>
            <li>This happens when Windows cannot verify the driver signature</li>
            <li><b>Solution 1:</b> Disable driver signature enforcement:
                <ul>
                    <li>Windows + I → System → Recovery → Advanced startup → Restart now</li>
                    <li>Troubleshoot → Advanced options → Startup Settings → Restart</li>
                    <li>Press 7 or F7 for "Disable driver signature enforcement"</li>
                    <li>After restart: Right-click on com0com devices in Device Manager → Update driver</li>
                </ul>
            </li>
            <li><b>Solution 2:</b> Use Virtual Serial Port Driver (paid solution with signed drivers)</li>
            <li><b>Solution 3:</b> Test with physical RTU equipment instead of simulator</li>
        </ul>
        
        <h3>Simulator problems</h3>
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
        
        <h3>Polling problems</h3>
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
        
        <h3>Tag problems</h3>
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
            <li>Check that tag address is within session's start address and quantity</li>
            <li>For INT32/UINT32/FLOAT32 tags: Make sure session reads enough registers (minimum tag.address + 1)</li>
        </ul>
        
        <p><b>INT32/DINT values look incorrect:</b></p>
        <ul>
            <li>Check that Byte Order is correct (Big Endian is default)</li>
            <li>Check that session reads enough registers (INT32 uses 2 registers)</li>
            <li>Check that tag address is correct (INT32 starts at tag.address and also uses tag.address+1)</li>
        </ul>
        
        <h3>Multi-view problems</h3>
        <p><b>Sessions do not appear in multi-view:</b></p>
        <ul>
            <li>Check that sessions are added to groups via <b>View → Manage Multi-view...</b></li>
            <li>Check that multi-view is activated (<b>View → Multi-view</b> must be checked)</li>
            <li>Try clicking on the group in the connection tree</li>
        </ul>
        
        <h3>RTU Device Scanner</h3>
        <p><b>Scanner does not find devices:</b></p>
        <ul>
            <li>Check that the COM port is correct and available</li>
            <li>Check that baudrate, parity, stop bits match the device</li>
            <li>Try a smaller device ID range (e.g. 1-10) to speed up scanning</li>
            <li>Some devices may not respond to all function codes - this is normal</li>
            <li>Note: Scanner only shows addresses with active values (non-zero for registers, True for coils)</li>
        </ul>
        
        <h3>Log viewer</h3>
        <p>Use <b>View → Show Log</b> to see detailed TX/RX messages with hexdump.</p>
        <p>This helps diagnose protocol problems.</p>
        """)
        tabs.addTab(troubleshooting, "Troubleshooting")
        
        # Tips tab
        tips = QTextBrowser()
        tips.setReadOnly(True)
        tips.setHtml("""
        <h2>Tips and Tricks</h2>
        <h3>Best practices</h3>
        <ul>
            <li>Start with slow poll interval (1000ms+) and increase gradually</li>
            <li>Use named connections to keep track of multiple devices</li>
            <li>Save projects regularly to preserve configuration</li>
            <li>Use log viewer (<b>View → Show Log</b>) to verify that messages look correct</li>
            <li>Use the simulator (<b>View → Modbus Simulator...</b>) to test before connecting to real equipment</li>
        </ul>
        
        <h3>Multi-view</h3>
        <ul>
            <li>Create groups with related sessions to view them together</li>
            <li>Each group is displayed in its own column side by side</li>
            <li>Sessions can only be in one group at a time</li>
            <li>Switch between single-view and multi-view via <b>View → Multi-view</b></li>
            <li>Click on a group in the connection tree to focus on it</li>
        </ul>
        
        <h3>Performance</h3>
        <ul>
            <li>RTU: Only one request at a time per COM port</li>
            <li>TCP: Multiple sessions can run in parallel, but one request per connection</li>
            <li>Slow poll interval = less load on network/device</li>
            <li>Use multi-view to monitor multiple devices simultaneously</li>
        </ul>
        
        <h3>Tags and Data Types</h3>
        <ul>
            <li>Tags provide names and data types to your Modbus addresses</li>
            <li>Use INT32 (DINT) for 32-bit signed integers (2 registers)</li>
            <li>Use UINT32 for 32-bit unsigned integers (2 registers)</li>
            <li>Use FLOAT32 for floating point values (2 registers)</li>
            <li>The HEX column shows hexadecimal representation of the value</li>
            <li>Scaling allows converting raw values to physical units (e.g. temperature)</li>
            <li><b>Important:</b> Tag's address_type MUST match session's function code, otherwise the tag is ignored</li>
        </ul>
        
        <h3>Writing</h3>
        <ul>
            <li>Double-click on a value in the table to write (if function code supports it)</li>
            <li>Holding registers can be written (function 03)</li>
            <li>Coils can be written (function 01)</li>
            <li>Input registers CANNOT be written (read-only)</li>
        </ul>
        
        <h3>Simulator</h3>
        <ul>
            <li>Start the simulator before creating connections to it</li>
            <li>TCP simulator typically runs on port 5020 (not standard 502)</li>
            <li><b>RTU simulator requires a COM port pair:</b>
                <ul>
                    <li>You must first create a virtual COM port pair with a serial port emulator (e.g. com0com)</li>
                    <li>Create a pair (e.g. COM10 ↔ COM11)</li>
                    <li>Start the simulator on one port (e.g. COM10)</li>
                    <li>Connect from the app to the other port (e.g. COM11)</li>
                </ul>
            </li>
            <li>The simulator stops automatically when the application closes</li>
            <li>You can have both TCP and RTU simulator running simultaneously</li>
        </ul>
        
        <h3>RTU Device Scanner</h3>
        <ul>
            <li>Use <b>Connection → RTU Device Scanner...</b> to automatically discover Modbus devices on a serial bus</li>
            <li>Configure COM port and serial settings to match your bus</li>
            <li>Set device ID range (default 1-247, but you can limit it for faster scanning)</li>
            <li>The scanner tests each device ID and identifies available register types</li>
            <li>Results show which addresses have active values (non-zero for registers, True for coils)</li>
            <li>Use the scanner to quickly identify device IDs and available data on an unknown RTU network</li>
        </ul>
        
        <h3>User Interface</h3>
        <ul>
            <li>The application uses a dark theme for reduced eye strain</li>
            <li>Connections and Sessions are organized in resizable panels with borders</li>
            <li>You can resize the splitter between Connections and Sessions panels</li>
            <li>Window position and splitter sizes are automatically saved and restored</li>
            <li>Use the log viewer (<b>View → Show Log</b>) to monitor all Modbus communication</li>
        </ul>
        """)
        tabs.addTab(tips, "Tips")
        
        layout.addWidget(tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
    
    def _apply_dark_theme(self):
        """Apply dark theme styling"""
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
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
            QTextBrowser {
                background-color: #252526;
                border: 1px solid #3e3e42;
                border-radius: 3px;
                color: #cccccc;
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
        """)
