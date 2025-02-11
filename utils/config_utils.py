import json
import os
from .startup_utils import get_launch_at_login

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

def save_config(config):
    """Save config to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception:
        pass

def load_config():
    """Load config from file"""
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
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                default_config.update(config)
        return default_config
    except Exception:
        return default_config

def load_settings(self):
    """Load advanced settings from config file"""
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
