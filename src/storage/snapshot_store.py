"""Snapshot store for managing snapshots"""
import json
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from src.models.snapshot import Snapshot
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SnapshotStore:
    """Store for managing snapshots"""
    
    def __init__(self, snapshots_dir: Optional[Path] = None):
        """Initialize snapshot store
        
        Args:
            snapshots_dir: Directory to store snapshots (default: snapshots/ in project root)
        """
        if snapshots_dir is None:
            snapshots_dir = Path("snapshots")
        self.snapshots_dir = snapshots_dir
        self.snapshots_dir.mkdir(parents=True, exist_ok=True)
    
    def save_snapshot(self, snapshot: Snapshot) -> bool:
        """Save snapshot to file"""
        try:
            # Create safe filename from snapshot name
            safe_name = "".join(c for c in snapshot.name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            if not safe_name:
                safe_name = "snapshot"
            
            # Add timestamp to filename
            timestamp_str = snapshot.timestamp.strftime("%Y%m%d_%H%M%S")
            file_path = self.snapshots_dir / f"{safe_name}_{timestamp_str}.json"
            
            # Handle duplicate names
            counter = 1
            while file_path.exists():
                file_path = self.snapshots_dir / f"{safe_name}_{timestamp_str}_{counter}.json"
                counter += 1
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved snapshot '{snapshot.name}' to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            return False
    
    def load_snapshot(self, file_path: Path) -> Optional[Snapshot]:
        """Load snapshot from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            snapshot = Snapshot.from_dict(data)
            logger.info(f"Loaded snapshot '{snapshot.name}' from {file_path}")
            return snapshot
        except Exception as e:
            logger.error(f"Failed to load snapshot from {file_path}: {e}")
            return None
    
    def load_all_snapshots(self) -> List[Snapshot]:
        """Load all snapshots from snapshots directory"""
        snapshots = []
        
        if not self.snapshots_dir.exists():
            return snapshots
        
        for file_path in sorted(self.snapshots_dir.glob("*.json"), reverse=True):
            snapshot = self.load_snapshot(file_path)
            if snapshot:
                snapshots.append(snapshot)
        
        return snapshots
    
    def delete_snapshot(self, snapshot_id: str) -> bool:
        """Delete snapshot by ID"""
        try:
            snapshots = self.load_all_snapshots()
            snapshot = next((s for s in snapshots if s.id == snapshot_id), None)
            
            if not snapshot:
                logger.warning(f"Snapshot '{snapshot_id}' not found")
                return False
            
            # Find and delete file
            for file_path in self.snapshots_dir.glob("*.json"):
                loaded_snapshot = self.load_snapshot(file_path)
                if loaded_snapshot and loaded_snapshot.id == snapshot_id:
                    file_path.unlink()
                    logger.info(f"Deleted snapshot '{snapshot_id}' from {file_path}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to delete snapshot: {e}")
            return False
    
    def get_snapshot(self, snapshot_id: str) -> Optional[Snapshot]:
        """Get snapshot by ID"""
        snapshots = self.load_all_snapshots()
        return next((s for s in snapshots if s.id == snapshot_id), None)

