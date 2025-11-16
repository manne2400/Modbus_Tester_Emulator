"""Check available COM ports"""
import serial.tools.list_ports

print("Available COM ports:")
ports = serial.tools.list_ports.comports()
if ports:
    for port in ports:
        print(f"  {port.device} - {port.description}")
        if hasattr(port, 'hwid'):
            print(f"    HWID: {port.hwid}")
else:
    print("  No COM ports found")

print("\nChecking for COM10 and COM11:")
print(f"  COM10: {'Found' if any(p.device == 'COM10' for p in ports) else 'NOT FOUND'}")
print(f"  COM11: {'Found' if any(p.device == 'COM11' for p in ports) else 'NOT FOUND'}")
