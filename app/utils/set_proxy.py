import subprocess
import os
import signal
import time
from platform import system

from PySide6.QtCore import QThread, Signal

if system() == "Windows":
    from subprocess import CREATE_NO_WINDOW


def get_proxy_settings(window):
    """Get proxy settings from window HTTP and SOCKS binds"""
    http_host, http_port = "127.0.0.1", None
    socks_host, socks_port = "127.0.0.1", None

    if hasattr(window, "http_bind") and window.http_bind:
        try:
            http_port = int(window.http_bind)
        except ValueError:
            pass

    if hasattr(window, "socks_bind") and window.socks_bind:
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
        self._should_stop = False
        self._proxy_handlers = {
            "Windows": set_windows_proxy,
            "Darwin": set_macos_proxy,
            "Linux": set_linux_proxy,
        }
        # Derive executable name for robust cleanup
        try:
            self.exe_name = os.path.basename(self.command_args[0]) if self.command_args else None
        except Exception:
            self.exe_name = None

    def run(self):
        error_occurred = False
        try:
            # Check if we should stop before starting
            if self._should_stop:
                return

            # Set proxy if enabled
            if self.proxy_enabled and self.window:
                try:
                    proxy_handler = self._proxy_handlers.get(system())
                    if proxy_handler:
                        proxy_handler(True, *get_proxy_settings(self.window))
                except Exception as e:
                    self.output.emit(f"Failed to set proxy: {str(e)}\n")

            # Check again before starting process
            if self._should_stop:
                return

            # Run process
            try:
                creation_flags = CREATE_NO_WINDOW if system() == "Windows" else 0
                self.process = subprocess.Popen(
                    self.command_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    encoding="utf-8",
                    creationflags=creation_flags,
                )
            except FileNotFoundError as e:
                self.output.emit(f"Failed to start process: executable not found\n{str(e)}\n")
                error_occurred = True
                return
            except Exception as e:
                self.output.emit(f"Process start failed: {str(e)}\n")
                error_occurred = True
                return

            # Read output with stop checking
            try:
                while not self._should_stop and self.process.poll() is None:
                    line = self.process.stdout.readline()
                    if line:
                        self.output.emit(line)
                    else:
                        # Small delay to prevent busy waiting
                        time.sleep(0.1)
                
                # Read any remaining output
                if not self._should_stop:
                    remaining_output = self.process.stdout.read()
                    if remaining_output:
                        self.output.emit(remaining_output)
                    
                    # Wait for process and check exit code
                    exit_code = self.process.wait()
                    if exit_code != 0:
                        self.output.emit(f"Process exited with non-zero code: {exit_code}\n")
                        error_occurred = True
                        
            except Exception as e:
                self.output.emit(f"Error reading process output: {str(e)}\n")
                error_occurred = True

        except Exception as e:
            self.output.emit(f"Unexpected error during thread run: {str(e)}\n")
            error_occurred = True
        finally:
            # Disable proxy on completion
            if self.proxy_enabled:
                try:
                    proxy_handler = self._proxy_handlers.get(system())
                    if proxy_handler:
                        proxy_handler(False)
                except Exception as e:
                    self.output.emit(f"Proxy cleanup failed: {str(e)}\n")
            
            # Small delay to allow socket cleanup
            time.sleep(0.5)
            
            # Always emit finished signal to ensure proper cleanup
            try:
                self.finished.emit()
            except RuntimeError:
                # Signal connection may have been destroyed, but that's ok
                pass

    def stop(self):
        # Set stop flag first
        self._should_stop = True
        
        # Request thread interruption
        self.requestInterruption()
        
        if self.process:
            try:
                # First try graceful termination
                if system() == "Windows":
                    # On Windows, use taskkill for a more forceful termination
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                        capture_output=True,
                        timeout=5
                    )
                else:
                    # On Unix-like systems, try SIGTERM first
                    self.process.terminate()
                    try:
                        # Wait up to 3 seconds for graceful shutdown
                        self.process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        # If process doesn't terminate gracefully, kill it
                        self.process.kill()
                        self.process.wait(timeout=2)
                
                # Additional cleanup: try to kill any remaining zju-connect processes
                self._cleanup_remaining_processes()
                
            except Exception as e:
                # If all else fails, force kill
                try:
                    self.process.kill()
                    self.process.wait(timeout=2)
                except:
                    pass
            finally:
                self.process = None
    
    def _cleanup_remaining_processes(self):
        """Clean up any remaining processes of the current executable that might be holding ports"""
        try:
            if not self.exe_name:
                return
            if system() == "Windows":
                # Find and kill any remaining processes by image name
                result = subprocess.run(
                    ["tasklist", "/FI", f"IMAGENAME eq {self.exe_name}", "/FO", "CSV"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if self.exe_name in result.stdout:
                    subprocess.run(
                        ["taskkill", "/F", "/IM", self.exe_name],
                        capture_output=True,
                        timeout=5
                    )
            else:
                # On Unix-like systems, find and kill processes by executable name
                result = subprocess.run(
                    ["pgrep", "-f", self.exe_name],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    pids = result.stdout.strip().split('\n')
                    for pid in pids:
                        try:
                            subprocess.run(
                                ["kill", "-TERM", pid],
                                capture_output=True,
                                timeout=2
                            )
                        except:
                            # If TERM fails, try KILL
                            try:
                                subprocess.run(
                                    ["kill", "-KILL", pid],
                                    capture_output=True,
                                    timeout=2
                                )
                            except:
                                pass
        except Exception:
            # Cleanup is best effort, don't fail if it doesn't work
            pass


def set_windows_proxy(
    enable, http_host=None, http_port=None, socks_host=None, socks_port=None
):
    """Manage proxy settings for Windows using the Windows Registry."""
    if system() != "Windows":
        return

    import winreg as reg
    import ctypes

    with reg.OpenKey(
        reg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
        0,
        reg.KEY_ALL_ACCESS,
    ) as internet_settings:
        reg.SetValueEx(
            internet_settings, "ProxyEnable", 0, reg.REG_DWORD, 1 if enable else 0
        )
        if enable and http_host and http_port:
            reg.SetValueEx(
                internet_settings,
                "ProxyServer",
                0,
                reg.REG_SZ,
                f"{http_host}:{http_port}",
            )

    # Refresh system proxy settings
    ctypes.windll.Wininet.InternetSetOptionW(0, 37, 0, 0)
    ctypes.windll.Wininet.InternetSetOptionW(0, 39, 0, 0)


def set_macos_proxy(
    enable, http_host=None, http_port=None, socks_host=None, socks_port=None
):
    """Manage proxy settings for macOS using networksetup."""
    if system() != "Darwin":
        return

    services = (
        subprocess.check_output(["networksetup", "-listallnetworkservices"])
        .decode()
        .split("\n")[1:]
    )
    services = [s for s in services if s and not s.startswith("*")]

    for service in services:
        if enable and http_host and http_port:
            subprocess.run(
                ["networksetup", "-setwebproxy", service, http_host, str(http_port)]
            )
            subprocess.run(
                [
                    "networksetup",
                    "-setsecurewebproxy",
                    service,
                    http_host,
                    str(http_port),
                ]
            )
            if socks_host and socks_port:
                subprocess.run(
                    [
                        "networksetup",
                        "-setsocksfirewallproxy",
                        service,
                        socks_host,
                        str(socks_port),
                    ]
                )
        else:
            subprocess.run(["networksetup", "-setwebproxystate", service, "off"])
            subprocess.run(["networksetup", "-setsecurewebproxystate", service, "off"])
            subprocess.run(
                ["networksetup", "-setsocksfirewallproxystate", service, "off"]
            )


def set_linux_proxy(
    enable, http_host=None, http_port=None, socks_host=None, socks_port=None
):
    """Manage proxy settings for Linux using gsettings."""
    if system() != "Linux":
        return

    if enable and http_host and http_port:
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "manual"])
        for protocol in ["http", "https"]:
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    f"org.gnome.system.proxy.{protocol}",
                    "host",
                    http_host,
                ]
            )
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    f"org.gnome.system.proxy.{protocol}",
                    "port",
                    str(http_port),
                ]
            )
        if socks_host and socks_port:
            subprocess.run(
                ["gsettings", "set", "org.gnome.system.proxy.socks", "host", socks_host]
            )
            subprocess.run(
                [
                    "gsettings",
                    "set",
                    "org.gnome.system.proxy.socks",
                    "port",
                    str(socks_port),
                ]
            )
    else:
        subprocess.run(["gsettings", "set", "org.gnome.system.proxy", "mode", "none"])
