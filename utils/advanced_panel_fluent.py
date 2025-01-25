from qfluentwidgets import (LineEdit, BodyLabel, CheckBox, SwitchButton,
                          PushButton, FluentIcon)
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from .config_utils import save_config
from .startup_utils import set_launch_at_login, get_launch_at_login

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('高级设置')
        self.setFixedWidth(400)
        self.setup_ui()
        
    def setup_ui(self):
        # Create main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(24, 24, 24, 24)
        
        # Server settings
        layout.addWidget(BodyLabel('SSL VPN 服务端地址'))
        self.server_input = LineEdit(self)
        self.server_input.setPlaceholderText('vpn.hitsz.edu.cn')
        layout.addWidget(self.server_input)

        # DNS settings
        layout.addWidget(BodyLabel('DNS 服务器地址'))
        self.dns_input = LineEdit(self)
        self.dns_input.setPlaceholderText('10.248.98.30')
        layout.addWidget(self.dns_input)
        
        # Proxy Control and Login option
        h_layout2 = QHBoxLayout()
        
        proxy_layout = QVBoxLayout()
        proxy_layout.addWidget(BodyLabel('自动配置代理'))
        self.proxy_switch = SwitchButton(self)
        proxy_layout.addWidget(self.proxy_switch)
        h_layout2.addLayout(proxy_layout)
        
        startup_layout2 = QVBoxLayout()
        startup_layout2.addWidget(BodyLabel('开机启动'))
        self.startup_switch = SwitchButton(self)
        self.startup_switch.setChecked(get_launch_at_login())
        startup_layout2.addWidget(self.startup_switch)
        h_layout2.addLayout(startup_layout2)
        
        layout.addLayout(h_layout2)

        # Connect on startup and Silent mode
        h_layout = QHBoxLayout()
        
        startup_layout = QVBoxLayout()
        startup_layout.addWidget(BodyLabel('启动时自动连接'))
        self.connect_startup_switch = SwitchButton(self)
        startup_layout.addWidget(self.connect_startup_switch)
        h_layout.addLayout(startup_layout)
        
        silent_layout = QVBoxLayout()
        silent_layout.addWidget(BodyLabel('静默启动')) 
        self.silent_mode_switch = SwitchButton(self)
        silent_layout.addWidget(self.silent_mode_switch)
        h_layout.addLayout(silent_layout)
        
        layout.addLayout(h_layout)
        
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
            'server': self.server_input.text() or self.server_input.placeholderText(),
            'dns': self.dns_input.text() or self.dns_input.placeholderText(),
            'proxy': self.proxy_switch.isChecked(),
            'connect_startup': self.connect_startup_switch.isChecked(),
            'silent_mode': self.silent_mode_switch.isChecked()
        }

    def set_settings(self, server, dns, proxy, connect_startup, silent_mode):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.dns_input.setText(dns)
        self.proxy_switch.setChecked(proxy)
        self.connect_startup_switch.setChecked(connect_startup)
        self.silent_mode_switch.setChecked(silent_mode)

    def accept(self):
        """Save settings before closing"""
        settings = self.get_settings()
        save_config(settings)
        set_launch_at_login(self.startup_switch.isChecked())
        super().accept()
