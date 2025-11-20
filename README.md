# Modbus Tester

A Modbus master/simulator desktop application for testing Modbus RTU (RS-485/RS-232) and Modbus TCP/IP connections.

## Features

- **Modbus RTU (master)** via RS-485/RS-232
- **Modbus TCP (client/master)**
- **Multiple parallel sessions** with multi-view support
- **Read/write coils, discrete inputs, input registers and holding registers**
- **Integrated Modbus Simulator** - Start TCP/RTU simulators directly from the app
- **Device Scanner** - Automatically discover Modbus devices on RTU bus or TCP/IP network
  - **RTU Scanner** - Scan serial bus for device IDs and active registers
  - **TCP Scanner** - Scan network IP ranges and ports for Modbus TCP devices
  - **Export to PDF** - Save device information as PDF for documentation
  - **Import Connection/Session** - Right-click on found devices to automatically import them
- **Multi-view** - View multiple sessions side-by-side in groups
- **Tag Management** - Define custom tags with data types, scaling, and units
- **Data Types Support** - UINT16, INT16, UINT32, INT32 (DINT), FLOAT32, BOOL
- **HEX Display** - View hexadecimal representation of all values
- **Dark Theme** - Modern dark interface for reduced eye strain
- **Resizable Panels** - Adjustable splitter between Connections and Sessions
- **Auto-save UI Settings** - Window position and panel sizes are saved automatically
- **Comprehensive debugging**: hexdump, timestamps, log, status codes
- **Real-time data display** in tables
- **Manual write operations**
- **Project management** - Save and reopen configurations (including multi-view setup)

## Installation

```bash
pip install -r requirements.txt
```

## Running

### Main Application

```bash
python src/main.py
```

### Modbus Simulator (for testing)

**Recommended:** Use the integrated simulator in the app via **View → Modbus Simulator...**

Alternatively, you can run the simulator from the command line:

**TCP Simulator:**
```bash
python src/simulator/modbus_simulator.py --type tcp --host 127.0.0.1 --port 5020
```

**RTU Simulator:**
```bash
python src/simulator/modbus_simulator.py --type rtu --serial-port COM10 --baudrate 9600
```

**Or use the simple script:**
```bash
python start_rtu_simulator.py
```

This starts the RTU simulator on COM10 at 9600 baud.

The simulator has the following test data:
- **Holding registers (0-9)**: 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
- **Input registers (0-9)**: 50, 150, 250, 350, 450, 550, 650, 750, 850, 950
- **Coils (0-9)**: True, False, True, False, True, False, True, False, True, False
- **Discrete inputs (0-9)**: False, True, False, True, False, True, False, True, False, True

**Connection example:**
1. Start the application: `python src/main.py`
2. Start the simulator via **View → Modbus Simulator...** → Start TCP Simulator (port 5020)
3. Create a new TCP connection with:
   - Host: `127.0.0.1`
   - Port: `5020`
   - Slave ID: `1`
4. Create a session with:
   - Function code: `03` (Read Holding Registers)
   - Start address: `0`
   - Quantity: `10`
5. Start polling to see the data

**Multi-view:**
- Create groups via **View → Manage Multi-view...**
- Activate multi-view via **View → Multi-view**
- View multiple sessions side-by-side
- Multi-view configuration is saved with projects

**Device Scanner:**
- Go to **Connection → Device Scanner...**
- **RTU Scanner Tab:**
  - Select COM port and configure serial settings (baudrate, parity, etc.)
  - Set device ID range to scan (default: 1-247)
  - Click "Start Scan" to automatically discover Modbus devices on serial bus
- **TCP Scanner Tab:**
  - Enter IP range (e.g., "192.168.1.1-254" or "192.168.1.0/24" for CIDR notation)
  - Enter ports to scan (e.g., "502" or "502,5020" for multiple ports)
  - Set device ID range to scan (default: 1-247)
  - Click "Start Scan" to automatically discover Modbus TCP devices on network
- **Features:**
  - Results show available register types and active addresses
  - **Save as PDF:** Click "Save as PDF" button to export device information
  - **Import Connection:** Right-click on found device → "Import Connection" to create connection profile
  - **Import Session:** Right-click on found device → "Import Session" to create connection and session automatically
  - Note: Only addresses with active values are shown (non-zero for registers, True for coils)

**Tag Management:**
- Click "Manage Tags..." in a session tab
- Define custom tags with names, data types, byte order, scaling, and units
- Supports: UINT16, INT16, UINT32, INT32 (DINT), FLOAT32, BOOL
- Tags must match the session's function code (address_type)

**User Interface:**
- Dark theme for reduced eye strain
- Resizable panels - drag the splitter between Connections and Sessions
- Window position and panel sizes are automatically saved
- HEX column shows hexadecimal representation of values

## Build Executable (.exe)

To build a standalone .exe file:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Build executable
python build_exe.py
```

Or use the batch file:
```bash
build_exe.bat
```

The executable will be placed in `dist/ModbusTester.exe`

**Notes:**
- The executable is standalone and does not require Python installation
- First build may take a few minutes
- The executable will be approximately 50-100 MB (includes Python runtime and all dependencies)

## Technology Stack

- Python 3.10+
- PyQt6 (GUI)
- pymodbus (Modbus protocol)
- pyserial (Serial communication)
- PyInstaller (for building .exe)

---

# Modbus Tester

En Modbus master/simulator desktop-applikation til test af Modbus RTU (RS-485/RS-232) og Modbus TCP/IP forbindelser.

## Funktioner

- **Modbus RTU (master)** via RS-485/RS-232
- **Modbus TCP (client/master)**
- **Flere parallelle sessions** med multi-view support
- **Læs/skriv coils, discrete inputs, input registers og holding registers**
- **Integreret Modbus Simulator** - Start TCP/RTU simulatoren direkte fra appen
- **Device Scanner** - Find automatisk Modbus enheder på RTU bus eller TCP/IP netværk
  - **RTU Scanner** - Scan seriel bus for device IDs og aktive registre
  - **TCP Scanner** - Scan netværk IP ranges og porte for Modbus TCP enheder
  - **Eksporter til PDF** - Gem device information som PDF til dokumentation
  - **Importer Connection/Session** - Højreklik på fundne enheder for automatisk at importere dem
- **Multi-view** - Se flere sessions side om side i grupper
- **Tag Management** - Definer brugerdefinerede tags med datatyper, skalering og enheder
- **Datatyper Support** - UINT16, INT16, UINT32, INT32 (DINT), FLOAT32, BOOL
- **HEX Visning** - Se hexadecimal repræsentation af alle værdier
- **Mørkt Tema** - Moderne mørkt interface for mindre anstrengelse
- **Justerbare Paneler** - Justerbar splitter mellem Connections og Sessions
- **Auto-gem UI Indstillinger** - Vindue position og panel størrelser gemmes automatisk
- **Omfattende fejlsøgning**: hexdump, tidsstempler, log, statuskoder
- **Real-time data visning** i tabeller
- **Manuel write operationer**
- **Projekt management** - Gem og genåbn konfigurationer (inkl. multi-view opsætning)

## Installation

```bash
pip install -r requirements.txt
```

## Kørsel

### Hovedapplikation

```bash
python src/main.py
```

### Modbus Simulator (til test)

**Anbefalet:** Brug den integrerede simulator i appen via **Vis → Modbus Simulator...**

Alternativt kan du køre simulatoren fra kommandolinjen:

**TCP Simulator:**
```bash
python src/simulator/modbus_simulator.py --type tcp --host 127.0.0.1 --port 5020
```

**RTU Simulator:**
```bash
python src/simulator/modbus_simulator.py --type rtu --serial-port COM10 --baudrate 9600
```

**Eller brug det simple script:**
```bash
python start_rtu_simulator.py
```

Dette starter RTU simulatoren på COM10 med 9600 baud.

Simulatoren har følgende testdata:
- **Holding registers (0-9)**: 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
- **Input registers (0-9)**: 50, 150, 250, 350, 450, 550, 650, 750, 850, 950
- **Coils (0-9)**: True, False, True, False, True, False, True, False, True, False
- **Discrete inputs (0-9)**: False, True, False, True, False, True, False, True, False, True

**Eksempel på forbindelse:**
1. Start applikationen: `python src/main.py`
2. Start simulatoren via **Vis → Modbus Simulator...** → Start TCP Simulator (port 5020)
3. Opret en ny TCP forbindelse med:
   - Host: `127.0.0.1`
   - Port: `5020`
   - Slave ID: `1`
4. Opret en session med:
   - Function code: `03` (Read Holding Registers)
   - Start address: `0`
   - Quantity: `10`
5. Start polling for at se dataene

**Multi-view:**
- Opret grupper via **Vis → Manage Multi-view...**
- Aktiver multi-view via **Vis → Multi-view**
- Se flere sessions side om side
- Multi-view konfiguration gemmes med projekter

**Device Scanner:**
- Gå til **Connection → Device Scanner...**
- **RTU Scanner Tab:**
  - Vælg COM port og konfigurer serielle indstillinger (baudrate, parity, etc.)
  - Sæt device ID range til at scanne (standard: 1-247)
  - Klik "Start Scan" for automatisk at finde Modbus enheder på seriel bus
- **TCP Scanner Tab:**
  - Indtast IP range (f.eks. "192.168.1.1-254" eller "192.168.1.0/24" for CIDR notation)
  - Indtast porte til at scanne (f.eks. "502" eller "502,5020" for flere porte)
  - Sæt device ID range til at scanne (standard: 1-247)
  - Klik "Start Scan" for automatisk at finde Modbus TCP enheder på netværket
- **Funktioner:**
  - Resultater viser tilgængelige register typer og aktive adresser
  - **Gem som PDF:** Klik "Save as PDF" knap for at eksportere device information
  - **Importer Connection:** Højreklik på funden enhed → "Import Connection" for at oprette connection profile
  - **Importer Session:** Højreklik på funden enhed → "Import Session" for at oprette connection og session automatisk
  - Bemærk: Kun adresser med aktive værdier vises (non-zero for registre, True for coils)

**Tag Management:**
- Klik "Manage Tags..." i en session tab
- Definer brugerdefinerede tags med navne, datatyper, byte order, skalering og enheder
- Understøtter: UINT16, INT16, UINT32, INT32 (DINT), FLOAT32, BOOL
- Tags skal matche sessionens function code (address_type)

**Brugergrænseflade:**
- Mørkt tema for mindre anstrengelse
- Justerbare paneler - træk splitteren mellem Connections og Sessions
- Vindue position og panel størrelser gemmes automatisk
- HEX kolonne viser hexadecimal repræsentation af værdier

## Byg Executable (.exe)

For at bygge en standalone .exe fil:

```bash
# Installer PyInstaller (hvis ikke allerede installeret)
pip install pyinstaller

# Byg executable
python build_exe.py
```

Eller brug batch filen:
```bash
build_exe.bat
```

Executablen vil blive placeret i `dist/ModbusTester.exe`

**Noter:**
- Executablen er standalone og kræver ikke Python installation
- Første build kan tage et par minutter
- Executablen vil være ca. 50-100 MB (inkluderer Python runtime og alle dependencies)

## Teknologistack

- Python 3.10+
- PyQt6 (GUI)
- pymodbus (Modbus protokol)
- pyserial (Seriel kommunikation)
- PyInstaller (til at bygge .exe)
