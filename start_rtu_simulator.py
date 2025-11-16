"""Quick start script for RTU simulator on COM10"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.simulator.modbus_simulator import run_rtu_simulator
from src.utils.logger import setup_logging

if __name__ == "__main__":
    setup_logging()
    print("Starting Modbus RTU Simulator on COM10 at 9600 baud...")
    print("Press Ctrl+C to stop")
    run_rtu_simulator(port="COM10", baudrate=9600)
