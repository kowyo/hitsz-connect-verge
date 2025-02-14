from qfluentwidgets import (LineEdit, BodyLabel, SwitchButton, PushButton, 
                          FluentIcon, Pivot)
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QWidget,
                              QStackedWidget)
from PySide6.QtCore import Qt
from .config_utils import save_config, load_config
from .startup_utils import set_launch_at_login, get_launch_at_login

class NetworkSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Server & Port
        server_layout = QHBoxLayout()
        server_layout.addWidget(BodyLabel('VPN 服务端地址'))
        self.server_input = LineEdit(self)
        self.server_input.setPlaceholderText('vpn.hitsz.edu.cn')
        server_layout.addWidget(self.server_input)
        server_layout.addWidget(BodyLabel('端口'))
        self.port_input = LineEdit(self)
        self.port_input.setFixedWidth(80)
        self.port_input.setPlaceholderText('443')
        server_layout.addWidget(self.port_input)
        layout.addLayout(server_layout)
        
        # DNS settings
        dns_layout = QHBoxLayout()
        dns_layout.addWidget(BodyLabel('DNS 服务器地址'))
        self.dns_input = LineEdit(self)
        self.dns_input.setPlaceholderText('10.248.98.30')
        dns_layout.addWidget(self.dns_input)
        layout.addLayout(dns_layout)

        # SOCKS bind
        socks_bind_layout = QHBoxLayout()
        socks_bind_layout.addWidget(BodyLabel('SOCKS5 代理监听地址'))
        self.socks_bind_input = LineEdit(self)
        self.socks_bind_input.setFixedWidth(80)
        self.socks_bind_input.setPlaceholderText('1080')
        socks_bind_layout.addStretch()
        socks_bind_layout.addWidget(self.socks_bind_input)
        layout.addLayout(socks_bind_layout)

        # HTTP bind
        http_bind_layout = QHBoxLayout()
        http_bind_layout.addWidget(BodyLabel('HTTP 代理监听地址'))
        self.http_bind_input = LineEdit(self)
        self.http_bind_input.setFixedWidth(80)
        self.http_bind_input.setPlaceholderText('1081')
        http_bind_layout.addStretch()
        http_bind_layout.addWidget(self.http_bind_input)
        layout.addLayout(http_bind_layout)
        
        # Proxy Control
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(BodyLabel('自动配置代理'))
        proxy_layout.addStretch()
        self.proxy_switch = SwitchButton(self)
        proxy_layout.addWidget(self.proxy_switch)
        layout.addLayout(proxy_layout)
        
        # Disable keep-alive
        keep_alive_layout = QHBoxLayout()
        keep_alive_layout.addWidget(BodyLabel('定时保活'))
        keep_alive_layout.addStretch()
        self.keep_alive_switch = SwitchButton(self)
        keep_alive_layout.addWidget(self.keep_alive_switch)
        layout.addLayout(keep_alive_layout)
        
        # Debug dump
        debug_dump_layout = QHBoxLayout()
        debug_dump_layout.addWidget(BodyLabel('调试模式'))
        debug_dump_layout.addStretch()
        self.debug_dump_switch = SwitchButton(self)
        debug_dump_layout.addWidget(self.debug_dump_switch)
        layout.addLayout(debug_dump_layout)

        layout.addStretch()

class GeneralSettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Startup Control
        launch_layout = QHBoxLayout()
        launch_layout.addWidget(BodyLabel('开机启动'))
        launch_layout.addStretch()
        self.startup_switch = SwitchButton(self)
        self.startup_switch.setChecked(get_launch_at_login())
        launch_layout.addWidget(self.startup_switch)
        layout.addLayout(launch_layout)
        
        # Silent mode
        silent_layout = QHBoxLayout()
        silent_layout.addWidget(BodyLabel('静默启动'))
        silent_layout.addStretch() 
        self.silent_mode_switch = SwitchButton(self)
        silent_layout.addWidget(self.silent_mode_switch)
        layout.addLayout(silent_layout)

        # Connect on startup
        startup_layout = QHBoxLayout()
        startup_layout.addWidget(BodyLabel('启动时自动连接'))
        startup_layout.addStretch()
        self.connect_startup_switch = SwitchButton(self)
        startup_layout.addWidget(self.connect_startup_switch)
        layout.addLayout(startup_layout)

        # Check for update
        check_update_layout = QHBoxLayout()
        check_update_layout.addWidget(BodyLabel('启动时检查更新'))
        check_update_layout.addStretch()
        self.check_update_switch = SwitchButton(self)
        check_update_layout.addWidget(self.check_update_switch)
        layout.addLayout(check_update_layout)
        
        layout.addStretch()

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('高级设置')
        self.setMinimumWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Create pivot and stacked widget
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        
        # Create sub interfaces
        self.network_settings = NetworkSettingsWidget(self)
        self.general_settings = GeneralSettingsWidget(self)
        
        # Add sub interfaces
        self.addSubInterface(self.network_settings, 'networkSettings', '网络')
        self.addSubInterface(self.general_settings, 'generalSettings', '通用')
        
        # Initialize current tab
        self.stackedWidget.setCurrentWidget(self.network_settings)
        self.pivot.setCurrentItem(self.network_settings.objectName())
        
        layout.addWidget(self.pivot, 0, Qt.AlignHCenter)
        layout.addWidget(self.stackedWidget)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_button = PushButton('保存', self)
        save_button.setIcon(FluentIcon.SAVE)
        save_button.clicked.connect(self.accept)
        
        cancel_button = PushButton('取消', self)
        cancel_button.setIcon(FluentIcon.CLOSE)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def addSubInterface(self, widget: QWidget, objectName: str, text: str):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def get_settings(self):
        return {
            'server': self.network_settings.server_input.text(),
            'port': self.network_settings.port_input.text(),
            'dns': self.network_settings.dns_input.text(),
            'proxy': self.network_settings.proxy_switch.isChecked(),
            'connect_startup': self.general_settings.connect_startup_switch.isChecked(),
            'silent_mode': self.general_settings.silent_mode_switch.isChecked(),
            'check_update': self.general_settings.check_update_switch.isChecked(),
            'keep_alive': self.network_settings.keep_alive_switch.isChecked(),
            'debug_dump': self.network_settings.debug_dump_switch.isChecked(),
            'http_bind': self.network_settings.http_bind_input.text(),
            'socks_bind': self.network_settings.socks_bind_input.text(),
        }
    
    def set_settings(self, server, port, dns, proxy, connect_startup, silent_mode, check_update, keep_alive=False, debug_dump=False, http_bind='', socks_bind=''):
        """Set dialog values from main window values"""
        self.network_settings.server_input.setText(server)
        self.network_settings.port_input.setText(port)
        self.network_settings.dns_input.setText(dns)
        self.network_settings.proxy_switch.setChecked(proxy)
        self.general_settings.connect_startup_switch.setChecked(connect_startup)
        self.general_settings.silent_mode_switch.setChecked(silent_mode)
        self.general_settings.check_update_switch.setChecked(check_update)
        self.network_settings.keep_alive_switch.setChecked(keep_alive)
        self.network_settings.debug_dump_switch.setChecked(debug_dump)
        self.network_settings.http_bind_input.setText(http_bind)
        self.network_settings.socks_bind_input.setText(socks_bind)

    def accept(self):
        """Save settings before closing"""
        current_config = load_config()
        settings = self.get_settings()

        settings['username'] = current_config.get('username', '')
        settings['password'] = current_config.get('password', '')
        settings['remember'] = current_config.get('remember', False)

        save_config(settings)
        set_launch_at_login(enable=self.general_settings.startup_switch.isChecked())
        super().accept()
