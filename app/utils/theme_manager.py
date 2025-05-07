import os
from enum import Enum
from PySide6.QtCore import QSettings, QObject, Signal, QEvent, Qt
from PySide6.QtGui import QGuiApplication

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
        
        QGuiApplication.instance().installEventFilter(self)

    def eventFilter(self, watched, event):
        """Event filter to catch system theme change events"""
        if event.type() == QEvent.ThemeChange:
            if self.get_theme() == Theme.SYSTEM.value:
                self.apply_theme()
        return super().eventFilter(watched, event)
        
    def get_theme(self):
        """Get current theme preference from settings"""
        return self.settings.value("theme", Theme.SYSTEM.value)
    
    def set_theme(self, theme):
        """Save theme preference to settings"""
        if isinstance(theme, Theme):
            theme = theme.value
        self.settings.setValue("theme", theme)
        self.apply_theme(theme)
        
    def _get_system_theme(self):
        """Detect system theme using Qt native API"""
        color_scheme = QGuiApplication.styleHints().colorScheme()
        if color_scheme == Qt.ColorScheme.Dark:
            return Theme.DARK.value
        else:
            return Theme.LIGHT.value
            
    def apply_theme(self, theme=None):
        """Apply the specified theme or the saved theme preference"""
        if theme is None:
            theme = self.get_theme()
            
        # Determine if we should use dark mode based on system or explicit setting
        if theme == Theme.SYSTEM.value:
            theme = self._get_system_theme()
            
        # Load the appropriate stylesheet
        theme_file = f"{theme}.qss"
        style_path = os.path.join(self._themes_dir, theme_file)
        
        if os.path.exists(style_path):
            with open(style_path, "r") as f:
                self.app.setStyleSheet(f.read())
                self.themeChanged.emit(theme)