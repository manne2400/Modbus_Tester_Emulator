"""Manager for running Modbus simulators"""
import threading
import time
from typing import Optional
from pymodbus.server import StartTcpServer, StartSerialServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusDeviceContext, ModbusServerContext
from pymodbus.framer import FramerType
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SimulatorManager:
    """Manager for running Modbus simulators in background threads"""
    
    def __init__(self):
        """Initialize simulator manager"""
        self.tcp_thread: Optional[threading.Thread] = None
        self.rtu_thread: Optional[threading.Thread] = None
        self.tcp_server = None
        self.rtu_server = None
        self.tcp_running = False
        self.rtu_running = False
        self._tcp_stop_event = threading.Event()
        self._rtu_stop_event = threading.Event()
    
    def create_simulator_context(self):
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
        
        logger.info("Simulator data initialized")
        return context
    
    def _run_tcp_simulator(self, host: str, port: int):
        """Run TCP simulator in thread"""
        try:
            logger.info(f"Starting Modbus TCP simulator on {host}:{port}")
            context = self.create_simulator_context()
            # StartTcpServer is blocking, so we run it in the thread
            # The thread will be a daemon thread, so it will stop when app closes
            StartTcpServer(
                context=context,
                address=(host, port)
            )
        except Exception as e:
            logger.error(f"Error running TCP simulator: {e}")
            self.tcp_running = False
        finally:
            self.tcp_running = False
            logger.info("TCP simulator thread ended")
    
    def _run_rtu_simulator(self, port: str, baudrate: int, parity: str, stopbits: int, bytesize: int):
        """Run RTU simulator in thread"""
        try:
            logger.info(f"Starting Modbus RTU simulator on {port} at {baudrate} baud")
            context = self.create_simulator_context()
            # StartSerialServer is blocking, so we run it in the thread
            # The thread will be a daemon thread, so it will stop when app closes
            StartSerialServer(
                context=context,
                port=port,
                framer=FramerType.RTU,
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize
            )
        except Exception as e:
            logger.error(f"Error running RTU simulator: {e}")
            self.rtu_running = False
        finally:
            self.rtu_running = False
            logger.info("RTU simulator thread ended")
    
    def start_tcp_simulator(self, host: str = "127.0.0.1", port: int = 5020) -> bool:
        """Start TCP simulator"""
        if self.tcp_running:
            logger.warning("TCP simulator is already running")
            return False
        
        self._tcp_stop_event.clear()
        self.tcp_running = True
        self.tcp_thread = threading.Thread(
            target=self._run_tcp_simulator,
            args=(host, port),
            daemon=True,
            name="TCP-Simulator"
        )
        self.tcp_thread.start()
        logger.info(f"TCP simulator thread started on {host}:{port}")
        return True
    
    def start_rtu_simulator(
        self, 
        port: str = "COM10", 
        baudrate: int = 9600,
        parity: str = 'N',
        stopbits: int = 1,
        bytesize: int = 8
    ) -> bool:
        """Start RTU simulator"""
        if self.rtu_running:
            logger.warning("RTU simulator is already running")
            return False
        
        self._rtu_stop_event.clear()
        self.rtu_running = True
        self.rtu_thread = threading.Thread(
            target=self._run_rtu_simulator,
            args=(port, baudrate, parity, stopbits, bytesize),
            daemon=True,
            name="RTU-Simulator"
        )
        self.rtu_thread.start()
        logger.info(f"RTU simulator thread started on {port} at {baudrate} baud")
        return True
    
    def stop_tcp_simulator(self):
        """Stop TCP simulator"""
        if not self.tcp_running:
            return
        
        self.tcp_running = False
        self._tcp_stop_event.set()
        # Note: StartTcpServer is blocking and doesn't have a direct stop method
        # The thread is a daemon thread, so it will stop when app closes
        # For now, we just mark it as stopped - the thread will continue until app closes
        logger.info("TCP simulator stop requested (will stop when app closes)")
    
    def stop_rtu_simulator(self):
        """Stop RTU simulator"""
        if not self.rtu_running:
            return
        
        self.rtu_running = False
        self._rtu_stop_event.set()
        # Note: StartSerialServer is blocking and doesn't have a direct stop method
        # The thread is a daemon thread, so it will stop when app closes
        # For now, we just mark it as stopped - the thread will continue until app closes
        logger.info("RTU simulator stop requested (will stop when app closes)")
    
    def is_tcp_running(self) -> bool:
        """Check if TCP simulator is running"""
        return self.tcp_running
    
    def is_rtu_running(self) -> bool:
        """Check if RTU simulator is running"""
        return self.rtu_running

