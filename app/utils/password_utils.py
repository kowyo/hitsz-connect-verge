from PySide6.QtWidgets import QLineEdit

def toggle_password_visibility(password_input, is_checked):
    """Toggle password visibility in a password input field"""
    password_input.setEchoMode(QLineEdit.Normal if is_checked else QLineEdit.Password)
