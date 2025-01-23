import json
import os

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
        'proxy': True
    }
    
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    
    return default_config