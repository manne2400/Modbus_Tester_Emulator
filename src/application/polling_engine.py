"""Polling engine for Modbus sessions"""
import time
import threading
from datetime import datetime
from typing import Dict, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from src.models.session_definition import SessionDefinition, SessionStatus
from src.models.poll_result import PollResult, PollStatus
from src.models.tag_definition import DataType
from src.application.session_manager import SessionManager
from src.application.data_processor import DataProcessor
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PollingEngine(QObject):
    """Polling engine that manages Modbus polling for all sessions"""
    
    # Signals
    poll_result = pyqtSignal(str, PollResult)  # session_id, result
    session_error = pyqtSignal(str, str)  # session_id, error_message
    
    def __init__(self, session_manager: SessionManager):
        """Initialize polling engine"""
        super().__init__()
        self.session_manager = session_manager
        self.running = False
        self.poll_thread: Optional[threading.Thread] = None
        self.next_poll_times: Dict[str, float] = {}  # session_id -> next poll time
        self.result_callback: Optional[Callable] = None
    
    def set_result_callback(self, callback: Callable):
        """Set callback for poll results"""
        self.result_callback = callback
    
    def start(self):
        """Start polling engine"""
        if self.running:
            return
        
        self.running = True
        self.poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.poll_thread.start()
        logger.info("Polling engine started")
    
    def stop(self):
        """Stop polling engine"""
        self.running = False
        if self.poll_thread:
            self.poll_thread.join(timeout=2.0)
        logger.info("Polling engine stopped")
    
    def _poll_loop(self):
        """Main polling loop"""
        while self.running:
            try:
                current_time = time.time()
                running_sessions = self.session_manager.get_running_sessions()
                
                for session in running_sessions:
                    session_id = session.name
                    
                    # Check if it's time to poll
                    next_poll_time = self.next_poll_times.get(session_id, 0)
                    
                    if current_time >= next_poll_time:
                        self._poll_session(session)
                        # Schedule next poll
                        interval_seconds = session.poll_interval_ms / 1000.0
                        self.next_poll_times[session_id] = current_time + interval_seconds
                
                # Sleep a bit to avoid busy waiting
                time.sleep(0.01)  # 10ms
                
            except Exception as e:
                logger.error(f"Error in polling loop: {e}")
                time.sleep(0.1)
    
    def _poll_session(self, session: SessionDefinition):
        """Poll a single session"""
        try:
            protocol = self.session_manager.get_protocol(session.connection_profile_name)
            if not protocol:
                error_msg = f"Protocol not found for {session.connection_profile_name}"
                self.session_error.emit(session.name, error_msg)
                return
            
            # Ensure connection is established
            transport = self.session_manager.connections.get(session.connection_profile_name)
            if not transport or not transport.is_connected:
                if not self.session_manager.connect(session.connection_profile_name):
                    error_msg = f"Failed to connect to {session.connection_profile_name}"
                    self.session_error.emit(session.name, error_msg)
                    self.session_manager.set_session_error(session.name)
                    return
            
            start_time = time.time()
            
            # Calculate required quantity to cover all tags
            # For tags with INT32/UINT32/FLOAT32, we need 2 registers per tag
            required_quantity = session.quantity
            if session.tags:
                max_tag_address = max(tag.address for tag in session.tags)
                max_tag_end = max_tag_address
                # Check if any tag needs 2 registers
                for tag in session.tags:
                    if tag.data_type in [DataType.UINT32, DataType.INT32, DataType.FLOAT32]:
                        # Tag uses 2 registers, so end address is tag.address + 1
                        max_tag_end = max(max_tag_end, tag.address + 1)
                # Calculate quantity needed to cover all tags
                required_quantity = max(required_quantity, max_tag_end - session.start_address + 1)
            
            # Execute read operation
            data, error = protocol.execute_read(
                session.function_code,
                session.slave_id,
                session.start_address,
                required_quantity,
                session_id=session.name
            )
            
            response_time = (time.time() - start_time) * 1000
            
            # Create poll result
            if error:
                status = PollStatus.ERROR
                if "timeout" in error.lower():
                    status = PollStatus.TIMEOUT
                elif "crc" in error.lower():
                    status = PollStatus.CRC_ERROR
                elif "exception" in error.lower():
                    status = PollStatus.EXCEPTION
                
                result = PollResult(
                    timestamp=datetime.now(),
                    session_id=session.name,
                    raw_data=[],
                    decoded_values=[],
                    status=status,
                    error_message=error,
                    response_time_ms=response_time
                )
            else:
                # Process data
                raw_data = []
                decoded_values = []
                
                if data is not None:
                    if isinstance(data, list):
                        if len(data) > 0:
                            if isinstance(data[0], bool):
                                raw_data = [1 if b else 0 for b in data]
                            else:
                                raw_data = list(data)
                            
                            # Decode values if tags are defined
                            # Map function code to address type
                            from src.models.tag_definition import AddressType
                            from src.protocol.function_codes import FunctionCode
                            
                            function_to_address_type = {
                                FunctionCode.READ_COILS: AddressType.COIL,
                                FunctionCode.READ_DISCRETE_INPUTS: AddressType.DISCRETE_INPUT,
                                FunctionCode.READ_HOLDING_REGISTERS: AddressType.HOLDING_REGISTER,
                                FunctionCode.READ_INPUT_REGISTERS: AddressType.INPUT_REGISTER,
                            }
                            
                            expected_address_type = function_to_address_type.get(session.function_code)
                            
                            # Filter tags that match the session's function code
                            matching_tags = []
                            if session.tags and expected_address_type:
                                matching_tags = [tag for tag in session.tags 
                                                if tag.address_type == expected_address_type]
                            
                            if matching_tags:
                                # Use matching tags to decode values
                                for tag in matching_tags:
                                    try:
                                        if tag.data_type in [DataType.UINT32, DataType.INT32, DataType.FLOAT32]:
                                            # Multi-register types
                                            tag_index = tag.address - session.start_address
                                            if tag_index >= 0 and tag_index + 1 < len(raw_data):
                                                decoded = DataProcessor.decode_value(
                                                    raw_data,
                                                    tag.data_type,
                                                    tag.byte_order,
                                                    tag_index
                                                )
                                                scaled = DataProcessor.apply_scaling(
                                                    decoded,
                                                    tag.scale_factor,
                                                    tag.scale_offset
                                                )
                                                decoded_values.append({
                                                    "address": tag.address,
                                                    "name": tag.name,
                                                    "raw": decoded,
                                                    "scaled": scaled,
                                                    "unit": tag.unit
                                                })
                                        else:
                                            # Single register types
                                            tag_index = tag.address - session.start_address
                                            if 0 <= tag_index < len(raw_data):
                                                decoded = DataProcessor.decode_value(
                                                    raw_data,
                                                    tag.data_type,
                                                    tag.byte_order,
                                                    tag_index
                                                )
                                                scaled = DataProcessor.apply_scaling(
                                                    decoded,
                                                    tag.scale_factor,
                                                    tag.scale_offset
                                                )
                                                decoded_values.append({
                                                    "address": tag.address,
                                                    "name": tag.name,
                                                    "raw": decoded,
                                                    "scaled": scaled,
                                                    "unit": tag.unit
                                                })
                                    except Exception as e:
                                        logger.error(f"Error decoding tag {tag.name}: {e}")
                            else:
                                # No matching tags, just use raw values
                                for i, val in enumerate(raw_data):
                                    decoded_values.append({
                                        "address": session.start_address + i,
                                        "name": f"Address {session.start_address + i}",
                                        "raw": val,
                                        "scaled": val,
                                        "unit": ""
                                    })
                
                result = PollResult(
                    timestamp=datetime.now(),
                    session_id=session.name,
                    raw_data=raw_data,
                    decoded_values=decoded_values,
                    status=PollStatus.OK,
                    response_time_ms=response_time
                )
            
            # Emit result
            self.poll_result.emit(session.name, result)
            if self.result_callback:
                self.result_callback(session.name, result)
            
        except Exception as e:
            logger.error(f"Error polling session {session.name}: {e}")
            error_result = PollResult(
                timestamp=datetime.now(),
                session_id=session.name,
                raw_data=[],
                decoded_values=[],
                status=PollStatus.ERROR,
                error_message=str(e)
            )
            self.poll_result.emit(session.name, error_result)
            self.session_manager.set_session_error(session.name)
    
    def reset_poll_timer(self, session_id: str):
        """Reset poll timer for a session (poll immediately on next cycle)"""
        self.next_poll_times[session_id] = 0
