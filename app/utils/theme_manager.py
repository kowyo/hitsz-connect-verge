import os
import threading
import darkdetect
from enum import Enum
from PySide6.QtCore import QSettings, QObject, Signal

class Theme(Enum):
    LIGHT = "light"
    DARK = "dark"
    SYSTEM = "system"

class ThemeManager(QObject):
    themeChanged = Signal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = QSettings("Kowyo", "HITSZ Connect Verge")
        self._themes_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles")
        self._current_theme = None

        try:
            t = threading.Thread(target=darkdetect.listener, args=(self._on_system_theme_change,))
            t.daemon = True
            t.start()
        except (ImportError, AttributeError):
            pass

    def _on_system_theme_change(self, is_dark):
        """Called when system theme changes"""
        # Only react if we're using system theme
        if self.get_theme() == Theme.SYSTEM.value:
            self.apply_theme()
        
    def get_theme(self):
        """Get current theme preference from settings"""
        return self.settings.value("theme", Theme.SYSTEM.value)
    
    def set_theme(self, theme):
        """Save theme preference to settings"""
        if isinstance(theme, Theme):
            theme = theme.value
        self.settings.setValue("theme", theme)
        self.apply_theme(theme)
        
    def apply_theme(self, theme=None):
        """Apply the specified theme or the saved theme preference"""
        if theme is None:
            theme = self.get_theme()
            
        # Determine if we should use dark mode based on system or explicit setting
        if theme == Theme.SYSTEM.value:
            import darkdetect
            is_dark = darkdetect.isDark()
            theme = Theme.DARK.value if is_dark else Theme.LIGHT.value
            
        # Load the appropriate stylesheet
        theme_file = f"{theme}.qss"
        style_path = os.path.join(self._themes_dir, theme_file)
        
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.app.setStyleSheet(f.read())
                self.themeChanged.emit(theme)