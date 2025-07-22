from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, 
                              QPushButton, QHBoxLayout, QApplication, QTabWidget, QWidget)
from PySide6.QtGui import QIcon
from utils.config_utils import save_config, load_config
from utils.startup_utils import set_launch_at_login, get_launch_at_login
from platform import system
if system() == "Darwin":
    from utils.macos_utils import hide_dock_icon
from common.version import get_version
from common import resources

VERSION = get_version()

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级设置")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        tab_widget = QTabWidget()
        
        # Network tab
        network_tab = QWidget()
        network_layout = QVBoxLayout()
        
        # Server & Port
        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel("VPN 服务端地址"))
        self.server_input = QLineEdit("vpn.hitsz.edu.cn")
        server_layout.addWidget(self.server_input)
        server_layout.addWidget(QLabel("端口"))
        self.port_input = QLineEdit("443")
        self.port_input.setMaximumWidth(60)
        server_layout.addWidget(self.port_input)
        network_layout.addLayout(server_layout)

        # DNS settings
        dns_layout = QHBoxLayout()
        dns_layout.addWidget(QLabel("DNS 服务器地址"))
        self.dns_input = QLineEdit("10.248.98.30")
        dns_layout.addWidget(self.dns_input)
        network_layout.addLayout(dns_layout)
        
        # SOCKS bind
        socks_bind_layout = QHBoxLayout()
        socks_bind_layout.addWidget(QLabel("SOCKS5 代理监听地址"))
        self.socks_bind_input = QLineEdit()
        self.socks_bind_input.setPlaceholderText("1080")
        socks_bind_layout.addStretch()
        socks_bind_layout.addWidget(self.socks_bind_input)
        network_layout.addLayout(socks_bind_layout)

        # HTTP bind
        http_bind_layout = QHBoxLayout()
        http_bind_layout.addWidget(QLabel("HTTP 代理监听地址 "))
        self.http_bind_input = QLineEdit()
        self.http_bind_input.setPlaceholderText("1081")
        http_bind_layout.addStretch()
        http_bind_layout.addWidget(self.http_bind_input)
        network_layout.addLayout(http_bind_layout)

        # Proxy Control
        self.proxy_switch = QCheckBox("自动配置代理")
        network_layout.addWidget(self.proxy_switch)

        # Disable keep-alive
        self.keep_alive_switch = QCheckBox("定时保活")
        network_layout.addWidget(self.keep_alive_switch)

        # Debug-dump
        self.debug_dump_switch = QCheckBox("调试模式")
        network_layout.addWidget(self.debug_dump_switch)

        # Disable multi line
        self.disable_multi_line_switch = QCheckBox("禁用备用线路检测")
        network_layout.addWidget(self.disable_multi_line_switch)

        network_tab.setLayout(network_layout)
        
        # General tab
        general_tab = QWidget()
        general_layout = QVBoxLayout()

        # Startup Control
        self.startup_switch = QCheckBox("开机启动")
        self.startup_switch.setChecked(get_launch_at_login())
        general_layout.addWidget(self.startup_switch)

        # Silent mode
        self.silent_mode_switch = QCheckBox("静默启动")
        general_layout.addWidget(self.silent_mode_switch)

        # Connect on startup
        self.connect_startup_switch = QCheckBox("启动时自动连接")
        general_layout.addWidget(self.connect_startup_switch)

        # Check for update on startup
        self.check_update_switch = QCheckBox("启动时检查更新")
        general_layout.addWidget(self.check_update_switch)

        # Hide dock icon option (only for macOS)
        if system() == "Darwin":
            self.hide_dock_icon_switch = QCheckBox("隐藏 Dock 图标")
            general_layout.addWidget(self.hide_dock_icon_switch)

        general_tab.setLayout(general_layout)

        # Add tabs to widget
        tab_widget.addTab(network_tab, "网络")
        tab_widget.addTab(general_tab, "通用")
        layout.addWidget(tab_widget)

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
            'port': self.port_input.text(),
            'dns': self.dns_input.text(),
            'proxy': self.proxy_switch.isChecked(),
            'connect_startup': self.connect_startup_switch.isChecked(),
            'silent_mode': self.silent_mode_switch.isChecked(),
            'check_update': self.check_update_switch.isChecked(),
            'keep_alive': self.keep_alive_switch.isChecked(),
            'debug_dump': self.debug_dump_switch.isChecked(),
            'disable_multi_line': self.disable_multi_line_switch.isChecked(),
            'http_bind': self.http_bind_input.text(),
            'socks_bind': self.socks_bind_input.text(),
        }
        
        if system() == "Darwin":
            settings['hide_dock_icon'] = self.hide_dock_icon_switch.isChecked()
            
        return settings
    
    def set_settings(self, server, port, dns, proxy, connect_startup, silent_mode, check_update, hide_dock_icon=False, keep_alive=False, debug_dump=False, disable_multi_line=False, http_bind='', socks_bind=''):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.port_input.setText(port)
        self.dns_input.setText(dns)
        self.proxy_switch.setChecked(proxy)
        self.connect_startup_switch.setChecked(connect_startup)
        self.silent_mode_switch.setChecked(silent_mode)
        self.check_update_switch.setChecked(check_update)
        if system() == "Darwin":
            self.hide_dock_icon_switch.setChecked(hide_dock_icon)
        self.keep_alive_switch.setChecked(keep_alive)
        self.debug_dump_switch.setChecked(debug_dump)
        self.disable_multi_line_switch.setChecked(disable_multi_line)
        self.http_bind_input.setText(http_bind)
        self.socks_bind_input.setText(socks_bind)

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
            
            icon_path = ':/icons/icon.icns'

            app_icon = QIcon(icon_path)
            app = QApplication.instance()
            app.setWindowIcon(app_icon)

        super().accept()
