import subprocess
from platform import system
from utils.connection_utils import get_proxy_settings

from PySide6.QtCore import QThread, Signal
if system() == "Windows":
    from subprocess import CREATE_NO_WINDOW

# Worker Thread for Running Commands
class CommandWorker(QThread):
    output = Signal(str)
    finished = Signal()

    def __init__(self, command_args, proxy_enabled, window=None):
        super().__init__()
        self.command_args = command_args
        self.proxy_enabled = proxy_enabled
        self.window = window
        self.process = None

    def run(self):
        if self.proxy_enabled and self.window:
            http_host, http_port, socks_host, socks_port = get_proxy_settings(self.window)
            if system() == "Windows":
                set_windows_proxy(True, http_host=http_host, http_port=http_port, 
                                socks_host=socks_host, socks_port=socks_port)
            elif system() == "Darwin":
                set_macos_proxy(True, http_host=http_host, http_port=http_port,
                              socks_host=socks_host, socks_port=socks_port)
            elif system() == "Linux":
                set_linux_proxy(True, http_host=http_host, http_port=http_port,
                              socks_host=socks_host, socks_port=socks_port)
    
        if system() == "Windows":
            creation_flags = CREATE_NO_WINDOW
        elif system() == "Darwin":
            creation_flags = 0
        elif system() == "Linux":
            creation_flags = 0

        self.process = subprocess.Popen(
            self.command_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            encoding="utf-8",
            creationflags=creation_flags
        )
        for line in self.process.stdout:
            self.output.emit(line)
        self.process.wait()
        
        if system() == "Windows" and self.proxy_enabled:
            set_windows_proxy(False)
        elif system() == "Darwin" and self.proxy_enabled:
            set_macos_proxy(False)
        elif system() == "Linux" and self.proxy_enabled:
            set_linux_proxy(False)
        
        self.finished.emit()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

def set_windows_proxy(enable, http_host=None, http_port=None, socks_host=None, socks_port=None):
    """Manage proxy settings for Windows using the Windows Registry."""
    if system() == "Windows":
        import winreg as reg
        import ctypes
        
        internet_settings = reg.OpenKey(reg.HKEY_CURRENT_USER,
                                        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                        0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(internet_settings, 'ProxyEnable', 0, reg.REG_DWORD, 1 if enable else 0)
        if enable and http_host and http_port:
            proxy = f"{http_host}:{http_port}"
            reg.SetValueEx(internet_settings, 'ProxyServer', 0, reg.REG_SZ, proxy)
        ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
        ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
        reg.CloseKey(internet_settings)

def set_macos_proxy(enable, http_host=None, http_port=None, socks_host=None, socks_port=None):
    """Manage proxy settings for macOS using networksetup."""
    # Get list of network services
    network_services = subprocess.check_output(['networksetup', '-listallnetworkservices']).decode().split('\n')
    for service in network_services[1:]:
        if not service or service.startswith('*'):  # Skip empty lines and disabled services
            continue
            
        if enable and http_host and http_port:
            subprocess.run(['networksetup', '-setwebproxy', service, http_host, str(http_port)])
            subprocess.run(['networksetup', '-setsecurewebproxy', service, http_host, str(http_port)])
            if socks_host and socks_port:
                subprocess.run(['networksetup', '-setsocksfirewallproxy', service, socks_host, str(socks_port)])
        else:
            subprocess.run(['networksetup', '-setwebproxystate', service, 'off'])
            subprocess.run(['networksetup', '-setsecurewebproxystate', service, 'off'])
            subprocess.run(['networksetup', '-setsocksfirewallproxystate', service, 'off'])

def set_linux_proxy(enable, http_host=None, http_port=None, socks_host=None, socks_port=None):
    """Manage proxy settings for Linux using gsettings."""
    if enable and http_host and http_port:
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'manual'])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.http', 'host', http_host])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.http', 'port', str(http_port)])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.https', 'host', http_host])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.https', 'port', str(http_port)])
        if socks_host and socks_port:
            subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.socks', 'host', socks_host])
            subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.socks', 'port', str(socks_port)])
    else:
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'none'])