"""Configuration manager for JSON serialization"""
import json
from pathlib import Path
from typing import List, Dict, Any
from src.models.connection_profile import ConnectionProfile
from src.models.session_definition import SessionDefinition
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """Manages configuration file operations"""
    
    def __init__(self, config_dir: Path = None):
        """Initialize config manager"""
        if config_dir is None:
            config_dir = Path.home() / ".modbus_tester"
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.connections_file = self.config_dir / "connections.json"
        self.sessions_file = self.config_dir / "sessions.json"
        self.project_file = self.config_dir / "last_project.json"
        self.ui_settings_file = self.config_dir / "ui_settings.json"
    
    def save_connections(self, connections: List[ConnectionProfile]) -> bool:
        """Save connection profiles to file"""
        try:
            data = {
                "connections": [conn.to_dict() for conn in connections]
            }
            with open(self.connections_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(connections)} connection profiles")
            return True
        except Exception as e:
            logger.error(f"Failed to save connections: {e}")
            return False
    
    def load_connections(self) -> List[ConnectionProfile]:
        """Load connection profiles from file"""
        try:
            if not self.connections_file.exists():
                return []
            
            with open(self.connections_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            connections = [
                ConnectionProfile.from_dict(conn_data)
                for conn_data in data.get("connections", [])
            ]
            logger.info(f"Loaded {len(connections)} connection profiles")
            return connections
        except Exception as e:
            logger.error(f"Failed to load connections: {e}")
            return []
    
    def save_sessions(self, sessions: List[SessionDefinition]) -> bool:
        """Save session definitions to file"""
        try:
            data = {
                "sessions": [session.to_dict() for session in sessions]
            }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(sessions)} session definitions")
            return True
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
            return False
    
    def load_sessions(self) -> List[SessionDefinition]:
        """Load session definitions from file"""
        try:
            if not self.sessions_file.exists():
                return []
            
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            sessions = [
                SessionDefinition.from_dict(session_data)
                for session_data in data.get("sessions", [])
            ]
            logger.info(f"Loaded {len(sessions)} session definitions")
            return sessions
        except Exception as e:
            logger.error(f"Failed to load sessions: {e}")
            return []
    
    def save_ui_settings(self, window_geometry: Dict[str, int], splitter_sizes: List[int]) -> bool:
        """Save UI settings (window geometry and splitter sizes)"""
        try:
            data = {
                "window_geometry": window_geometry,
                "splitter_sizes": splitter_sizes
            }
            with open(self.ui_settings_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info("Saved UI settings")
            return True
        except Exception as e:
            logger.error(f"Failed to save UI settings: {e}")
            return False
    
    def load_ui_settings(self) -> tuple[Dict[str, int], List[int]]:
        """Load UI settings (window geometry and splitter sizes)"""
        try:
            if not self.ui_settings_file.exists():
                return {}, []
            
            with open(self.ui_settings_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            window_geometry = data.get("window_geometry", {})
            splitter_sizes = data.get("splitter_sizes", [])
            logger.info("Loaded UI settings")
            return window_geometry, splitter_sizes
        except Exception as e:
            logger.error(f"Failed to load UI settings: {e}")
            return {}, []
