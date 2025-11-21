"""Snapshot manager for capturing device state"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.models.snapshot import Snapshot, SnapshotSession, SnapshotValue, SnapshotValueStatus
from src.models.session_definition import SessionDefinition
from src.models.poll_result import PollResult, PollStatus
from src.application.session_manager import SessionManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SnapshotManager:
    """Manager for taking snapshots of device state"""
    
    def __init__(self, session_manager: SessionManager):
        """Initialize snapshot manager"""
        self.session_manager = session_manager
        self.last_poll_results: Dict[str, PollResult] = {}  # session_id -> last PollResult
    
    def register_poll_result(self, session_id: str, result: PollResult):
        """Register a poll result for snapshot capture"""
        self.last_poll_results[session_id] = result
    
    def take_snapshot_from_result(
        self,
        session: SessionDefinition,
        result: PollResult,
        snapshot_name: Optional[str] = None,
        note: Optional[str] = None
    ) -> Snapshot:
        """Take snapshot from a single session's poll result"""
        snapshot_id = str(uuid.uuid4())
        snapshot_name = snapshot_name or f"Snapshot_{session.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Convert PollResult to SnapshotSession
        values = []
        for value_data in result.decoded_values:
            if isinstance(value_data, dict):
                # Determine status
                if result.status == PollStatus.OK:
                    status = SnapshotValueStatus.OK
                elif result.status == PollStatus.TIMEOUT:
                    status = SnapshotValueStatus.TIMEOUT
                elif result.status == PollStatus.ERROR:
                    status = SnapshotValueStatus.ERROR
                else:
                    status = SnapshotValueStatus.ERROR
                
                snapshot_value = SnapshotValue(
                    address=value_data.get("address", 0),
                    tag_name=value_data.get("name"),
                    raw_value=value_data.get("raw"),
                    scaled_value=value_data.get("scaled"),
                    status=status,
                    unit=value_data.get("unit")
                )
                values.append(snapshot_value)
        
        snapshot_session = SnapshotSession(
            session_id=session.name,
            session_name=session.name,
            connection_name=session.connection_profile_name,
            slave_id=session.slave_id,
            function_code=session.function_code,
            values=values
        )
        
        snapshot = Snapshot(
            id=snapshot_id,
            name=snapshot_name,
            timestamp=datetime.now(),
            note=note,
            sessions=[snapshot_session]
        )
        
        logger.info(f"Created snapshot '{snapshot_name}' for session '{session.name}' with {len(values)} values")
        return snapshot
    
    def take_snapshot_from_session(
        self,
        session: SessionDefinition,
        snapshot_name: Optional[str] = None,
        note: Optional[str] = None
    ) -> Optional[Snapshot]:
        """Take snapshot from a single session using last poll result"""
        if session.name not in self.last_poll_results:
            logger.warning(f"No poll result available for session '{session.name}'")
            return None
        
        result = self.last_poll_results[session.name]
        return self.take_snapshot_from_result(session, result, snapshot_name, note)
    
    def take_snapshot_from_all_sessions(
        self,
        sessions: List[SessionDefinition],
        snapshot_name: Optional[str] = None,
        note: Optional[str] = None
    ) -> Snapshot:
        """Take snapshot from all sessions"""
        snapshot_id = str(uuid.uuid4())
        snapshot_name = snapshot_name or f"Snapshot_All_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        snapshot_sessions = []
        sessions_with_data = 0
        sessions_without_data = 0
        
        for session in sessions:
            if session.name in self.last_poll_results:
                result = self.last_poll_results[session.name]
                sessions_with_data += 1
                
                # Convert PollResult to SnapshotSession
                values = []
                for value_data in result.decoded_values:
                    if isinstance(value_data, dict):
                        # Determine status
                        if result.status == PollStatus.OK:
                            status = SnapshotValueStatus.OK
                        elif result.status == PollStatus.TIMEOUT:
                            status = SnapshotValueStatus.TIMEOUT
                        elif result.status == PollStatus.ERROR:
                            status = SnapshotValueStatus.ERROR
                        else:
                            status = SnapshotValueStatus.ERROR
                        
                        snapshot_value = SnapshotValue(
                            address=value_data.get("address", 0),
                            tag_name=value_data.get("name"),
                            raw_value=value_data.get("raw"),
                            scaled_value=value_data.get("scaled"),
                            status=status,
                            unit=value_data.get("unit")
                        )
                        values.append(snapshot_value)
                
                snapshot_session = SnapshotSession(
                    session_id=session.name,
                    session_name=session.name,
                    connection_name=session.connection_profile_name,
                    slave_id=session.slave_id,
                    function_code=session.function_code,
                    values=values
                )
                snapshot_sessions.append(snapshot_session)
            else:
                sessions_without_data += 1
                logger.warning(f"No poll result available for session '{session.name}', skipping")
        
        logger.info(f"Snapshot from all sessions: {sessions_with_data} sessions with data, {sessions_without_data} sessions without data")
        
        snapshot = Snapshot(
            id=snapshot_id,
            name=snapshot_name,
            timestamp=datetime.now(),
            note=note,
            sessions=snapshot_sessions
        )
        
        total_values = sum(len(s.values) for s in snapshot_sessions)
        logger.info(f"Created snapshot '{snapshot_name}' for {len(snapshot_sessions)} sessions with {total_values} total values")
        return snapshot

