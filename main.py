import keyring
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QCheckBox, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QWidget, QSystemTrayIcon, QMenu
)
from qfluentwidgets import (PushButton, CheckBox, LineEdit, TextEdit, PasswordLineEdit, BodyLabel, TogglePushButton, PrimaryPushButton, DotInfoBadge, IconInfoBadge, FluentIcon)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QThread, Signal
import subprocess
import platform
import shlex
if platform.system() == "Windows":
    from subprocess import CREATE_NO_WINDOW


def set_windows_proxy(enable, server=None, port=None):
    """Manage proxy settings for Windows using the Windows Registry."""
    if platform.system() == "Windows":
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
            # Enable proxy for the service
            subprocess.run(['networksetup', '-setwebproxy', service, server, str(port)])
            subprocess.run(['networksetup', '-setsecurewebproxy', service, server, str(port)])
        else:
            # Disable proxy for the serviceS
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
        if platform.system() == "Windows" and self.proxy_enabled:
            set_windows_proxy(True, server="127.0.0.1", port=1081)
        elif platform.system() == "Darwin" and self.proxy_enabled:
            set_macos_proxy(True, server="127.0.0.1", port=1081)
        elif platform.system() == "Linux" and self.proxy_enabled:
            set_linux_proxy(True, server="127.0.0.1", port=1081)
    
        if platform.system() == "Windows":
            creation_flags = CREATE_NO_WINDOW
        elif platform.system() == "Darwin":
            creation_flags = 0
        elif platform.system() == "Linux":
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
        
        if platform.system() == "Windows" and self.proxy_enabled:
            set_windows_proxy(False)
        elif platform.system() == "Darwin" and self.proxy_enabled:
            set_macos_proxy(False)
        elif platform.system() == "Linux" and self.proxy_enabled:
            set_linux_proxy(False)
        
        self.finished.emit()

    def stop(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

# Main Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HITSZ Connect Verge")
        self.setFixedSize(300, 450)
        self.service_name = "hitsz-connect-verge"
        self.username_key = "username"    
        self.password_key = "password"    
        
        # Initialize system tray icon
        self.tray_icon = QSystemTrayIcon(self)
        if platform.system() == "Windows":
            icon_path = self.get_resource_path("assets/Graphicloads-Colorful-Long-Shadow-Cloud.ico")
        elif platform.system() == "Darwin":
            icon_path = self.get_resource_path("assets/Graphicloads-Colorful-Long-Shadow-Cloud.icns")
        elif platform.system() == "Linux":
            icon_path = self.get_resource_path("assets/Graphicloads-Colorful-Long-Shadow-Cloud.png")
        self.tray_icon.setIcon(QIcon(icon_path))
        self.create_tray_menu()
        self.tray_icon.show()
        
        self.worker = None
        self.setup_ui()
        self.load_credentials()

    def setup_ui(self):
        # Layouts
        layout = QVBoxLayout()
        
        # Account and Password
        layout.addWidget(BodyLabel("账号"))
        self.username_input = LineEdit(self)  # Add self as parent
        layout.addWidget(self.username_input)

        # layout.PasswordLineEdit()
        layout.addWidget(BodyLabel("密码"))
        self.password_input = PasswordLineEdit(self)  # Add self as parent
        layout.addWidget(self.password_input)
        # self.password_input.setEchoMode(QLineEdit.Password)  # Still use QLineEdit enum
        # layout.addWidget(self.password_input)

        # self.show_password_cb = CheckBox("显示密码")
        # self.show_password_cb.stateChanged.connect(self.toggle_password_visibility)
        # layout.addWidget(self.show_password_cb)

        layout.addSpacing(5)
        self.remember_cb = CheckBox("记住密码")
        layout.addWidget(self.remember_cb)
        layout.addSpacing(5)

        # Server and DNS
        # layout.addWidget(BodyLabel("SSL VPN 服务端地址"))
        self.server_input = LineEdit(self)  # Add self as parent
        self.server_input.setText("vpn.hitsz.edu.cn")  # Use setText after creation
        self.server_input.hide()
        # layout.addWidget(self.server_input)

        self.dns_input = LineEdit(self)
        self.dns_input.setText("10.248.98.30") 
        self.dns_input.hide()
        
        # Proxy Control
        self.proxy_cb = CheckBox("自动配置代理")
        self.proxy_cb.setChecked(True)
        # layout.addWidget(self.proxy_cb)

        layout.addSpacing(5)
        # Status and Output
        status_layout = QHBoxLayout()
        status_layout.addWidget(BodyLabel("运行信息"))
        status_layout.addStretch()  # Add stretch to push status label to the right
        self.status_icon = IconInfoBadge(FluentIcon.CANCEL_MEDIUM)
        status_layout.addWidget(self.status_icon)
        self.status_label = BodyLabel("状态: 未连接")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        self.output_text = TextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.connect_button = TogglePushButton("连接")
        self.connect_button.toggled.connect(lambda: self.start_connection() if self.connect_button.isChecked() else self.stop_connection())
        self.connect_button.clicked.connect(self.save_credentials)
        button_layout.addWidget(self.connect_button)

        # self.disconnect_button = PushButton("断开")
        # self.disconnect_button.clicked.connect(self.stop_connection)
        # button_layout.addWidget(self.disconnect_button)

        button_layout.addStretch()
        self.exit_button = PushButton("退出")
        self.exit_button.clicked.connect(self.stop_connection) 
        self.exit_button.clicked.connect(self.close)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        # Set main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_tray_menu(self):
        menu = QMenu()
        show_action = menu.addAction("打开面板")
        show_action.triggered.connect(self.show)
        hide_action = menu.addAction("隐藏面板")
        hide_action.triggered.connect(self.hide)
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self.quit_app)
        
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.activateWindow()

    def closeEvent(self, event):
        if self.tray_icon.isVisible():
            self.hide()
            event.ignore()
        else:
            self.quit_app()

    def quit_app(self):
        self.stop_connection()
        self.tray_icon.hide()
        QApplication.quit()

    def toggle_password_visibility(self):
        if self.show_password_cb.isChecked():
            self.password_input.setEchoMode(QLineEdit.Normal)  # Still use QLineEdit enum
        else:
            self.password_input.setEchoMode(QLineEdit.Password)  # Still use QLineEdit enum

    def load_credentials(self):
        """Load stored credentials from keyring."""
        saved_username = keyring.get_password(self.service_name, self.username_key)
        saved_password = keyring.get_password(self.service_name, self.password_key)
        if saved_username:
            self.username_input.setText(saved_username)
        if saved_password:
            self.password_input.setText(saved_password)
            self.remember_cb.setChecked(True)

    def save_credentials(self):
        """Save credentials to keyring if 'Remember Password' is checked."""
        username = self.username_input.text()
        password = self.password_input.text()

        if self.remember_cb.isChecked():
            keyring.set_password(self.service_name, self.username_key, username)
            keyring.set_password(self.service_name, self.password_key, password)
        else:
            # Remove credentials if the user unchecks the remember box
            keyring.delete_password(self.service_name, self.username_key)
            keyring.delete_password(self.service_name, self.password_key)

        # self.status_label.setText("状态: 凭据已保存" if self.remember_cb.isChecked() else "状态: 凭据未保存")

    def start_connection(self):
        if self.worker and self.worker.isRunning():
            self.status_label.setText("状态: 已连接")
            self.status_icon.setIcon(FluentIcon.ACCEPT_MEDIUM)
            return

        username = self.username_input.text()
        password = self.password_input.text()
        server_address = self.server_input.text()
        dns_server_address = self.dns_input.text()

        import os, sys
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
            
        if platform.system() == "Windows":
            command = os.path.join(base_path, "core", "zju-connect.exe")
        else:
            command = os.path.join(base_path, "core", "zju-connect")
            # Ensure executable permissions on Unix-like systems
            if os.path.exists(command):
                os.chmod(command, 0o755)

        command_args = [
            command, "-server", shlex.quote(server_address),
            "-zju-dns-server", shlex.quote(dns_server_address),
            "-username", shlex.quote(username), "-password", shlex.quote(password)
        ]
        
        self.worker = CommandWorker(command_args, self.proxy_cb.isChecked())
        self.worker.output.connect(self.append_output)
        self.worker.finished.connect(self.on_connection_finished)
        self.worker.start()

        self.status_label.setText("状态: 已连接")
        self.status_icon.setIcon(FluentIcon.ACCEPT_MEDIUM)

    def stop_connection(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait()
            self.worker = None

        self.status_label.setText("状态: 未连接")
        self.status_icon.setIcon(FluentIcon.CANCEL_MEDIUM)

    def append_output(self, text):
        self.output_text.append(text)

    def on_connection_finished(self):
        self.worker = None
        self.status_label.setText("状态: 未连接")
        self.status_icon.setIcon(FluentIcon.CANCEL_MEDIUM)

    @staticmethod
    def get_resource_path(relative_path):
        """Get absolute path to resource, works for dev and for PyInstaller"""
        import os, sys
        if getattr(sys, 'frozen', False):
            # Running as bundled exe
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    
    if platform.system() == "Windows":
        icon_path = MainWindow.get_resource_path("assets/Graphicloads-Colorful-Long-Shadow-Cloud.ico")
    elif platform.system() == "Darwin":
        icon_path = MainWindow.get_resource_path("assets/Graphicloads-Colorful-Long-Shadow-Cloud.icns")
    elif platform.system() == "Linux":
        icon_path = MainWindow.get_resource_path("assets/Graphicloads-Colorful-Long-Shadow-Cloud.png")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    window = MainWindow()
    window.show()
    app.exec()
