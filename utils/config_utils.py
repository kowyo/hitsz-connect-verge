import json
import os
from .startup_utils import get_launch_at_login

CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".hitsz-connect-verge.json")

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
        'server': 'vpn.hitsz.edu.cn',
        'dns': '10.248.98.30',
        'proxy': True,
        'launch_at_login': get_launch_at_login(),
        'connect_startup': False,
        'silent_mode': False,
        'check_update': True
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                for key in default_config:
                    if key not in config:
                        config[key] = default_config[key]
    except Exception:
        return default_config

def load_settings(self):
    """Load advanced settings from config file"""
    config = load_config()
    self.server_address = config['server']
    self.dns_server = config['dns']
    self.proxy = config['proxy']
    self.connect_startup = config['connect_startup']
    self.silent_mode = config['silent_mode']
    self.check_update = config['check_update']
