"""Template library for managing device templates"""
import json
from pathlib import Path
from typing import List, Optional, Dict
from src.models.device_template import DeviceTemplate
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TemplateLibrary:
    """Library for managing device templates"""
    
    def __init__(self, templates_dir: Optional[Path] = None):
        """Initialize template library
        
        Args:
            templates_dir: Directory to store templates (default: templates/ in project root)
        """
        if templates_dir is None:
            templates_dir = Path("templates")
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def save_template(self, template: DeviceTemplate) -> bool:
        """Save template to file"""
        try:
            # Create safe filename from template name
            safe_name = "".join(c for c in template.name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            if not safe_name:
                safe_name = "template"
            
            file_path = self.templates_dir / f"{safe_name}.json"
            
            # Handle duplicate names
            counter = 1
            while file_path.exists():
                file_path = self.templates_dir / f"{safe_name}_{counter}.json"
                counter += 1
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved template '{template.name}' to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save template: {e}")
            return False
    
    def load_template(self, file_path: Path) -> Optional[DeviceTemplate]:
        """Load template from file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            template = DeviceTemplate.from_dict(data)
            logger.info(f"Loaded template '{template.name}' from {file_path}")
            return template
        except Exception as e:
            logger.error(f"Failed to load template from {file_path}: {e}")
            return None
    
    def load_all_templates(self) -> List[DeviceTemplate]:
        """Load all templates from templates directory"""
        templates = []
        
        if not self.templates_dir.exists():
            return templates
        
        for file_path in self.templates_dir.glob("*.json"):
            template = self.load_template(file_path)
            if template:
                templates.append(template)
        
        return templates
    
    def delete_template(self, template_name: str) -> bool:
        """Delete template by name"""
        try:
            templates = self.load_all_templates()
            template = next((t for t in templates if t.name == template_name), None)
            
            if not template:
                logger.warning(f"Template '{template_name}' not found")
                return False
            
            # Find and delete file
            for file_path in self.templates_dir.glob("*.json"):
                loaded_template = self.load_template(file_path)
                if loaded_template and loaded_template.name == template_name:
                    file_path.unlink()
                    logger.info(f"Deleted template '{template_name}' from {file_path}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Failed to delete template: {e}")
            return False
    
    def get_template(self, template_name: str) -> Optional[DeviceTemplate]:
        """Get template by name"""
        templates = self.load_all_templates()
        return next((t for t in templates if t.name == template_name), None)
    
    def search_templates(self, query: str) -> List[DeviceTemplate]:
        """Search templates by name, manufacturer, model, or category"""
        query_lower = query.lower()
        templates = self.load_all_templates()
        
        results = []
        for template in templates:
            if (query_lower in template.name.lower() or
                (template.manufacturer and query_lower in template.manufacturer.lower()) or
                (template.model and query_lower in template.model.lower()) or
                (template.category and query_lower in template.category.lower())):
                results.append(template)
        
        return results

