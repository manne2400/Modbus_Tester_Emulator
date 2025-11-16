"""Test COM ports even with unsigned drivers"""
import serial
import serial.tools.list_ports

print("Testing COM ports availability...")
print("=" * 50)

# Get all COM ports
ports = serial.tools.list_ports.comports()
print(f"\nFound {len(ports)} COM port(s):")
for port in ports:
    print(f"  {port.device} - {port.description}")

# Test COM10 and COM11 specifically
test_ports = ['COM10', 'COM11']
print("\n" + "=" * 50)
print("Testing COM10 and COM11:")
print("=" * 50)

for port_name in test_ports:
    print(f"\nTesting {port_name}...")
    try:
        # Try to open the port
        ser = serial.Serial(
            port=port_name,
            baudrate=9600,
            timeout=1,
            write_timeout=1
        )
        print(f"  [OK] {port_name} is AVAILABLE and can be opened!")
        ser.close()
    except serial.SerialException as e:
        print(f"  [FAIL] {port_name} is NOT available: {e}")
    except Exception as e:
        print(f"  [WARNING] {port_name} error: {e}")

print("\n" + "=" * 50)
print("Note: Even with unsigned drivers (Code 52),")
print("the ports might still work if you disable")
print("driver signature enforcement.")
print("=" * 50)
