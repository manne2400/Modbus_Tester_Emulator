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
    # Holding registers - some test values (UINT16)
    values = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    for i, val in enumerate(values):
        device.setValues(3, i, [val])  # Function 03, address i, value
    
    # Input registers - some test values (UINT16)
    values = [50, 150, 250, 350, 450, 550, 650, 750, 850, 950]
    for i, val in enumerate(values):
        device.setValues(4, i, [val])  # Function 04, address i, value
    
    # DINT (INT32) test values in holding registers (starting at address 20)
    # DINT uses 2 registers, so we set them in pairs
    # Big Endian format: high word first, then low word
    dint_values = [
        1000000,      # Address 20-21: 1,000,000 (0x000F4240)
        -500000,      # Address 22-23: -500,000 (0xFFF8F380)
        2147483647,   # Address 24-25: Max INT32 (0x7FFFFFFF)
        -2147483648,  # Address 26-27: Min INT32 (0x80000000)
        12345,        # Address 28-29: 12,345 (0x00003039)
        -12345,       # Address 30-31: -12,345 (0xFFFFCFC7)
    ]
    
    for i, dint_val in enumerate(dint_values):
        addr = 20 + (i * 2)  # Each DINT uses 2 registers
        # Convert DINT to two 16-bit words (Big Endian)
        if dint_val < 0:
            # Convert negative to unsigned 32-bit
            uint32_val = dint_val + 4294967296
        else:
            uint32_val = dint_val
        
        high_word = (uint32_val >> 16) & 0xFFFF
        low_word = uint32_val & 0xFFFF
        device.setValues(3, addr, [high_word, low_word])
    
    # DINT (INT32) test values in input registers (starting at address 20)
    dint_input_values = [
        50000,        # Address 20-21: 50,000 (0x0000C350)
        -25000,       # Address 22-23: -25,000 (0xFFFF9C18)
        100000,       # Address 24-25: 100,000 (0x000186A0)
        -100000,      # Address 26-27: -100,000 (0xFFFE7960)
        999999,       # Address 28-29: 999,999 (0x000F423F)
        -999999,      # Address 30-31: -999,999 (0xFFF0BDC1)
    ]
    
    for i, dint_val in enumerate(dint_input_values):
        addr = 20 + (i * 2)  # Each DINT uses 2 registers
        # Convert DINT to two 16-bit words (Big Endian)
        if dint_val < 0:
            # Convert negative to unsigned 32-bit
            uint32_val = dint_val + 4294967296
        else:
            uint32_val = dint_val
        
        high_word = (uint32_val >> 16) & 0xFFFF
        low_word = uint32_val & 0xFFFF
        device.setValues(4, addr, [high_word, low_word])
    
    # Coils - some test values
    coil_values = [True, False, True, False, True, False, True, False, True, False]
    for i, val in enumerate(coil_values):
        device.setValues(1, i, [val])  # Function 01, address i, value
    
    # Discrete inputs - some test values
    di_values = [False, True, False, True, False, True, False, True, False, True]
    for i, val in enumerate(di_values):
        device.setValues(2, i, [val])  # Function 02, address i, value
    
    # Dedicated write addresses for app testing
    # Holding registers - writable addresses (40-49) - initialized to 0
    # These can be written to using function code 06 (Write Single Register) or 16 (Write Multiple Registers)
    for i in range(40, 50):
        device.setValues(3, i, [0])  # Function 03, address i, value = 0
    
    # Coils - writable addresses (20-29) - initialized to False
    # These can be written to using function code 05 (Write Single Coil) or 15 (Write Multiple Coils)
    for i in range(20, 30):
        device.setValues(1, i, [False])  # Function 01, address i, value = False
    
    logger.info("Simulator data initialized")
    logger.info("Holding registers (0-9): 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000")
    logger.info("Input registers (0-9): 50, 150, 250, 350, 450, 550, 650, 750, 850, 950")
    logger.info("Coils (0-9): True, False, True, False, True, False, True, False, True, False")
    logger.info("Discrete inputs (0-9): False, True, False, True, False, True, False, True, False, True")
    logger.info("")
    logger.info("DINT (INT32) test values in Holding Registers (Big Endian):")
    logger.info("  Address 20-21: 1,000,000 (0x000F4240)")
    logger.info("  Address 22-23: -500,000 (0xFFF8F380)")
    logger.info("  Address 24-25: 2,147,483,647 (MAX INT32, 0x7FFFFFFF)")
    logger.info("  Address 26-27: -2,147,483,648 (MIN INT32, 0x80000000)")
    logger.info("  Address 28-29: 12,345 (0x00003039)")
    logger.info("  Address 30-31: -12,345 (0xFFFFCFC7)")
    logger.info("")
    logger.info("DINT (INT32) test values in Input Registers (Big Endian):")
    logger.info("  Address 20-21: 50,000 (0x0000C350)")
    logger.info("  Address 22-23: -25,000 (0xFFFF9C18)")
    logger.info("  Address 24-25: 100,000 (0x000186A0)")
    logger.info("  Address 26-27: -100,000 (0xFFFE7960)")
    logger.info("  Address 28-29: 999,999 (0x000F423F)")
    logger.info("  Address 30-31: -999,999 (0xFFF0BDC1)")
    logger.info("")
    logger.info("Note: DINT values use 2 registers each. Use INT32 datatype with Big Endian byte order.")
    logger.info("")
    logger.info("Dedicated write addresses for app testing:")
    logger.info("  Holding registers (40-49): Initialized to 0 - can be written with function code 06 or 16")
    logger.info("  Coils (20-29): Initialized to False - can be written with function code 05 or 15")
    
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
