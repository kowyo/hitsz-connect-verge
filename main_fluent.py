from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
)
from qfluentwidgets import (PushButton, CheckBox, LineEdit, TextEdit, PasswordLineEdit, 
                          BodyLabel, TogglePushButton, IconInfoBadge, FluentIcon)
from PySide6.QtGui import QIcon
import platform
from utils.tray_utils import handle_close_event, quit_app, init_tray_icon
from utils.credential_utils import load_credentials, save_credentials
from utils.connection_utils import start_connection, stop_connection
from utils.common import get_resource_path, get_version
from utils.menu_utils import setup_menubar

VERSION = get_version()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HITSZ Connect Verge")
        self.setFixedSize(300, 450)
        self.service_name = "hitsz-connect-verge"
        self.username_key = "username"    
        self.password_key = "password"    
        
        self.tray_icon = init_tray_icon(self)
        
        self.worker = None
        setup_menubar(self, VERSION)
        self.setup_ui()
        self.load_credentials()

    def setup_ui(self):
        # Layouts
        layout = QVBoxLayout()
        
        # Account and Password
        layout.addWidget(BodyLabel("用户名"))
        self.username_input = LineEdit(self)  # Add self as parent
        layout.addWidget(self.username_input)

        # layout.PasswordLineEdit()
        layout.addWidget(BodyLabel("密码"))
        self.password_input = PasswordLineEdit(self)  # Add self as parent
        layout.addWidget(self.password_input)

        layout.addSpacing(5)
        self.remember_cb = CheckBox("记住密码")
        layout.addWidget(self.remember_cb)
        layout.addSpacing(5)

        # Server and DNS
        # layout.addWidget(BodyLabel("SSL VPN 服务端地址"))
        self.server_input = LineEdit(self)
        self.server_input.setText("vpn.hitsz.edu.cn")
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
        status_layout.addStretch()
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
        self.connect_button.toggled.connect(lambda: self.connect_button.setText("断开") if self.connect_button.isChecked() else self.connect_button.setText("连接"))
        self.connect_button.clicked.connect(self.save_credentials)
        button_layout.addWidget(self.connect_button)

        button_layout.addStretch()
        self.exit_button = PushButton("退出")
        self.exit_button.clicked.connect(self.stop_connection) 
        self.exit_button.clicked.connect(self.quit_app)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        # Set main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        handle_close_event(self, event, self.tray_icon)

    def quit_app(self):
        quit_app(self, self.tray_icon)

    def load_credentials(self):
        load_credentials(self, self.service_name, self.username_key, self.password_key)

    def save_credentials(self):
        save_credentials(self, self.service_name, self.username_key, self.password_key)

    def start_connection(self):
        start_connection(self)

    def stop_connection(self):
        stop_connection(self)

    def toggle_advanced_settings(self, checked):
        QMainWindow.resize(self, 300, 450 if checked else 300)
        self.server_input.setVisible(checked)
        self.dns_input.setVisible(checked)

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    
    if platform.system() == "Windows":
        icon_path = get_resource_path("assets/icon.ico")
    elif platform.system() == "Darwin":
        icon_path = get_resource_path("assets/icon.icns")
    elif platform.system() == "Linux":
        icon_path = get_resource_path("assets/icon.png")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    window = MainWindow()
    window.show()
    app.exec()
