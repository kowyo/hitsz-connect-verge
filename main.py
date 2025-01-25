from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QLineEdit, QCheckBox, QPushButton, 
    QTextEdit, QVBoxLayout, QHBoxLayout, QWidget
)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from platform import system
from utils.tray_utils import handle_close_event, quit_app, init_tray_icon
from utils.credential_utils import load_credentials, save_credentials
from utils.connection_utils import start_connection, stop_connection
from utils.common import get_resource_path, get_version
from utils.password_utils import toggle_password_visibility
from utils.menu_utils import setup_menubar
from utils.config_utils import load_config

VERSION = get_version()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HITSZ Connect Verge")
        self.setMinimumSize(300, 450)
        self.service_name = "hitsz-connect-verge"
        self.username_key = "username"    
        self.password_key = "password"    
        
        self.worker = None
        setup_menubar(self, VERSION)
        self.setup_ui()
        self.load_credentials()
        self.load_advanced_settings()
        self.tray_icon = init_tray_icon(self)
        
        if self.connect_startup:
            self.connect_button.setChecked(True)
        
        if self.silent_mode:
            QTimer.singleShot(1000, lambda: self.hide())

    def setup_ui(self):
        # Layouts
        layout = QVBoxLayout()
        
        # Account and Password
        layout.addWidget(QLabel("用户名"))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("密码"))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.show_password_cb = QCheckBox("显示密码")
        self.show_password_cb.stateChanged.connect(
            lambda checked: toggle_password_visibility(self.password_input, checked)
        )
        layout.addWidget(self.show_password_cb)

        self.remember_cb = QCheckBox("记住密码")
        layout.addWidget(self.remember_cb)
        
        # Status and Output
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("运行信息"))
        layout.addLayout(status_layout)
        status_layout.addStretch()
        self.status_label = QLabel("状态: 未连接")
        status_layout.addWidget(self.status_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("连接")
        self.connect_button.setCheckable(True)
        self.connect_button.toggled.connect(lambda: self.start_connection() if self.connect_button.isChecked() else self.stop_connection())
        self.connect_button.toggled.connect(lambda: self.connect_button.setText("断开") if self.connect_button.isChecked() else self.connect_button.setText("连接"))
        self.connect_button.clicked.connect(self.save_credentials)
        button_layout.addWidget(self.connect_button)

        button_layout.addStretch()

        self.exit_button = QPushButton("退出")
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

    def load_advanced_settings(self):
        """Load advanced settings from config file"""
        config = load_config()
        self.server_address = config['server']
        self.dns_server = config['dns']
        self.proxy = config['proxy']
        self.connect_startup = config['connect_startup']
        self.silent_mode = config['silent_mode']

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    
    if system() == "Windows":
        icon_path = get_resource_path("assets/icon.ico")
    elif system() == "Darwin":
        icon_path = get_resource_path("assets/icon.icns")
    elif system() == "Linux":
        icon_path = get_resource_path("assets/icon.png")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    window = MainWindow()
    window.show()
    app.exec()
