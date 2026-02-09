"""
Theme Manager for Hayward Tech Suite.

Handles loading and applying QSS stylesheets with hot-reload capability.
"""

from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QApplication
from src.utils.logger import get_logger
from src.utils.resource_path import resource_path

logger = get_logger("theme_manager")


class ThemeManager:
    """Manages application themes and stylesheets."""
    
    THEMES = {
        "hacker_dark": "hacker_dark.qss",
        "hacker_light": "hacker_light.qss",
    }
    
    def __init__(self):
        """Initialize theme manager."""
        self.current_theme = "hacker_dark"
        self.styles_dir = Path(resource_path("src/gui/styles"))
        logger.info(f"Theme manager initialized with styles directory: {self.styles_dir}")
    
    def load_theme(self, theme_name: str) -> Optional[str]:
        """
        Load a theme's QSS stylesheet.
        
        Args:
            theme_name: Name of the theme to load
            
        Returns:
            QSS stylesheet content or None if loading fails
        """
        if theme_name not in self.THEMES:
            logger.error(f"Unknown theme: {theme_name}")
            return None
        
        qss_file = self.styles_dir / self.THEMES[theme_name]
        
        try:
            if not qss_file.exists():
                logger.error(f"QSS file not found: {qss_file}")
                return None
            
            with open(qss_file, 'r', encoding='utf-8') as f:
                stylesheet = f.read()
            
            logger.info(f"Loaded theme: {theme_name} from {qss_file}")
            return stylesheet
            
        except Exception as e:
            logger.error(f"Failed to load theme {theme_name}: {e}")
            return None
    
    def apply_theme(self, theme_name: str, app: Optional[QApplication] = None) -> bool:
        """
        Apply a theme to the application.
        
        Args:
            theme_name: Name of the theme to apply
            app: QApplication instance (uses QApplication.instance() if None)
            
        Returns:
            True if theme was applied successfully, False otherwise
        """
        stylesheet = self.load_theme(theme_name)
        
        if stylesheet is None:
            return False
        
        if app is None:
            app = QApplication.instance()
        
        if app is None:
            logger.error("No QApplication instance found")
            return False
        
        try:
            app.setStyleSheet(stylesheet)
            self.current_theme = theme_name
            logger.info(f"Applied theme: {theme_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply theme {theme_name}: {e}")
            return False
    
    def get_current_theme(self) -> str:
        """Get the name of the currently active theme."""
        return self.current_theme
    
    def get_available_themes(self) -> list:
        """Get a list of available theme names."""
        return list(self.THEMES.keys())
    
    def reload_theme(self, app: Optional[QApplication] = None) -> bool:
        """
        Reload the current theme (hot-reload for development).
        
        Args:
            app: QApplication instance (uses QApplication.instance() if None)
            
        Returns:
            True if theme was reloaded successfully, False otherwise
        """
        logger.info(f"Reloading theme: {self.current_theme}")
        return self.apply_theme(self.current_theme, app)


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get the global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
