# Modbus Tester - Status og Noter

## Projekt Status
✅ **Applikationen er færdig og virker!**

## Hvad vi har lavet

### 1. Modbus Tester Applikation
- ✅ Komplet Modbus master/simulator desktop-applikation
- ✅ Understøtter Modbus RTU og Modbus TCP/IP
- ✅ Flere parallelle sessions
- ✅ Læs/skriv coils, discrete inputs, input registers og holding registers
- ✅ Fejlsøgning: hexdump, tidsstempler, log, statuskoder
- ✅ Real-time data visning i tabeller

### 2. Modbus Simulatorer
- ✅ **TCP Simulator** - Virker perfekt på port 5020
- ✅ **RTU Simulator** - Klar til brug, venter på COM-port par

## Filer og Scripts

### Hovedapplikation
```bash
python src/main.py
```

### TCP Simulator
```bash
python src/simulator/modbus_simulator.py --type tcp --host 127.0.0.1 --port 5020
```

### RTU Simulator
```bash
python start_rtu_simulator.py
```
Eller:
```bash
python src/simulator/modbus_simulator.py --type rtu --serial-port COM10 --baudrate 9600
```

### Tjek COM-porte
```bash
python check_com_ports.py
```

## Nuværende Status

### ✅ TCP - Virker perfekt
- Simulator kører på: `127.0.0.1:5020`
- Testdata:
  - Holding registers (0-9): 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000
  - Input registers (0-9): 50, 150, 250, 350, 450, 550, 650, 750, 850, 950
  - Coils (0-9): True, False, True, False, True, False, True, False, True, False
  - Discrete inputs (0-9): False, True, False, True, False, True, False, True, False, True

### ⏳ RTU - Vent på genstart
- **Problem:** COM10 og COM11 findes ikke endnu
- **Årsag:** com0com driverne er installeret men ikke aktiveret (gule advarselstrekanter i Device Manager)
- **Løsning:** Genstart computeren for at aktivere driverne

## Efter Genstart - RTU Setup

### 1. Tjek om COM-porte er tilgængelige
```bash
python check_com_ports.py
```
**Forventet resultat:** COM10 og COM11 skal være synlige

### 2. Hvis COM10 og COM11 findes:
1. **Start RTU simulatoren** (i et terminalvindue):
   ```bash
   python start_rtu_simulator.py
   ```
   - Simulatoren kører på **COM10**

2. **I Modbus Tester applikationen:**
   - Opret/rediger RTU forbindelse
   - **Port:** COM11 (ikke COM10!)
   - **Baudrate:** 9600
   - **Parity:** N
   - **Stop bits:** 1
   - **Data bits:** 8
   - **Slave ID:** 1

3. **Opret session:**
   - Function code: 03 (Read Holding Registers)
   - Start address: 0
   - Quantity: 10
   - Klik "Start"

### 3. Hvis COM10/COM11 stadig ikke findes efter genstart:
- Tjek Device Manager for com0com enheder
- Hvis der stadig er gule advarselstrekanter med **Code 52** (unsigned drivers):
  - **Løsning:** Deaktiver driver signature enforcement
  - **Metode:**
    1. Windows + I → System → Recovery → Advanced startup → Restart now
    2. Troubleshoot → Advanced options → Startup Settings → Restart
    3. Vælg "Disable driver signature enforcement" (tast 7)
    4. Efter genstart: Højreklik på com0com enheder → Update driver
    5. Vælg "Browse my computer" → "Let me pick from a list"
    6. Vælg com0com driverne
  - **Alternativ:** Brug Virtual Serial Port Driver (betalingsløsning med signerede drivers)
  - **Alternativ:** Test med fysisk RTU udstyr i stedet for simulator

## Projektstruktur

```
Modbus_Tester/
├── src/
│   ├── main.py                    # Hovedapplikation
│   ├── models/                    # Datamodeller
│   ├── transport/                 # TCP og RTU transport
│   ├── protocol/                  # Modbus protokol
│   ├── application/               # Session manager og polling
│   ├── ui/                        # PyQt6 GUI
│   ├── storage/                   # JSON lagring
│   ├── utils/                     # Utilities
│   └── simulator/
│       └── modbus_simulator.py    # Modbus simulator
├── start_rtu_simulator.py         # RTU simulator script
├── check_com_ports.py             # Tjek COM-porte
├── requirements.txt               # Dependencies
└── README.md                      # Dokumentation
```

## Vigtige Oplysninger

### Teknologistack
- Python 3.10+
- PyQt6 (GUI)
- pymodbus 3.11.3 (Modbus protokol)
- pyserial 3.5 (Seriel kommunikation)

### pymodbus 3.x API Ændringer (vigtigt!)
- `slave=` → `device_id=`
- `quantity` → `count=` (for read operationer)
- `ModbusSlaveContext` → `ModbusDeviceContext`
- `slaves={}` → `devices={}` i ModbusServerContext
- `FramerRTU` → `FramerType.RTU`

### COM-port Par Setup
- **com0com installeret:** ✅
- **COM-port par oprettet:** COM10 ↔ COM11
- **Status:** Vent på genstart for at aktivere

## Test Scenarier

### TCP Test (Virker nu)
1. Start TCP simulator: `python src/simulator/modbus_simulator.py --type tcp --port 5020`
2. Åbn Modbus Tester
3. Opret TCP forbindelse: 127.0.0.1:5020
4. Opret session med Slave ID 1, Function 03, Address 0, Quantity 10
5. Start polling → Se dataene!

### RTU Test (Efter genstart)
1. Tjek COM-porte: `python check_com_ports.py`
2. Start RTU simulator på COM10: `python start_rtu_simulator.py`
3. I Modbus Tester: Opret RTU forbindelse på COM11
4. Opret session og start polling

## Næste Skridt

1. ✅ Genstart computeren
2. ⏳ Tjek COM-porte efter genstart
3. ⏳ Test RTU simulator
4. ⏳ Test RTU i Modbus Tester

## Noter

- TCP simulatoren virker perfekt og kan bruges til test nu
- RTU simulatoren er klar, venter bare på at COM-port parret bliver aktivt
- Alle function codes (01, 02, 03, 04, 05, 06, 0F, 10) er implementeret
- Applikationen gemmer automatisk connections og sessions i JSON filer

---
**Sidst opdateret:** 2025-11-16
**Status:** Vent på genstart for RTU test
