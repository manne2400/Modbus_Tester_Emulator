"""Modbus simulator for testing"""
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pymodbus.server import StartTcpServer, StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
from pymodbus.framer import FramerType
from src.utils.logger import setup_logging, get_logger

logger = get_logger(__name__)


def create_simulator_context():
    """Create simulator data store"""
    # Create data blocks
    # Holding registers (function 03) - start at 0, 100 registers
    hr = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Input registers (function 04) - start at 0, 100 registers
    ir = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Coils (function 01) - start at 0, 100 coils
    co = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Discrete inputs (function 02) - start at 0, 100 inputs
    di = ModbusSequentialDataBlock(0, [0] * 100)
    
    # Create device context
    device = ModbusDeviceContext(
        di=di,  # Discrete inputs
        co=co,  # Coils
        hr=hr,  # Holding registers
        ir=ir   # Input registers
    )
    
    # Create server context with unit ID 1
    context = ModbusServerContext(devices={1: device}, single=False)
    
    # Initialize some test values
    # Holding registers - some test values
    values = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    for i, val in enumerate(values):
        device.setValues(3, i, [val])  # Function 03, address i, value
    
    # Input registers - some test values
    values = [50, 150, 250, 350, 450, 550, 650, 750, 850, 950]
    for i, val in enumerate(values):
        device.setValues(4, i, [val])  # Function 04, address i, value
    
    # Coils - some test values
    coil_values = [True, False, True, False, True, False, True, False, True, False]
    for i, val in enumerate(coil_values):
        device.setValues(1, i, [val])  # Function 01, address i, value
    
    # Discrete inputs - some test values
    di_values = [False, True, False, True, False, True, False, True, False, True]
    for i, val in enumerate(di_values):
        device.setValues(2, i, [val])  # Function 02, address i, value
    
    logger.info("Simulator data initialized")
    logger.info("Holding registers (0-9): 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000")
    logger.info("Input registers (0-9): 50, 150, 250, 350, 450, 550, 650, 750, 850, 950")
    logger.info("Coils (0-9): True, False, True, False, True, False, True, False, True, False")
    logger.info("Discrete inputs (0-9): False, True, False, True, False, True, False, True, False, True")
    
    return context


def run_tcp_simulator(host="127.0.0.1", port=5020):
    """Run Modbus TCP simulator"""
    logger.info(f"Starting Modbus TCP simulator on {host}:{port}")
    
    # Create context
    context = create_simulator_context()
    
    try:
        # Start TCP server
        StartTcpServer(
            context=context,
            address=(host, port)
        )
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
    except Exception as e:
        logger.error(f"Error running simulator: {e}")


def run_rtu_simulator(port="COM3", baudrate=9600):
    """Run Modbus RTU simulator"""
    logger.info(f"Starting Modbus RTU simulator on {port} at {baudrate} baud")
    
    # Create context
    context = create_simulator_context()
    
    try:
        # Start RTU server
        StartSerialServer(
            context=context,
            port=port,
            framer=FramerType.RTU,
            baudrate=baudrate,
            parity='N',
            stopbits=1,
            bytesize=8
        )
    except KeyboardInterrupt:
        logger.info("Simulator stopped by user")
    except Exception as e:
        logger.error(f"Error running simulator: {e}")


def main():
    """Main entry point"""
    import argparse
    
    setup_logging()
    
    parser = argparse.ArgumentParser(description='Modbus Simulator')
    parser.add_argument('--type', choices=['tcp', 'rtu'], default='tcp',
                        help='Simulator type (default: tcp)')
    parser.add_argument('--host', default='127.0.0.1',
                        help='TCP host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=5020,
                        help='TCP port (default: 5020)')
    parser.add_argument('--serial-port', default='COM3',
                        help='Serial port for RTU (default: COM3)')
    parser.add_argument('--baudrate', type=int, default=9600,
                        help='Baudrate for RTU (default: 9600)')
    
    args = parser.parse_args()
    
    if args.type == 'tcp':
        run_tcp_simulator(args.host, args.port)
    else:
        run_rtu_simulator(args.serial_port, args.baudrate)


if __name__ == "__main__":
    main()
