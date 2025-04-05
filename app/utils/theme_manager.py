import os
import threading
from enum import Enum
from platform import system
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
        self._is_macos = system() == "Darwin"
        
        # Set up platform-specific theme change detection
        if self._is_macos:
            self._setup_macos_theme_detection()
        else:
            self._setup_other_platforms_theme_detection()

    def _setup_macos_theme_detection(self):
        """Set up native notification listening for macOS appearance changes"""
        try:
            import objc
            from Foundation import NSDistributedNotificationCenter, NSObject
            
            # Create a delegate class to receive notifications
            class AppearanceChangeDelegate(NSObject):
                def initWithCallback_(self, callback):
                    self = objc.super(AppearanceChangeDelegate, self).init()
                    self.callback = callback
                    return self
                
                def appearanceChanged_(self, notification):
                    self.callback()
            
            # Create and retain the delegate
            self._delegate = AppearanceChangeDelegate.alloc().initWithCallback_(self._check_macos_theme_changed)
            
            # Register for appearance change notifications
            notification_center = NSDistributedNotificationCenter.defaultCenter()
            notification_center.addObserver_selector_name_object_(
                self._delegate,
                objc.selector(self._delegate.appearanceChanged_, signature=b'v@:@'),
                'AppleInterfaceThemeChangedNotification',
                None
            )
        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"Failed to set up macOS theme detection: {e}")
            # Fallback to a simple initialization without live updates

    def _setup_other_platforms_theme_detection(self):
        """Set up theme detection for Windows and other platforms"""
        try:
            import darkdetect
            t = threading.Thread(target=darkdetect.listener, args=(self._on_system_theme_change,))
            t.daemon = True
            t.start()
        except (ImportError, AttributeError, RuntimeError) as e:
            print(f"Failed to set up theme detection: {e}")

    def _check_macos_theme_changed(self):
        """Called when macOS system appearance changes"""
        if self.get_theme() == Theme.SYSTEM.value:
            self.apply_theme()

    def _on_system_theme_change(self, is_dark):
        """Called when system theme changes on non-macOS platforms"""
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
        
    def _get_system_theme(self):
        """Safely detect system theme"""
        try:
            import darkdetect
            is_dark = darkdetect.isDark()
            return Theme.DARK.value if is_dark else Theme.LIGHT.value
        except (ImportError, AttributeError, RuntimeError):
            # Fallback to light theme if detection fails
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