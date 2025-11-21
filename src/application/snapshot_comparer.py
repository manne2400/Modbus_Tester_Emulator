"""Snapshot comparer for comparing two snapshots"""
from typing import List, Dict, Optional
from src.models.snapshot import Snapshot, SnapshotSession, SnapshotValue
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SnapshotDifference:
    """Represents a difference between two snapshots"""
    
    def __init__(
        self,
        session_id: str,
        session_name: str,
        address: int,
        tag_name: Optional[str],
        value_a: Optional[SnapshotValue],
        value_b: Optional[SnapshotValue]
    ):
        """Initialize snapshot difference"""
        self.session_id = session_id
        self.session_name = session_name
        self.address = address
        self.tag_name = tag_name
        self.value_a = value_a
        self.value_b = value_b
    
    def get_raw_difference(self) -> Optional[float]:
        """Get raw value difference (B - A)"""
        if self.value_a and self.value_b:
            if self.value_a.raw_value is not None and self.value_b.raw_value is not None:
                try:
                    return float(self.value_b.raw_value) - float(self.value_a.raw_value)
                except (ValueError, TypeError):
                    return None
        return None
    
    def get_scaled_difference(self) -> Optional[float]:
        """Get scaled value difference (B - A)"""
        if self.value_a and self.value_b:
            if self.value_a.scaled_value is not None and self.value_b.scaled_value is not None:
                return self.value_b.scaled_value - self.value_a.scaled_value
        return None
    
    def get_percentage_change(self) -> Optional[float]:
        """Get percentage change from A to B"""
        if self.value_a and self.value_b:
            if self.value_a.scaled_value is not None and self.value_b.scaled_value is not None:
                if self.value_a.scaled_value != 0:
                    return ((self.value_b.scaled_value - self.value_a.scaled_value) / abs(self.value_a.scaled_value)) * 100
                elif self.value_b.scaled_value != 0:
                    return 100.0  # Changed from 0 to non-zero
        return None
    
    def is_value_added(self) -> bool:
        """Check if value was added (exists in B but not A)"""
        return self.value_a is None and self.value_b is not None
    
    def is_value_removed(self) -> bool:
        """Check if value was removed (exists in A but not B)"""
        return self.value_a is not None and self.value_b is None
    
    def is_value_changed(self) -> bool:
        """Check if value changed"""
        if not self.value_a or not self.value_b:
            return False
        
        # Compare scaled values if available
        if self.value_a.scaled_value is not None and self.value_b.scaled_value is not None:
            return self.value_a.scaled_value != self.value_b.scaled_value
        
        # Fall back to raw values
        if self.value_a.raw_value is not None and self.value_b.raw_value is not None:
            return self.value_a.raw_value != self.value_b.raw_value
        
        return False


class SnapshotComparer:
    """Comparer for comparing two snapshots"""
    
    def __init__(self, snapshot_a: Snapshot, snapshot_b: Snapshot):
        """Initialize comparer with two snapshots"""
        self.snapshot_a = snapshot_a
        self.snapshot_b = snapshot_b
    
    def compare(self, changed_only: bool = False) -> List[SnapshotDifference]:
        """Compare two snapshots and return list of differences
        
        Args:
            changed_only: If True, only return differences where values changed
        
        Returns:
            List of SnapshotDifference objects
        """
        differences = []
        
        # Create maps for quick lookup: session_id -> address -> value
        map_a = self._create_value_map(self.snapshot_a)
        map_b = self._create_value_map(self.snapshot_b)
        
        # Get all unique session+address combinations
        all_keys = set()
        for session_id, address_map in map_a.items():
            for address in address_map.keys():
                all_keys.add((session_id, address))
        for session_id, address_map in map_b.items():
            for address in address_map.keys():
                all_keys.add((session_id, address))
        
        # Compare each key
        for session_id, address in all_keys:
            value_a = map_a.get(session_id, {}).get(address)
            value_b = map_b.get(session_id, {}).get(address)
            
            # Get session name
            session_name = self._get_session_name(session_id, value_a, value_b)
            tag_name = value_a.tag_name if value_a else (value_b.tag_name if value_b else None)
            
            diff = SnapshotDifference(
                session_id=session_id,
                session_name=session_name,
                address=address,
                tag_name=tag_name,
                value_a=value_a,
                value_b=value_b
            )
            
            # Filter if changed_only
            if changed_only:
                if diff.is_value_changed() or diff.is_value_added() or diff.is_value_removed():
                    differences.append(diff)
            else:
                differences.append(diff)
        
        return differences
    
    def _create_value_map(self, snapshot: Snapshot) -> Dict[str, Dict[int, SnapshotValue]]:
        """Create a map of session_id -> address -> value"""
        value_map = {}
        
        for session in snapshot.sessions:
            session_map = {}
            for value in session.values:
                session_map[value.address] = value
            value_map[session.session_id] = session_map
        
        return value_map
    
    def _get_session_name(self, session_id: str, value_a: Optional[SnapshotValue], value_b: Optional[SnapshotValue]) -> str:
        """Get session name from either snapshot"""
        # Try to find in snapshot A
        for session in self.snapshot_a.sessions:
            if session.session_id == session_id:
                return session.session_name
        
        # Try to find in snapshot B
        for session in self.snapshot_b.sessions:
            if session.session_id == session_id:
                return session.session_name
        
        return session_id
    
    def get_summary(self) -> Dict:
        """Get summary statistics of comparison"""
        differences = self.compare()
        
        total = len(differences)
        changed = sum(1 for d in differences if d.is_value_changed())
        added = sum(1 for d in differences if d.is_value_added())
        removed = sum(1 for d in differences if d.is_value_removed())
        unchanged = total - changed - added - removed
        
        return {
            "total": total,
            "changed": changed,
            "added": added,
            "removed": removed,
            "unchanged": unchanged
        }

