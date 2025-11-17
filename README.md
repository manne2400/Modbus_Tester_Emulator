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
