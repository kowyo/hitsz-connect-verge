import sys
import signal
import atexit
import logging

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from platform import system

if system() == "Darwin":
    from utils.macos_utils import hide_dock_icon
from common import resources
from views.main_window import MainWindow

logger = logging.getLogger(__name__)

# Global variables for cleanup
app = None
window = None


def cleanup_handler():
    """Cleanup function to be called on exit"""
    global window
    if window:
        try:
            window.stop_connection()
        except Exception as e:
            # Avoid swallowing SystemExit/KeyboardInterrupt by catching only Exception
            logger.debug("Error during cleanup stop_connection: %s", e)


def signal_handler(signum, frame):
    """Handle system signals for graceful shutdown"""
    global app
    cleanup_handler()
    if app:
        app.quit()
    sys.exit(0)


# Run the application
if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()

    # Register cleanup handlers
    atexit.register(cleanup_handler)
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

    # On Windows, also handle SIGBREAK
    if system() == "Windows":
        signal.signal(signal.SIGBREAK, signal_handler)

    if system() == "Windows":
        font = app.font()
        font.setFamily("Microsoft YaHei UI")
        app.setFont(font)

    if system() == "Windows":
        app.setWindowIcon(QIcon(":/icons/icon.ico"))
    elif system() == "Darwin":
        app.setWindowIcon(QIcon(":/icons/icon.icns"))
    elif system() == "Linux":
        app.setWindowIcon(QIcon(":/icons/icon.png"))

    if not window.silent_mode:
        window.show()

    if system() == "Darwin":
        hide_dock_icon(window.hide_dock_icon)

    app.exec()
