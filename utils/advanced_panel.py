from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QHBoxLayout
from .config_utils import save_config

class AdvancedSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("高级设置")
        self.setMinimumWidth(300)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Server settings
        layout.addWidget(QLabel("SSL VPN 服务端地址："))
        self.server_input = QLineEdit("vpn.hitsz.edu.cn")
        layout.addWidget(self.server_input)

        # DNS settings
        layout.addWidget(QLabel("DNS 服务器地址："))
        self.dns_input = QLineEdit("10.248.98.30")
        layout.addWidget(self.dns_input)
        
        # Proxy Control
        self.proxy_cb = QCheckBox("自动配置代理")
        self.proxy_cb.setChecked(True)
        layout.addWidget(self.proxy_cb)

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
        return {
            'server': self.server_input.text(),
            'dns': self.dns_input.text(),
            'proxy': self.proxy_cb.isChecked()
        }

    def set_settings(self, server, dns, proxy):
        """Set dialog values from main window values"""
        self.server_input.setText(server)
        self.dns_input.setText(dns)
        self.proxy_cb.setChecked(proxy)

    def accept(self):
        """Save settings before closing"""
        settings = self.get_settings()
        save_config(settings)
        super().accept()
