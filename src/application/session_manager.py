"""Session manager for handling session lifecycle"""
from typing import Dict, Optional, List
from src.models.connection_profile import ConnectionProfile
from src.models.session_definition import SessionDefinition, SessionStatus
from src.transport.base_transport import BaseTransport
from src.transport.tcp_transport import TcpTransport
from src.transport.rtu_transport import RtuTransport
from src.protocol.modbus_protocol import ModbusProtocol
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SessionManager:
    """Manages Modbus sessions and connections"""
    
    def __init__(self):
        """Initialize session manager"""
        self.connections: Dict[str, BaseTransport] = {}  # profile_name -> transport
        self.protocols: Dict[str, ModbusProtocol] = {}  # profile_name -> protocol
        self.sessions: Dict[str, SessionDefinition] = {}  # session_id -> session
        self.log_callback = None
        self.trace_callback = None
    
    def set_log_callback(self, callback):
        """Set callback for logging"""
        self.log_callback = callback
        # Update existing transports
        for transport in self.connections.values():
            transport.set_log_callback(callback)
    
    def set_trace_callback(self, callback):
        """Set callback for trace entries"""
        self.trace_callback = callback
        # Update existing transports
        for transport in self.connections.values():
            transport.set_trace_callback(callback)
    
    def add_connection(self, profile: ConnectionProfile) -> bool:
        """Add or update a connection profile"""
        try:
            # Create transport based on type
            if profile.connection_type.value == "TCP":
                transport = TcpTransport(profile)
            elif profile.connection_type.value == "RTU":
                transport = RtuTransport(profile)
            else:
                logger.error(f"Unknown connection type: {profile.connection_type}")
                return False
            
            # Set log callback if available
            if self.log_callback:
                transport.set_log_callback(self.log_callback)
            
            # Set trace callback if available
            if self.trace_callback:
                transport.set_trace_callback(self.trace_callback)
            
            # Store transport and protocol
            self.connections[profile.name] = transport
            self.protocols[profile.name] = ModbusProtocol(transport)
            
            logger.info(f"Added connection profile: {profile.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to add connection: {e}")
            return False
    
    def remove_connection(self, profile_name: str) -> bool:
        """Remove a connection profile"""
        try:
            if profile_name in self.connections:
                transport = self.connections[profile_name]
                transport.disconnect()
                del self.connections[profile_name]
                del self.protocols[profile_name]
                
                # Remove sessions using this connection
                sessions_to_remove = [
                    session_id for session_id, session in self.sessions.items()
                    if session.connection_profile_name == profile_name
                ]
                for session_id in sessions_to_remove:
                    self.remove_session(session_id)
                
                logger.info(f"Removed connection profile: {profile_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove connection: {e}")
            return False
    
    def connect(self, profile_name: str) -> bool:
        """Connect to a Modbus device"""
        if profile_name not in self.connections:
            logger.error(f"Connection profile not found: {profile_name}")
            return False
        
        transport = self.connections[profile_name]
        return transport.connect()
    
    def disconnect(self, profile_name: str):
        """Disconnect from a Modbus device"""
        if profile_name in self.connections:
            self.connections[profile_name].disconnect()
    
    def add_session(self, session: SessionDefinition) -> bool:
        """Add a session"""
        try:
            # Verify connection exists
            if session.connection_profile_name not in self.connections:
                logger.error(f"Connection profile not found: {session.connection_profile_name}")
                return False
            
            session_id = session.name
            self.sessions[session_id] = session
            logger.info(f"Added session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to add session: {e}")
            return False
    
    def remove_session(self, session_id: str) -> bool:
        """Remove a session"""
        try:
            if session_id in self.sessions:
                session = self.sessions[session_id]
                session.status = SessionStatus.STOPPED
                del self.sessions[session_id]
                logger.info(f"Removed session: {session_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to remove session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[SessionDefinition]:
        """Get a session by ID"""
        return self.sessions.get(session_id)
    
    def get_all_sessions(self) -> List[SessionDefinition]:
        """Get all sessions"""
        return list(self.sessions.values())
    
    def get_protocol(self, profile_name: str) -> Optional[ModbusProtocol]:
        """Get protocol for a connection profile"""
        return self.protocols.get(profile_name)
    
    def start_session(self, session_id: str) -> bool:
        """Start a session (mark as running)"""
        if session_id in self.sessions:
            self.sessions[session_id].status = SessionStatus.RUNNING
            return True
        return False
    
    def stop_session(self, session_id: str) -> bool:
        """Stop a session (mark as stopped)"""
        if session_id in self.sessions:
            self.sessions[session_id].status = SessionStatus.STOPPED
            return True
        return False
    
    def set_session_error(self, session_id: str):
        """Set session status to error"""
        if session_id in self.sessions:
            self.sessions[session_id].status = SessionStatus.ERROR
    
    def get_running_sessions(self) -> List[SessionDefinition]:
        """Get all running sessions"""
        return [
            session for session in self.sessions.values()
            if session.status == SessionStatus.RUNNING
        ]
