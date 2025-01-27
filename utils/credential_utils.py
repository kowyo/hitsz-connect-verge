from .config_utils import load_config, save_config

def load_credentials(window):
    """Load stored credentials from config."""
    config = load_config()
    if config['remember']:
        window.username_input.setText(config['username'])
        window.password_input.setText(config['password'])
        window.remember_cb.setChecked(True)

def save_credentials(window):
    """Save credentials to config if 'Remember Password' is checked."""
    config = load_config()
    config['username'] = window.username_input.text() if window.remember_cb.isChecked() else ''
    config['password'] = window.password_input.text() if window.remember_cb.isChecked() else ''
    config['remember'] = window.remember_cb.isChecked()
    save_config(config)
