from qfluentwidgets import (LineEdit, SwitchButton, SubtitleLabel, BodyLabel,
                          PushButton, FluentIcon)
from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from .config_utils import save_config

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
        
        # Proxy Control
        layout.addWidget(BodyLabel('自动配置代理'))
        self.proxy_switch = SwitchButton(self)
        layout.addWidget(self.proxy_switch)
        
        # Add stretch to push buttons to bottom
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        save_button = PushButton('保存', self)
        save_button.setIcon(FluentIcon.SAVE)
        save_button.clicked.connect(self.accept)
        
        cancel_button = PushButton('取消', self)
        cancel_button.setIcon(FluentIcon.CANCEL)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

    def get_settings(self):
        return {
            'server': self.server_input.text() or self.server_input.placeholderText(),
            'dns': self.dns_input.text() or self.dns_input.placeholderText(),
            'proxy': self.proxy_switch.isChecked()
        }

    def set_settings(self, server, dns, proxy):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.dns_input.setText(dns)
        self.proxy_switch.setChecked(proxy)

    def accept(self):
        """Save settings before closing"""
        settings = self.get_settings()
        save_config(settings)
        super().accept()
