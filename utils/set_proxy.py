import subprocess
from platform import system

from PySide6.QtCore import QThread, Signal
if system() == "Windows":
    from subprocess import CREATE_NO_WINDOW

# Worker Thread for Running Commands
class CommandWorker(QThread):
    output = Signal(str)
    finished = Signal()

    def __init__(self, command_args, proxy_enabled):
        super().__init__()
        self.command_args = command_args
        self.proxy_enabled = proxy_enabled
        self.process = None

    def run(self):
        if system() == "Windows" and self.proxy_enabled:
            set_windows_proxy(True, server="127.0.0.1", port=1081)
        elif system() == "Darwin" and self.proxy_enabled:
            set_macos_proxy(True, server="127.0.0.1", port=1081)
        elif system() == "Linux" and self.proxy_enabled:
            set_linux_proxy(True, server="127.0.0.1", port=1081)
    
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

def set_windows_proxy(enable, server=None, port=None):
    """Manage proxy settings for Windows using the Windows Registry."""
    if system() == "Windows":
        import winreg as reg
        import ctypes
        
        internet_settings = reg.OpenKey(reg.HKEY_CURRENT_USER,
                                        r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                                        0, reg.KEY_ALL_ACCESS)
        reg.SetValueEx(internet_settings, 'ProxyEnable', 0, reg.REG_DWORD, 1 if enable else 0)
        if enable and server and port:
            proxy = f"{server}:{port}"
            reg.SetValueEx(internet_settings, 'ProxyServer', 0, reg.REG_SZ, proxy)
        ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
        ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)
        reg.CloseKey(internet_settings)

def set_macos_proxy(enable, server=None, port=None):
    """Manage proxy settings for macOS using networksetup."""
    # Get list of network services
    network_services = subprocess.check_output(['networksetup', '-listallnetworkservices']).decode().split('\n')
    for service in network_services[1:]:
        if not service or service.startswith('*'):  # Skip empty lines and disabled services
            continue
            
        if enable and server and port:
            subprocess.run(['networksetup', '-setwebproxy', service, server, str(port)])
            subprocess.run(['networksetup', '-setsecurewebproxy', service, server, str(port)])
        else:
            subprocess.run(['networksetup', '-setwebproxystate', service, 'off'])
            subprocess.run(['networksetup', '-setsecurewebproxystate', service, 'off'])

def set_linux_proxy(enable, server=None, port=None):
    """Manage proxy settings for Linux using gsettings."""
    if enable and server and port:
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'manual'])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.http', 'host', server])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.http', 'port', str(port)])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.https', 'host', server])
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.https', 'port', str(port)])
    else:
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'none'])