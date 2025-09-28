import sys
import signal
import atexit
import logging
from platform import system

logger = logging.getLogger(__name__)


def cleanup_handler(window):
    """Cleanup function to be called on exit"""
    if not window or not hasattr(window, "stop_connection"):
        return

    try:
        window.stop_connection()
    except (SystemExit, KeyboardInterrupt):
        raise  # 让系统级异常正常传播
    except Exception as e:
        logger.debug("Cleanup error: %s", e)


def register_cleanup_handlers(app, window):
    """Register cleanup and signal handlers for graceful shutdown."""
    atexit.register(cleanup_handler, window)

    def signal_handler(signum, frame):
        cleanup_handler(window)
        app and app.quit()
        sys.exit(0)

    # 注册信号处理器
    signals = [signal.SIGINT, signal.SIGTERM]
    if system() == "Windows":
        signals.append(signal.SIGBREAK)

    for sig in signals:
        signal.signal(sig, signal_handler)
