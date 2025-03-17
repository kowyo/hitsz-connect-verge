from PySide6.QtCore import QObject, Signal, QRunnable, QThreadPool, Slot
import requests
from requests.exceptions import RequestException
from packaging import version
import webbrowser

class UpdateSignals(QObject):
    """Signals for update checking process"""
    update_available = Signal(str)
    up_to_date = Signal()
    error = Signal(str)


class UpdateChecker(QRunnable):
    """Worker class to check for updates in background"""
    
    def __init__(self, repo_owner, repo_name, current_version):
        super().__init__()
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.current_version = current_version
        self.signals = UpdateSignals()
        
    @Slot()
    def run(self):
        try:
            latest_version = self.get_latest_version()
            if not latest_version:
                self.signals.error.emit("Failed to retrieve version information")
                return
                
            if version.parse(latest_version) > version.parse(self.current_version):
                self.signals.update_available.emit(latest_version)
            else:
                self.signals.up_to_date.emit()
                
        except Exception as e:
            self.signals.error.emit(f"Update check failed: {str(e)}")
    
    def get_latest_version(self):
        """Get the latest version from GitHub releases"""
        try:
            url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
            response = requests.get(url, timeout=10)
            return response.json()["tag_name"].lstrip('v')
        except RequestException as e:
            print(f"Failed to check for updates: {e}")
            return None
        except (KeyError, ValueError) as e:
            print(f"Failed to parse version information: {e}")
            return None


class UpdateService:
    """Service to handle update checking and notifications"""
    
    def __init__(self):
        self.thread_pool = QThreadPool()
    
    def check_for_updates(self, repo_owner, repo_name, current_version):
        worker = UpdateChecker(repo_owner, repo_name, current_version)
        self.thread_pool.start(worker)
        return worker.signals

    @staticmethod
    def open_download_page(repo_owner, repo_name):
        """Open the download page for the latest release"""
        url = f"https://github.com/{repo_owner}/{repo_name}/releases/latest"
        webbrowser.open(url)
