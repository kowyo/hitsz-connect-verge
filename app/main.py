from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from platform import system
if system() == "Darwin":
    from utils.macos_utils import hide_dock_icon
from common import resources
from views.main_window import MainWindow

# Run the application
if __name__ == "__main__":
    app = QApplication()
    window = MainWindow() 
    
    if system() == "Windows":
        font = app.font()
        font.setFamily("Microsoft YaHei UI")
        app.setFont(font)

    if system() == "Windows":
        app.setWindowIcon(QIcon(':/icons/icon.ico'))
    elif system() == "Darwin":
        app.setWindowIcon(QIcon(':/icons/icon.icns'))
    elif system() == "Linux":
        app.setWindowIcon(QIcon(':/icons/icon.png'))
    
    if not window.silent_mode:
        window.show()
    
    if system() == "Darwin":
        hide_dock_icon(window.hide_dock_icon)

    app.exec()
