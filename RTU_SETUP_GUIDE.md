# RTU Setup Guide - Løsning af Code 52 Fejl

## Problem
COM10 og COM11 findes ikke pga. **Code 52** - Windows kan ikke verificere den digitale signatur for com0com driverne.

## Løsning: Deaktiver Driver Signature Enforcement

### Metode 1: Via Windows Indstillinger (Anbefalet)

1. **Åbn Windows Indstillinger:**
   - Tryk `Windows + I`
   - Gå til **System** → **Recovery**

2. **Start i Advanced Startup:**
   - Under "Advanced startup" → Klik **"Restart now"**
   - Vælg **"Troubleshoot"**
   - Vælg **"Advanced options"**
   - Vælg **"Startup Settings"**
   - Klik **"Restart"**

3. **Vælg Startup Option:**
   - Når computeren genstarter, tryk **7** eller **F7**
   - Dette vælger **"Disable driver signature enforcement"**

4. **Efter genstart:**
   - Åbn **Device Manager**
   - Find com0com enhederne under "com0com - serial port emulators"
   - Højreklik på hver enhed → **"Update driver"**
   - Vælg **"Browse my computer for drivers"**
   - Vælg **"Let me pick from a list of available drivers on my computer"**
   - Vælg com0com driverne fra listen
   - Gentag for alle com0com enheder

5. **Tjek om det virker:**
   ```bash
   python test_com_ports.py
   ```
   - COM10 og COM11 skulle nu være tilgængelige

### Metode 2: Via Command Prompt (Avanceret)

1. **Åbn Command Prompt som Administrator:**
   - Søg efter "cmd" → Højreklik → "Run as administrator"

2. **Deaktiver driver signature enforcement:**
   ```cmd
   bcdedit /set testsigning on
   ```

3. **Genstart computeren**

4. **Efter genstart:**
   - Følg samme trin som i Metode 1, trin 4

5. **Når du er færdig, aktiver det igen:**
   ```cmd
   bcdedit /set testsigning off
   ```

## Alternativer

### Alternativ 1: Virtual Serial Port Driver (Betalingsløsning)
- Download fra: https://www.virtual-serial-port.org/
- Har signerede drivers, så ingen Code 52 fejl
- Koster ca. $99

### Alternativ 2: Test med Fysisk Udstyr
- Hvis du har fysisk RTU udstyr (PLC, frekvensomformer, etc.)
- Forbind det til COM1 eller en anden fysisk port
- Brug Modbus Tester direkte mod udstyr
- Ingen simulator nødvendig

### Alternativ 3: Brug TCP i stedet
- TCP simulatoren virker perfekt
- Du kan teste alle Modbus funktioner med TCP
- RTU er kun nødvendig hvis du specifikt skal teste seriel kommunikation

## Efter Setup

Når COM10 og COM11 er tilgængelige:

1. **Start RTU simulatoren:**
   ```bash
   python start_rtu_simulator.py
   ```
   - Simulatoren kører på **COM10**

2. **I Modbus Tester:**
   - Opret RTU forbindelse på **COM11**
   - Baudrate: 9600, Parity: N, Stop bits: 1, Data bits: 8
   - Slave ID: 1
   - Opret session og start polling

## Noter

- **Vigtigt:** Når du deaktiverer driver signature enforcement, er computeren mindre sikker
- Dette er kun til test/udvikling
- Aktiver det igen når du er færdig med test
- Code 52 er normalt for com0com - det er ikke en fejl i din installation
