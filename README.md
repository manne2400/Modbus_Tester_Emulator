# Modbus Tester

A Modbus master/simulator desktop application for testing Modbus RTU (RS-485/RS-232) and Modbus TCP/IP connections.

## Features

- **Modbus RTU (master)** via RS-485/RS-232
- **Modbus TCP (client/master)**
- **Multiple parallel sessions** with multi-view support
- **Read/write coils, discrete inputs, input registers and holding registers**
- **Integrated Modbus Simulator** - Start TCP/RTU simulators directly from the app
- **Multi-view** - View multiple sessions side-by-side in groups
- **Comprehensive debugging**: hexdump, timestamps, log, status codes
- **Real-time data display** in tables
- **Manual write operations**
- **Project management** - Save and reopen configurations

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
- Create groups via **View → Manage multi-view...**
- Activate multi-view via **View → Multi-view**
- View multiple sessions side-by-side

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
- **Multi-view** - Se flere sessions side om side i grupper
- **Omfattende fejlsøgning**: hexdump, tidsstempler, log, statuskoder
- **Real-time data visning** i tabeller
- **Manuel write operationer**
- **Projekt management** - Gem og genåbn konfigurationer

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
- Opret grupper via **Vis → Administrer multi-view...**
- Aktiver multi-view via **Vis → Multi-view**
- Se flere sessions side om side

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
