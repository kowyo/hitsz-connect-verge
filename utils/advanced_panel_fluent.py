from qfluentwidgets import (LineEdit, BodyLabel, CheckBox, SwitchButton,
                          PushButton, FluentIcon)
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from .config_utils import save_config, load_config
from .startup_utils import set_launch_at_login, get_launch_at_login

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('高级设置')
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Server settings
        layout.addWidget(BodyLabel('VPN 服务端地址'))
        self.server_input = LineEdit(self)
        self.server_input.setPlaceholderText('vpn.hitsz.edu.cn')
        layout.addWidget(self.server_input)

        # DNS settings
        layout.addWidget(BodyLabel('DNS 服务器地址'))
        self.dns_input = LineEdit(self)
        self.dns_input.setPlaceholderText('10.248.98.30')
        layout.addWidget(self.dns_input)
        
        # Proxy Control and Login option        
        proxy_layout = QHBoxLayout()
        proxy_layout.addWidget(BodyLabel('自动配置代理'))
        proxy_layout.addStretch()
        self.proxy_switch = SwitchButton(self)
        proxy_layout.addWidget(self.proxy_switch)
        layout.addLayout(proxy_layout)
        
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

        # Check for update on startup
        check_update_layout = QHBoxLayout()
        check_update_layout.addWidget(BodyLabel('启动时检查更新'))
        check_update_layout.addStretch()
        self.check_update_switch = SwitchButton(self)
        check_update_layout.addWidget(self.check_update_switch)
        layout.addLayout(check_update_layout)

        # Add stretch to push buttons to bottom
        layout.addStretch()
        
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
        
        self.setLayout(layout)

    def get_settings(self):
        return {
            'server': self.server_input.text(),
            'dns': self.dns_input.text(),
            'proxy': self.proxy_switch.isChecked(),
            'connect_startup': self.connect_startup_switch.isChecked(),
            'silent_mode': self.silent_mode_switch.isChecked(),
            'check_update': self.check_update_switch.isChecked()
        }
    
    def set_settings(self, server, dns, proxy, connect_startup, silent_mode, check_update):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.dns_input.setText(dns)
        self.proxy_switch.setChecked(proxy)
        self.connect_startup_switch.setChecked(connect_startup)
        self.silent_mode_switch.setChecked(silent_mode)
        self.check_update_switch.setChecked(check_update)

    def accept(self):
        """Save settings before closing"""
        current_config = load_config()
        settings = self.get_settings()

        settings['username'] = current_config.get('username', '')
        settings['password'] = current_config.get('password', '')
        settings['remember'] = current_config.get('remember', False)

        save_config(settings)
        set_launch_at_login(enable=self.startup_switch.isChecked())
        super().accept()
