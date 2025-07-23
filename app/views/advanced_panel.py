from PySide6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, 
                              QPushButton, QHBoxLayout, QApplication, QTabWidget, QWidget,
                              QFileDialog, QStyle)
from PySide6.QtGui import QIcon, QAction
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
        network_layout.setSpacing(10)
        
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
        self.auto_dns_switch = QCheckBox("自动配置 DNS")
        self.auto_dns_switch.setChecked(True)
        self.auto_dns_switch.toggled.connect(self.toggle_dns_input)
        dns_layout.addWidget(self.auto_dns_switch)
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
        self.proxy_switch.setToolTip("自动配置系统代理设置，将网络流量通过 VPN 转发")
        network_layout.addWidget(self.proxy_switch)

        # Disable keep-alive
        self.keep_alive_switch = QCheckBox("定时保活")
        self.keep_alive_switch.setToolTip("开启后，ZJU Connect 会定时发送心跳包以保持连接")
        network_layout.addWidget(self.keep_alive_switch)

        # Debug-dump
        self.debug_dump_switch = QCheckBox("调试模式")
        self.debug_dump_switch.setToolTip("开启后，ZJU Connect 会记录详细的调试信息到日志文件")
        network_layout.addWidget(self.debug_dump_switch)

        # Disable multi line
        self.disable_multi_line_switch = QCheckBox("禁用备用线路检测")
        self.disable_multi_line_switch.setToolTip("开启后，ZJU Connect 将不再自动切换到备用线路")
        network_layout.addWidget(self.disable_multi_line_switch)

                # Certificate file selection
        # Certificate file selection
        cert_label = QLabel("证书路径")
        cert_label.setToolTip("如果服务器要求证书验证，需要配置此参数")
        cert_layout.addWidget(cert_label)
        self.cert_file_input = QLineEdit()
        self.cert_file_input.setPlaceholderText("选择 .p12 证书文件")
        self.cert_file_input.setReadOnly(True)
        
        # Add clear action to the text field
        self.cert_clear_action = QAction()
        self.cert_clear_action.setIcon(self.style().standardIcon(QStyle.SP_DialogCancelButton))
        self.cert_clear_action.setToolTip("清除证书")
        self.cert_clear_action.triggered.connect(self.clear_cert_file)
        self.cert_file_input.addAction(self.cert_clear_action, QLineEdit.TrailingPosition)
        
        cert_layout.addWidget(self.cert_file_input)
        self.cert_browse_button = QPushButton("浏览...")
        self.cert_browse_button.clicked.connect(self.browse_cert_file)
        cert_layout.addWidget(self.cert_browse_button)
        network_layout.addLayout(cert_layout)

        # Certificate password
        cert_pwd_layout = QHBoxLayout()
        cert_pwd_layout.addWidget(QLabel("证书密码"))
        self.cert_password_input = QLineEdit()
        self.cert_password_input.setPlaceholderText("输入证书密码")
        self.cert_password_input.setEchoMode(QLineEdit.Password)
        cert_pwd_layout.addWidget(self.cert_password_input)
        network_layout.addLayout(cert_pwd_layout)

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

    def toggle_dns_input(self):
        """Toggle DNS input field based on auto DNS checkbox"""
        self.dns_input.setEnabled(not self.auto_dns_switch.isChecked())
    
    def browse_cert_file(self):
        """Open file dialog to browse for certificate file"""
        file_dialog = QFileDialog(self)
        file_dialog.setNameFilter("Certificate files (*.p12)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.cert_file_input.setText(selected_files[0])
    
    def clear_cert_file(self):
        """Clear the selected certificate file"""
        self.cert_file_input.clear()
        self.cert_password_input.clear()
        
    def get_settings(self):
        settings = {
            'server': self.server_input.text(),
            'port': self.port_input.text(),
            'dns': self.dns_input.text(),
            'auto_dns': self.auto_dns_switch.isChecked(),
            'proxy': self.proxy_switch.isChecked(),
            'connect_startup': self.connect_startup_switch.isChecked(),
            'silent_mode': self.silent_mode_switch.isChecked(),
            'check_update': self.check_update_switch.isChecked(),
            'keep_alive': self.keep_alive_switch.isChecked(),
            'debug_dump': self.debug_dump_switch.isChecked(),
            'disable_multi_line': self.disable_multi_line_switch.isChecked(),
            'http_bind': self.http_bind_input.text(),
            'socks_bind': self.socks_bind_input.text(),
            'cert_file': self.cert_file_input.text(),
            'cert_password': self.cert_password_input.text(),
        }
        
        if system() == "Darwin":
            settings['hide_dock_icon'] = self.hide_dock_icon_switch.isChecked()
            
        return settings
    
    def set_settings(self, server, port, dns, proxy, connect_startup, silent_mode, check_update, hide_dock_icon=False, keep_alive=False, debug_dump=False, disable_multi_line=False, http_bind='', socks_bind='', auto_dns=True, cert_file='', cert_password=''):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.port_input.setText(port)
        self.dns_input.setText(dns)
        self.auto_dns_switch.setChecked(auto_dns)
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
        self.cert_file_input.setText(cert_file)
        self.cert_password_input.setText(cert_password)
        
        # Enable/disable DNS input based on auto DNS setting
        self.toggle_dns_input()

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
