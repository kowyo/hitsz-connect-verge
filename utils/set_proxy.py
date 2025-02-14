import subprocess
from platform import system

from PySide6.QtCore import QThread, Signal
if system() == "Windows":
    from subprocess import CREATE_NO_WINDOW

def get_proxy_settings(window):
    """Get proxy settings from window HTTP and SOCKS binds"""
    http_host, http_port = "127.0.0.1", None
    socks_host, socks_port = "127.0.0.1", None
    
    if hasattr(window, 'http_bind') and window.http_bind:
        try:
            http_port = int(window.http_bind)
        except ValueError:
            pass
                
    if hasattr(window, 'socks_bind') and window.socks_bind:
        try:
            socks_port = int(window.socks_bind)
        except ValueError:
            pass
                
    return http_host, http_port, socks_host, socks_port

class CommandWorker(QThread):
    output = Signal(str)
    finished = Signal()

    def __init__(self, command_args, proxy_enabled, window=None):
        super().__init__()
        self.command_args = command_args
        self.proxy_enabled = proxy_enabled
        self.window = window
        self.process = None
        self._proxy_handlers = {
            "Windows": set_windows_proxy,
            "Darwin": set_macos_proxy,
            "Linux": set_linux_proxy
        }

    def run(self):
        try:
            # Set proxy if enabled
            if self.proxy_enabled and self.window:
                proxy_handler = self._proxy_handlers.get(system())
                if proxy_handler:
                    proxy_handler(True, *get_proxy_settings(self.window))

            # Run process
            creation_flags = CREATE_NO_WINDOW if system() == "Windows" else 0
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
        finally:
            # Disable proxy on completion
            if self.proxy_enabled:
                proxy_handler = self._proxy_handlers.get(system())
                if proxy_handler:
                    proxy_handler(False)
            self.finished.emit()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

def set_windows_proxy(enable, http_host=None, http_port=None, socks_host=None, socks_port=None):
    """Manage proxy settings for Windows using the Windows Registry."""
    if system() != "Windows":
        return

    import winreg as reg
    import ctypes
    
    with reg.OpenKey(reg.HKEY_CURRENT_USER,
                    r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                    0, reg.KEY_ALL_ACCESS) as internet_settings:
        reg.SetValueEx(internet_settings, 'ProxyEnable', 0, reg.REG_DWORD, 1 if enable else 0)
        if enable and http_host and http_port:
            reg.SetValueEx(internet_settings, 'ProxyServer', 0, reg.REG_SZ, f"{http_host}:{http_port}")

    # Refresh system proxy settings
    ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)

def set_macos_proxy(enable, http_host=None, http_port=None, socks_host=None, socks_port=None):
    """Manage proxy settings for macOS using networksetup."""
    if system() != "Darwin":
        return

    services = subprocess.check_output(['networksetup', '-listallnetworkservices']).decode().split('\n')[1:]
    services = [s for s in services if s and not s.startswith('*')]

    for service in services:
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
    if system() != "Linux":
        return

    if enable and http_host and http_port:
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'manual'])
        for protocol in ['http', 'https']:
            subprocess.run(['gsettings', 'set', f'org.gnome.system.proxy.{protocol}', 'host', http_host])
            subprocess.run(['gsettings', 'set', f'org.gnome.system.proxy.{protocol}', 'port', str(http_port)])
        if socks_host and socks_port:
            subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.socks', 'host', socks_host])
            subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy.socks', 'port', str(socks_port)])
    else:
        subprocess.run(['gsettings', 'set', 'org.gnome.system.proxy', 'mode', 'none'])