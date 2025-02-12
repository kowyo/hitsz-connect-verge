from PySide6.QtCore import QSettings
from .startup_utils import get_launch_at_login

def save_config(config):
    """Save config using QSettings"""
    settings = QSettings("Kowyo", "HITSZ Connect Verge")
    for key, value in config.items():
        settings.setValue(key, value)
    settings.sync()

def load_config():
    """Load config from QSettings"""
    settings = QSettings("Kowyo", "HITSZ Connect Verge")
    default_config = {
        'username': '',
        'password': '',
        'remember': False,
        'server': 'vpn.hitsz.edu.cn',
        'dns': '10.248.98.30',
        'proxy': True,
        'launch_at_login': get_launch_at_login(),
        'connect_startup': False,
        'silent_mode': False,
        'check_update': True,
        'hide_dock_icon': False
    }
    
    # Load values from QSettings, falling back to defaults if not found
    for key in default_config.keys():
        value = settings.value(key, default_config[key])
        if isinstance(default_config[key], bool):
            value = str(value).lower() == 'true'
        default_config[key] = value
    
    return default_config

def load_settings(self):
    """Load advanced settings from QSettings"""
    config = load_config()
    self.username = config['username']
    self.password = config['password']
    self.remember = config['remember']
    self.server_address = config['server']
    self.dns_server = config['dns']
    self.proxy = config['proxy']
    self.connect_startup = config['connect_startup']
    self.silent_mode = config['silent_mode']
    self.check_update = config['check_update']
    self.hide_dock_icon = config['hide_dock_icon']
