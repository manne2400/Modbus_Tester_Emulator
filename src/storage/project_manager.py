"""Project manager for saving/loading complete projects"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from src.models.connection_profile import ConnectionProfile
from src.models.session_definition import SessionDefinition
from src.storage.config_manager import ConfigManager
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectManager:
    """Manages project save/load operations"""
    
    def __init__(self, config_manager: ConfigManager):
        """Initialize project manager"""
        self.config_manager = config_manager
    
    def save_project(
        self,
        file_path: Path,
        connections: List[ConnectionProfile],
        sessions: List[SessionDefinition],
        multi_view_groups: Optional[Dict[str, List[str]]] = None,
        multi_view_active: bool = False
    ) -> bool:
        """Save complete project to file"""
        try:
            data = {
                "version": "1.0",
                "connections": [conn.to_dict() for conn in connections],
                "sessions": [session.to_dict() for session in sessions],
                "multi_view": {
                    "active": multi_view_active,
                    "groups": multi_view_groups or {}
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # Save as last project
            self.config_manager.config_dir.mkdir(parents=True, exist_ok=True)
            last_project_file = self.config_manager.config_dir / "last_project.json"
            with open(last_project_file, 'w', encoding='utf-8') as f:
                json.dump({"path": str(file_path)}, f, indent=2)
            
            logger.info(f"Saved project to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save project: {e}")
            return False
    
    def load_project(
        self,
        file_path: Path
    ) -> tuple[List[ConnectionProfile], List[SessionDefinition], Dict[str, List[str]], bool]:
        """Load complete project from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            connections = [
                ConnectionProfile.from_dict(conn_data)
                for conn_data in data.get("connections", [])
            ]
            
            sessions = [
                SessionDefinition.from_dict(session_data)
                for session_data in data.get("sessions", [])
            ]
            
            # Load multi-view configuration (backward compatible)
            multi_view_data = data.get("multi_view", {})
            multi_view_groups = multi_view_data.get("groups", {})
            multi_view_active = multi_view_data.get("active", False)
            
            logger.info(f"Loaded project from {file_path}: {len(connections)} connections, {len(sessions)} sessions, multi-view: {multi_view_active}")
            return connections, sessions, multi_view_groups, multi_view_active
        except Exception as e:
            logger.error(f"Failed to load project: {e}")
            return [], [], {}, False
    
    def get_last_project_path(self) -> Optional[Path]:
        """Get path to last opened project"""
        try:
            last_project_file = self.config_manager.config_dir / "last_project.json"
            if not last_project_file.exists():
                return None
            
            with open(last_project_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            path = Path(data.get("path", ""))
            if path.exists():
                return path
            return None
        except Exception as e:
            logger.error(f"Failed to get last project path: {e}")
            return None
    
    def export_project(
        self,
        file_path: Path,
        connections: List[ConnectionProfile],
        sessions: List[SessionDefinition],
        multi_view_groups: Optional[Dict[str, List[str]]] = None,
        multi_view_active: bool = False
    ) -> bool:
        """Export project (same as save, but for sharing)"""
        return self.save_project(file_path, connections, sessions, multi_view_groups, multi_view_active)
