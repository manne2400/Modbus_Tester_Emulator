"""Build script for creating Modbus Tester executable"""
import subprocess
import sys
import os
from pathlib import Path

def build_exe():
    """Build Modbus Tester as executable"""
    print("Building Modbus Tester executable...")
    print("=" * 50)
    
    # PyInstaller command
    cmd = [
        "pyinstaller",
        "--name=ModbusTester",
        "--onefile",
        "--windowed",  # No console window
        "--icon=NONE",  # Add icon file path here if you have one
        "--add-data=README.md;.",
        "--hidden-import=pymodbus",
        "--hidden-import=pymodbus.client",
        "--hidden-import=pymodbus.server",
        "--hidden-import=pymodbus.datastore",
        "--hidden-import=pymodbus.framer",
        "--hidden-import=serial",
        "--hidden-import=serial.tools",
        "--hidden-import=serial.tools.list_ports",
        "--hidden-import=PyQt6",
        "--hidden-import=PyQt6.QtCore",
        "--hidden-import=PyQt6.QtGui",
        "--hidden-import=PyQt6.QtWidgets",
        "--collect-all=pymodbus",
        "--collect-all=PyQt6",
        "src/main.py"
    ]
    
    try:
        result = subprocess.run(cmd, check=True)
        print("\n" + "=" * 50)
        print("Build successful!")
        print("=" * 50)
        print(f"Executable location: dist/ModbusTester.exe")
        print("\nYou can now distribute the ModbusTester.exe file.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")
        return False
    except FileNotFoundError:
        print("\nPyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("Please run this script again.")
        return False

if __name__ == "__main__":
    build_exe()
