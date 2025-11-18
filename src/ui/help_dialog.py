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
        <h3>1. Start en simulator (valgfrit - til test)</h3>
        <p>For at teste applikationen kan du starte en simuleret Modbus server direkte fra appen:</p>
        <ul>
            <li>Gå til <b>Vis → Modbus Simulator...</b></li>
            <li>Vælg <b>TCP</b> eller <b>RTU</b> tab</li>
            <li>Konfigurer indstillingerne (port, baudrate, etc.)</li>
            <li>Klik på <b>"Start TCP Simulator"</b> eller <b>"Start RTU Simulator"</b></li>
            <li>Simulatoren kører nu i baggrunden og kan bruges til test</li>
        </ul>
        
        <p><b>Vigtigt for RTU test:</b></p>
        <p>For at teste RTU forbindelser skal du først oprette et virtuelt COM-port par med en serial port emulator:</p>
        <ul>
            <li><b>Download og installer en serial port emulator:</b>
                <ul>
                    <li><b>com0com</b> (gratis, open source) - Download fra: https://sourceforge.net/projects/com0com/</li>
                    <li><b>Virtual Serial Port Driver</b> (betalingsløsning, signerede drivers) - Download fra: https://www.virtual-serial-port.org/</li>
                    <li>Eller en anden serial port emulator efter eget valg</li>
                </ul>
            </li>
            <li><b>Opret et COM-port par:</b>
                <ul>
                    <li>Efter installation, åbn emulator programmet</li>
                    <li>Opret et par af virtuelle COM-porte (fx COM10 ↔ COM11)</li>
                    <li>Disse porte vil fungere som om de er forbundet med et kabel</li>
                </ul>
            </li>
            <li><b>Brug COM-port parret:</b>
                <ul>
                    <li>Start RTU simulatoren på den ene port (fx COM10) via <b>Vis → Modbus Simulator...</b></li>
                    <li>Opret en RTU forbindelse i appen til den anden port (fx COM11)</li>
                    <li>Nu kan du teste RTU kommunikation mellem simulator og applikation</li>
                </ul>
            </li>
            <li><b>Bemærk:</b> Hvis du får Code 52 fejl med com0com, skal du muligvis deaktivere driver signature enforcement i Windows (se "Fejlsøgning" tab)</li>
        </ul>
        <p><b>Testdata i simulatoren:</b></p>
        <ul>
            <li>Holding registers (0-9): 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000</li>
            <li>Holding registers (20-31): DINT (INT32) test værdier:
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
            <li>Input registers (20-31): DINT (INT32) test værdier:
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
        
        <h3>2. Opret en forbindelse</h3>
        <p>Gå til <b>Forbindelse → Ny forbindelse...</b> eller klik på "Ny forbindelse" i toolbar.</p>
        <p><b>For TCP:</b></p>
        <ul>
            <li>Navn: Vælg et beskrivende navn (fx "PLC1")</li>
            <li>Host/IP: Indtast IP-adressen (fx 127.0.0.1 for simulator)</li>
            <li>Port: Typisk 502 for Modbus TCP (eller 5020 for simulator)</li>
            <li>Timeout: 3 sekunder (standard)</li>
        </ul>
        <p><b>For RTU:</b></p>
        <ul>
            <li>Navn: Vælg et beskrivende navn (fx "RS485 Bus")</li>
            <li>Port: Vælg COM-port (fx COM10 eller COM11)</li>
            <li>Baudrate: Typisk 9600, 19200, eller 38400</li>
            <li>Parity: N (None), E (Even), eller O (Odd)</li>
            <li>Stop bits: 1 eller 2</li>
            <li>Data bits: 7 eller 8</li>
        </ul>
        <p><b>Tip:</b> Forbindelserne grupperes automatisk efter type (TCP/RTU) i connection tree'en.</p>
        
        <h3>3. Opret en session</h3>
        <p>Gå til <b>Session → Ny session...</b> eller klik på "Ny session" i toolbar.</p>
        <p>Konfigurer sessionen:</p>
        <ul>
            <li><b>Forbindelse:</b> Vælg den forbindelse du lige oprettede</li>
            <li><b>Slave ID:</b> Modbus slave/unit ID (typisk 1-247, brug 1 for simulator)</li>
            <li><b>Function Code:</b> Vælg funktion (01-04 for læs, 05-06, 0F-10 for skriv)</li>
            <li><b>Startadresse:</b> Startadresse for læsning/skrivning (start med 0 for simulator)</li>
            <li><b>Antal:</b> Antal coils/registers (fx 10)</li>
            <li><b>Poll-interval:</b> Hvor ofte data skal læses (i millisekunder, fx 1000)</li>
        </ul>
        
        <h3>4. Administrer Tags (valgfrit)</h3>
        <p>For at få navne, datatyper og skalering på dine data:</p>
        <ul>
            <li>Klik på <b>"Administrer Tags..."</b> knappen i session tab'en</li>
            <li>Klik på <b>"Tilføj Tag"</b> for at oprette en ny tag</li>
            <li>Konfigurer tag'en:
                <ul>
                    <li><b>Adressetype:</b> Skal matche session's function code (Holding Register for function 03, Input Register for function 04)</li>
                    <li><b>Adresse:</b> Register adressen</li>
                    <li><b>Navn:</b> Et beskrivende navn (fx "Temperature")</li>
                    <li><b>Datatype:</b> Vælg datatype (UINT16, INT16, INT32/DINT, UINT32, FLOAT32, BOOL)</li>
                    <li><b>Byte Order:</b> Big Endian (standard), Little Endian, eller Swapped</li>
                    <li><b>Skalering:</b> Skaleringsfaktor og offset (valgfrit)</li>
                    <li><b>Enhed:</b> Enhedsbetegnelse (fx "°C", "bar", "%")</li>
                </ul>
            </li>
            <li><b>Vigtigt:</b> Tags med forkert address_type vil blive ignoreret. Sørg for at address_type matcher function code!</li>
        </ul>
        
        <h3>5. Start polling</h3>
        <p>Klik på <b>"Start"</b> knappen i session tab'en for at begynde at læse data.</p>
        <p>Data vil blive vist i tabellen nedenfor med:</p>
        <ul>
            <li><b>Adresse:</b> Register adressen</li>
            <li><b>Navn:</b> Tag navn (hvis defineret) eller "Address X"</li>
            <li><b>Rå værdi:</b> Den rå værdi fra Modbus (efter datatype dekodning)</li>
            <li><b>HEX:</b> Hexadecimal repræsentation af værdien</li>
            <li><b>Skaleret værdi:</b> Værdien efter skalering (hvis tag har skalering)</li>
            <li><b>Enhed:</b> Enhedsbetegnelse fra tag (fx "°C")</li>
            <li><b>Status:</b> OK, Timeout, Error, etc.</li>
        </ul>
        
        <h3>6. Multi-view (valgfrit)</h3>
        <p>For at se flere sessions samtidig side om side:</p>
        <ul>
            <li>Gå til <b>Vis → Administrer multi-view...</b></li>
            <li>Opret grupper og tilføj sessions til hver gruppe</li>
            <li>Aktiver <b>Vis → Multi-view</b> for at se alle grupper side om side</li>
            <li>Klik på en gruppe i connection tree'en for at fokusere på den</li>
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
        
        <h3>Datatyper:</h3>
        <p>Applikationen understøtter følgende datatyper:</p>
        <table border="1" cellpadding="5">
        <tr><th>Datatype</th><th>Beskrivelse</th><th>Registre</th></tr>
        <tr><td>BOOL</td><td>Boolean (1 bit)</td><td>1 bit</td></tr>
        <tr><td>UINT16</td><td>16-bit unsigned integer</td><td>1 register</td></tr>
        <tr><td>INT16</td><td>16-bit signed integer</td><td>1 register</td></tr>
        <tr><td>UINT32</td><td>32-bit unsigned integer</td><td>2 registre</td></tr>
        <tr><td>INT32 (DINT)</td><td>32-bit signed integer (også kaldet DINT)</td><td>2 registre</td></tr>
        <tr><td>FLOAT32</td><td>32-bit floating point</td><td>2 registre</td></tr>
        </table>
        <p><b>Vigtigt:</b> Multi-register typer (INT32, UINT32, FLOAT32) bruger 2 registre. Sørg for at læse nok registre!</p>
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
            <li>Tjek at Modbus serveren kører (eller start simulatoren via <b>Vis → Modbus Simulator...</b>)</li>
            <li>Tjek firewall indstillinger</li>
            <li>Prøv at ping IP-adressen</li>
            <li>For simulator: Brug port 5020 i stedet for standard 502</li>
        </ul>
        
        <p><b>RTU - "Kunne ikke forbinde":</b></p>
        <ul>
            <li>Tjek at COM-porten findes (se Device Manager)</li>
            <li>Tjek at porten ikke bruges af et andet program</li>
            <li>Tjek baudrate, parity, stop bits matcher enheden</li>
            <li>Prøv at genstarte computeren hvis porten er låst</li>
            <li><b>For simulator:</b> Du skal først oprette et COM-port par med en serial port emulator (fx com0com):
                <ul>
                    <li>Opret et par (fx COM10 ↔ COM11)</li>
                    <li>Start RTU simulatoren på én port (fx COM10) via <b>Vis → Modbus Simulator...</b></li>
                    <li>Forbind fra appen til den anden port (fx COM11)</li>
                </ul>
            </li>
            <li>Hvis du får Code 52 fejl med com0com, skal du muligvis deaktivere driver signature enforcement i Windows (se nedenfor)</li>
        </ul>
        
        <p><b>Code 52 fejl (com0com):</b></p>
        <ul>
            <li>Dette sker når Windows ikke kan verificere driver signaturen</li>
            <li><b>Løsning 1:</b> Deaktiver driver signature enforcement:
                <ul>
                    <li>Windows + I → System → Recovery → Advanced startup → Restart now</li>
                    <li>Troubleshoot → Advanced options → Startup Settings → Restart</li>
                    <li>Tryk 7 eller F7 for "Disable driver signature enforcement"</li>
                    <li>Efter genstart: Højreklik på com0com enheder i Device Manager → Update driver</li>
                </ul>
            </li>
            <li><b>Løsning 2:</b> Brug Virtual Serial Port Driver (betalingsløsning med signerede drivers)</li>
            <li><b>Løsning 3:</b> Test med fysisk RTU udstyr i stedet for simulator</li>
        </ul>
        
        <h3>Simulator problemer</h3>
        <p><b>Simulatoren starter ikke:</b></p>
        <ul>
            <li>Tjek at porten ikke allerede bruges (TCP port eller COM port)</li>
            <li>For RTU: Tjek at COM-porten findes og er tilgængelig</li>
            <li>Se log filen for detaljerede fejlbeskeder</li>
            <li>Prøv at genstarte applikationen</li>
        </ul>
        
        <p><b>Kan ikke forbinde til simulator:</b></p>
        <ul>
            <li>Tjek at simulatoren faktisk kører (se status i simulator dialog'en)</li>
            <li>For TCP: Brug samme port som simulatoren (fx 5020)</li>
            <li>For RTU: Brug den modsatte COM-port (hvis simulator på COM10, forbind til COM11)</li>
            <li>Tjek at Slave ID matcher (standard er 1)</li>
        </ul>
        
        <h3>Polling problemer</h3>
        <p><b>"Timeout" fejl:</b></p>
        <ul>
            <li>Enheden svarer ikke - tjek forbindelsen</li>
            <li>Slave ID er forkert (brug 1 for simulator)</li>
            <li>Function code er ikke understøttet af enheden</li>
            <li>Adressen er uden for enhedens range</li>
            <li>Tjek at simulatoren stadig kører</li>
        </ul>
        
        <p><b>"Exception" fejl:</b></p>
        <ul>
            <li>Function code ikke understøttet (exception code 01)</li>
            <li>Forkert adresse (exception code 02)</li>
            <li>Forkert værdi (exception code 03)</li>
            <li>Server fejl (exception code 04)</li>
        </ul>
        
        <h3>Tag problemer</h3>
        <p><b>Tags vises ikke i tabellen:</b></p>
        <ul>
            <li>Tjek at tag's address_type matcher session's function code:
                <ul>
                    <li>Function 03 (Read Holding Registers) → address_type skal være "Holding Register"</li>
                    <li>Function 04 (Read Input Registers) → address_type skal være "Input Register"</li>
                    <li>Function 01 (Read Coils) → address_type skal være "Coil"</li>
                    <li>Function 02 (Read Discrete Inputs) → address_type skal være "Discrete Input"</li>
                </ul>
            </li>
            <li>Hvis ingen tags matcher, vises rå data i stedet</li>
            <li>Tjek at tag adressen er inden for session's startadresse og antal</li>
            <li>For INT32/UINT32/FLOAT32 tags: Sørg for at session læser nok registre (minimum tag.address + 1)</li>
        </ul>
        
        <p><b>INT32/DINT værdier ser forkerte ud:</b></p>
        <ul>
            <li>Tjek at Byte Order er korrekt (Big Endian er standard)</li>
            <li>Tjek at session læser nok registre (INT32 bruger 2 registre)</li>
            <li>Tjek at tag adressen er korrekt (INT32 starter ved tag.address og bruger også tag.address+1)</li>
        </ul>
        
        <h3>Multi-view problemer</h3>
        <p><b>Sessions vises ikke i multi-view:</b></p>
        <ul>
            <li>Tjek at sessions er tilføjet til grupper via <b>Vis → Administrer multi-view...</b></li>
            <li>Tjek at multi-view er aktiveret (<b>Vis → Multi-view</b> skal være markeret)</li>
            <li>Prøv at klikke på gruppen i connection tree'en</li>
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
            <li>Brug log viewer (<b>Vis → Vis log</b>) til at verificere at beskeder ser korrekte ud</li>
            <li>Brug simulatoren (<b>Vis → Modbus Simulator...</b>) til at teste før du forbinder til rigtigt udstyr</li>
        </ul>
        
        <h3>Multi-view</h3>
        <ul>
            <li>Opret grupper med relaterede sessions for at se dem sammen</li>
            <li>Hver gruppe vises i sin egen kolonne side om side</li>
            <li>Sessions kan kun være i én gruppe ad gangen</li>
            <li>Skift mellem single-view og multi-view via <b>Vis → Multi-view</b></li>
            <li>Klik på en gruppe i connection tree'en for at fokusere på den</li>
        </ul>
        
        <h3>Performance</h3>
        <ul>
            <li>RTU: Kun én request ad gangen per COM-port</li>
            <li>TCP: Flere sessions kan køre parallelt, men én request per connection</li>
            <li>Langsom poll-interval = mindre belastning på netværk/enhed</li>
            <li>Brug multi-view til at overvåge flere enheder samtidig</li>
        </ul>
        
        <h3>Tags og Datatyper</h3>
        <ul>
            <li>Tags giver navne og datatyper til dine Modbus adresser</li>
            <li>Brug INT32 (DINT) for 32-bit signed integers (2 registre)</li>
            <li>Brug UINT32 for 32-bit unsigned integers (2 registre)</li>
            <li>Brug FLOAT32 for floating point værdier (2 registre)</li>
            <li>HEX kolonnen viser hexadecimal repræsentation af værdien</li>
            <li>Skalering giver mulighed for at konvertere rå værdier til fysiske enheder (fx temperatur)</li>
            <li><b>Vigtigt:</b> Tag's address_type SKAL matche session's function code, ellers ignoreres tag'en</li>
        </ul>
        
        <h3>Skrivning</h3>
        <ul>
            <li>Dobbeltklik på en værdi i tabellen for at skrive (hvis function code understøtter det)</li>
            <li>Holding registers kan skrives (function 03)</li>
            <li>Coils kan skrives (function 01)</li>
            <li>Input registers kan IKKE skrives (read-only)</li>
        </ul>
        
        <h3>Simulator</h3>
        <ul>
            <li>Start simulatoren før du opretter forbindelser til den</li>
            <li>TCP simulator kører typisk på port 5020 (ikke standard 502)</li>
            <li><b>RTU simulator kræver et COM-port par:</b>
                <ul>
                    <li>Du skal først oprette et virtuelt COM-port par med en serial port emulator (fx com0com)</li>
                    <li>Opret et par (fx COM10 ↔ COM11)</li>
                    <li>Start simulatoren på den ene port (fx COM10)</li>
                    <li>Forbind fra appen til den anden port (fx COM11)</li>
                </ul>
            </li>
            <li>Simulatoren stopper automatisk når applikationen lukkes</li>
            <li>Du kan have både TCP og RTU simulator kørende samtidig</li>
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
