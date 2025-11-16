"""Help dialog with user guide"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextBrowser, QTabWidget, QWidget
from PyQt6.QtCore import Qt


class HelpDialog(QDialog):
    """Help dialog with user guide"""
    
    def __init__(self, parent=None):
        """Initialize help dialog"""
        super().__init__(parent)
        self.setWindowTitle("Hjælp - Modbus Tester")
        self.setModal(True)
        self.setMinimumSize(700, 600)
        
        self._setup_ui()
    
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
        <h2>Kom i gang</h2>
        <h3>1. Opret en forbindelse</h3>
        <p>Gå til <b>Forbindelse → Ny forbindelse...</b> eller klik på "Ny forbindelse" i toolbar.</p>
        <p><b>For TCP:</b></p>
        <ul>
            <li>Navn: Vælg et beskrivende navn (fx "PLC1")</li>
            <li>Host/IP: Indtast IP-adressen (fx 127.0.0.1)</li>
            <li>Port: Typisk 502 for Modbus TCP</li>
            <li>Timeout: 3 sekunder (standard)</li>
        </ul>
        <p><b>For RTU:</b></p>
        <ul>
            <li>Navn: Vælg et beskrivende navn (fx "RS485 Bus")</li>
            <li>Port: Vælg COM-port (fx COM1)</li>
            <li>Baudrate: Typisk 9600, 19200, eller 38400</li>
            <li>Parity: N (None), E (Even), eller O (Odd)</li>
            <li>Stop bits: 1 eller 2</li>
            <li>Data bits: 7 eller 8</li>
        </ul>
        
        <h3>2. Opret en session</h3>
        <p>Gå til <b>Session → Ny session...</b> eller klik på "Ny session" i toolbar.</p>
        <p>Konfigurer sessionen:</p>
        <ul>
            <li><b>Forbindelse:</b> Vælg den forbindelse du lige oprettede</li>
            <li><b>Slave ID:</b> Modbus slave/unit ID (typisk 1-247)</li>
            <li><b>Function Code:</b> Vælg funktion (01-04 for læs, 05-06, 0F-10 for skriv)</li>
            <li><b>Startadresse:</b> Startadresse for læsning/skrivning</li>
            <li><b>Antal:</b> Antal coils/registers</li>
            <li><b>Poll-interval:</b> Hvor ofte data skal læses (i millisekunder)</li>
        </ul>
        
        <h3>3. Start polling</h3>
        <p>Klik på <b>"Start"</b> knappen i session tab'en for at begynde at læse data.</p>
        <p>Data vil blive vist i tabellen nedenfor med:</p>
        <ul>
            <li>Adresse</li>
            <li>Navn (hvis tags er defineret)</li>
            <li>Rå værdi</li>
            <li>Skaleret værdi</li>
            <li>Enhed</li>
            <li>Status (OK, Timeout, Error, etc.)</li>
        </ul>
        """)
        tabs.addTab(getting_started, "Kom i gang")
        
        # Function Codes tab
        function_codes = QTextBrowser()
        function_codes.setReadOnly(True)
        function_codes.setHtml("""
        <h2>Modbus Function Codes</h2>
        <h3>Læs funktioner:</h3>
        <table border="1" cellpadding="5">
        <tr><th>Code</th><th>Navn</th><th>Beskrivelse</th></tr>
        <tr><td>01</td><td>Read Coils</td><td>Læs coils (outputs)</td></tr>
        <tr><td>02</td><td>Read Discrete Inputs</td><td>Læs discrete inputs</td></tr>
        <tr><td>03</td><td>Read Holding Registers</td><td>Læs holding registers (read/write)</td></tr>
        <tr><td>04</td><td>Read Input Registers</td><td>Læs input registers (read-only)</td></tr>
        </table>
        
        <h3>Skriv funktioner:</h3>
        <table border="1" cellpadding="5">
        <tr><th>Code</th><th>Navn</th><th>Beskrivelse</th></tr>
        <tr><td>05</td><td>Write Single Coil</td><td>Skriv én coil</td></tr>
        <tr><td>06</td><td>Write Single Register</td><td>Skriv ét register</td></tr>
        <tr><td>0F (15)</td><td>Write Multiple Coils</td><td>Skriv flere coils</td></tr>
        <tr><td>10 (16)</td><td>Write Multiple Registers</td><td>Skriv flere registers</td></tr>
        </table>
        
        <h3>Adressering:</h3>
        <p>Modbus bruger 0-baserede adresser. Nogle enheder bruger 1-baserede adresser i dokumentationen:</p>
        <ul>
            <li>Coils: 00001-09999 (0-9998 i applikationen)</li>
            <li>Discrete Inputs: 10001-19999 (0-9998 i applikationen)</li>
            <li>Holding Registers: 40001-49999 (0-9998 i applikationen)</li>
            <li>Input Registers: 30001-39999 (0-9998 i applikationen)</li>
        </ul>
        """)
        tabs.addTab(function_codes, "Function Codes")
        
        # Troubleshooting tab
        troubleshooting = QTextBrowser()
        troubleshooting.setReadOnly(True)
        troubleshooting.setHtml("""
        <h2>Fejlsøgning</h2>
        <h3>Forbindelsesproblemer</h3>
        <p><b>TCP - "Kunne ikke forbinde":</b></p>
        <ul>
            <li>Tjek at IP-adressen og porten er korrekt</li>
            <li>Tjek at Modbus serveren kører</li>
            <li>Tjek firewall indstillinger</li>
            <li>Prøv at ping IP-adressen</li>
        </ul>
        
        <p><b>RTU - "Kunne ikke forbinde":</b></p>
        <ul>
            <li>Tjek at COM-porten findes (se Device Manager)</li>
            <li>Tjek at porten ikke bruges af et andet program</li>
            <li>Tjek baudrate, parity, stop bits matcher enheden</li>
            <li>Prøv at genstarte computeren hvis porten er låst</li>
        </ul>
        
        <h3>Polling problemer</h3>
        <p><b>"Timeout" fejl:</b></p>
        <ul>
            <li>Enheden svarer ikke - tjek forbindelsen</li>
            <li>Slave ID er forkert</li>
            <li>Function code er ikke understøttet af enheden</li>
            <li>Adressen er uden for enhedens range</li>
        </ul>
        
        <p><b>"Exception" fejl:</b></p>
        <ul>
            <li>Function code ikke understøttet (exception code 01)</li>
            <li>Forkert adresse (exception code 02)</li>
            <li>Forkert værdi (exception code 03)</li>
            <li>Server fejl (exception code 04)</li>
        </ul>
        
        <h3>Log viewer</h3>
        <p>Brug <b>Vis → Vis log</b> for at se detaljerede TX/RX beskeder med hexdump.</p>
        <p>Dette hjælper med at diagnosticere protokol problemer.</p>
        """)
        tabs.addTab(troubleshooting, "Fejlsøgning")
        
        # Tips tab
        tips = QTextBrowser()
        tips.setReadOnly(True)
        tips.setHtml("""
        <h2>Tips og Tricks</h2>
        <h3>Bedste praksis</h3>
        <ul>
            <li>Start med langsom poll-interval (1000ms+) og øg gradvist</li>
            <li>Brug navngivne forbindelser for at holde styr på flere enheder</li>
            <li>Gem projekter regelmæssigt for at bevare konfiguration</li>
            <li>Brug log viewer til at verificere at beskeder ser korrekte ud</li>
        </ul>
        
        <h3>Performance</h3>
        <ul>
            <li>RTU: Kun én request ad gangen per COM-port</li>
            <li>TCP: Flere sessions kan køre parallelt, men én request per connection</li>
            <li>Langsom poll-interval = mindre belastning på netværk/enhed</li>
        </ul>
        
        <h3>Skrivning</h3>
        <ul>
            <li>Dobbeltklik på en værdi i tabellen for at skrive (hvis function code understøtter det)</li>
            <li>Holding registers kan skrives (function 03)</li>
            <li>Coils kan skrives (function 01)</li>
            <li>Input registers kan IKKE skrives (read-only)</li>
        </ul>
        """)
        tabs.addTab(tips, "Tips")
        
        layout.addWidget(tabs)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = QPushButton("Luk")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
