from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout, QApplication
from PySide6.QtGui import QIcon
from .config_utils import save_config, load_config
from .startup_utils import set_launch_at_login, get_launch_at_login
from platform import system
from .macos_utils import hide_dock_icon
from utils.common import get_resource_path, get_version

VERSION = get_version()

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级设置")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Server settings
        layout.addWidget(QLabel("VPN 服务端地址"))
        self.server_input = QLineEdit("vpn.hitsz.edu.cn")
        layout.addWidget(self.server_input)

        # DNS settings
        layout.addWidget(QLabel("DNS 服务器地址"))
        self.dns_input = QLineEdit("10.248.98.30")
        layout.addWidget(self.dns_input)
        
        # Proxy Control
        self.proxy_switch = QCheckBox("自动配置代理")
        layout.addWidget(self.proxy_switch)

        # Startup Control
        self.startup_switch = QCheckBox("开机启动")
        self.startup_switch.setChecked(get_launch_at_login())
        layout.addWidget(self.startup_switch)

        # Silent mode
        self.silent_mode_switch = QCheckBox("静默启动")
        layout.addWidget(self.silent_mode_switch)

        # Connect on startup
        self.connect_startup_switch = QCheckBox("启动时自动连接")
        layout.addWidget(self.connect_startup_switch)

        # Check for update on startup
        self.check_update_switch = QCheckBox("启动时检查更新")
        layout.addWidget(self.check_update_switch)

        # Hide dock icon option (only for macOS)
        if system() == "Darwin":
            self.hide_dock_icon_switch = QCheckBox("隐藏 Dock 图标")
            layout.addWidget(self.hide_dock_icon_switch)

        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def get_settings(self):
        settings = {
            'server': self.server_input.text(),
            'dns': self.dns_input.text(),
            'proxy': self.proxy_switch.isChecked(),
            'connect_startup': self.connect_startup_switch.isChecked(),
            'silent_mode': self.silent_mode_switch.isChecked(),
            'check_update': self.check_update_switch.isChecked()
        }
        
        if system() == "Darwin":
            settings['hide_dock_icon'] = self.hide_dock_icon_switch.isChecked()
            
        return settings
    
    def set_settings(self, server, dns, proxy, connect_startup, silent_mode, check_update, hide_dock_icon=False):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.dns_input.setText(dns)
        self.proxy_switch.setChecked(proxy)
        self.connect_startup_switch.setChecked(connect_startup)
        self.silent_mode_switch.setChecked(silent_mode)
        self.check_update_switch.setChecked(check_update)
        if system() == "Darwin":
            self.hide_dock_icon_switch.setChecked(hide_dock_icon)

    def accept(self):
        """Save settings before closing"""
        current_config = load_config()
        settings = self.get_settings()

        settings['username'] = current_config.get('username', '')
        settings['password'] = current_config.get('password', '')
        settings['remember'] = current_config.get('remember', False)
        
        save_config(settings)
        set_launch_at_login(enable=self.startup_switch.isChecked())
        
        if system() == "Darwin":
            hide_dock_icon(self.hide_dock_icon_switch.isChecked())
            
            from .menu_utils import setup_menubar
            main_window = self.parent()
            main_window.hide_dock_icon = self.hide_dock_icon_switch.isChecked()
            setup_menubar(main_window, VERSION)

            main_window.show()
            main_window.raise_()
            
            icon_path = get_resource_path("assets/icon.icns")

            app_icon = QIcon(icon_path)
            app = QApplication.instance()
            app.setWindowIcon(app_icon)

        super().accept()
