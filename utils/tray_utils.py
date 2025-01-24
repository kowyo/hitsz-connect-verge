from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PySide6.QtGui import QIcon
import platform
from .common import get_resource_path

def create_tray_menu(window, tray_icon):
    """Create and set up the system tray menu"""
    menu = QMenu()
    show_action = menu.addAction("打开面板")
    show_action.triggered.connect(window.show)
    hide_action = menu.addAction("隐藏面板")
    hide_action.triggered.connect(window.hide)
    quit_action = menu.addAction("退出")
    quit_action.triggered.connect(window.quit_app)
    
    tray_icon.setContextMenu(menu)
    tray_icon.activated.connect(lambda reason: tray_icon_activated(reason, window))

def tray_icon_activated(reason, window):
    """Handle tray icon activation"""
    if reason == QSystemTrayIcon.DoubleClick:
        window.show()
        window.activateWindow()

def handle_close_event(window, event, tray_icon):
    """Handle window close event"""
    if tray_icon.isVisible():
        window.hide()
        event.ignore()
    else:
        window.quit_app()

def quit_app(window, tray_icon):
    """Quit the application"""
    window.stop_connection()
    tray_icon.hide()
    QApplication.quit()

def init_tray_icon(window):
    """Initialize system tray icon and menu"""
    tray_icon = QSystemTrayIcon(window)
    
    # Set icon based on platform
    if platform.system() == "Windows":
        icon_path = "assets/icon.ico"
    elif platform.system() == "Darwin":
        icon_path = "assets/icon.icns"
    elif platform.system() == "Linux":
        icon_path = "assets/icon.png"
    
    tray_icon.setIcon(QIcon(get_resource_path(icon_path)))
    create_tray_menu(window, tray_icon)
    tray_icon.show()
    return tray_icon
