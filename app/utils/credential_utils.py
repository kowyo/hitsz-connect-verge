from .config_utils import load_config, save_config

def save_credentials(window):
    config = load_config()
    
    if window.remember_cb.isChecked():
        config['username'] = window.username_input.text()
        config['password'] = window.password_input.text()
        config['remember'] = True
    else:
        config['username'] = ''
        config['password'] = ''
        config['remember'] = False
    
    save_config(config)
