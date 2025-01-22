import requests
from packaging import version
import webbrowser
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PySide6.QtWidgets import QMessageBox, QDialog, QVBoxLayout, QHBoxLayout
from PySide6.QtCore import Qt
from qfluentwidgets import (PushButton, TextEdit, BodyLabel, CommandBar, Action,
                          FluentIcon, TransparentDropDownPushButton, RoundMenu, MessageBox, Dialog)

def setup_menubar(window, version):
    """Set up the command bar instead of traditional menu bar"""
    command_bar = CommandBar(window)
    
    # Settings button with dropdown
    settings_button = TransparentDropDownPushButton('设置', window, FluentIcon.SETTING)
    settings_button.setFixedHeight(34)
    settings_menu = RoundMenu(parent=window)
    window.advanced_action = Action(FluentIcon.DEVELOPER_TOOLS, '高级设置')
    settings_menu.addAction(window.advanced_action)
    settings_button.setMenu(settings_menu)
    command_bar.addWidget(settings_button)
    
    # Help button with dropdown
    help_button = TransparentDropDownPushButton('帮助', window, FluentIcon.HELP)
    help_button.setFixedHeight(34)
    help_menu = RoundMenu(parent=window)
    help_menu.addActions([
        Action(FluentIcon.DICTIONARY, '查看日志', triggered=lambda: show_log(window)),
        Action(FluentIcon.UPDATE, '检查更新', triggered=lambda: check_for_updates(window, version)),
        Action(FluentIcon.INFO, '关于', triggered=lambda: show_about(window, version))
    ])
    help_button.setMenu(help_menu)
    command_bar.addWidget(help_button)
    
    return command_bar

def show_about(window, version):
    """Show about dialog"""
    about_text = f'''<p>Version: {version}</p>
    <p>Repository: <a href="https://github.com/kowyo/hitsz-connect-verge">github.com/kowyo/hitsz-connect-verge</a></p>
    <p>Author: <a href="https://github.com/kowyo">Kowyo</a></p> '''
    Dialog("关于 HITSZ Connect Verge", about_text, parent=window).exec()

def show_log(window):
    """Show the log window"""
    dialog = QDialog(window)
    dialog.setWindowTitle("查看日志")
    dialog.setMinimumSize(300, 400)
    
    layout = QVBoxLayout()
    
    # Use TextEdit from qfluentwidgets
    log_text = TextEdit()
    log_text.setReadOnly(True)
    log_text.setText(window.output_text.toPlainText())
    layout.addWidget(log_text)
    
    # Use PushButton from qfluentwidgets
    copy_button = PushButton("复制")
    copy_button.clicked.connect(
        lambda: window.QApplication.clipboard().setText(log_text.toPlainText())
    )
    
    close_button = PushButton("关闭")
    close_button.clicked.connect(dialog.close)

    button_layout = QHBoxLayout()
    button_layout.addWidget(copy_button)
    
    button_layout.addWidget(close_button)
    layout.addLayout(button_layout)
    
    dialog.setLayout(layout)
    dialog.show()

def check_for_updates(parent, current_version):
    """
    Check for updates and show appropriate dialog.
    
    Args:
        parent: Parent widget for dialogs
        current_version: Current version string
    """
    try:
        response = requests.get(
            "https://api.github.com/repos/kowyo/hitsz-connect-verge/releases/latest",
            timeout=5
        )
        response.raise_for_status()
        latest_version = response.json()["tag_name"].lstrip('v')
        
        if version.parse(latest_version) > version.parse(current_version):
            title = "检查更新"
            message = f"发现新版本 {latest_version}，是否前往下载？"
            dialog = MessageBox(title, message, parent=parent)
            if dialog.exec():
                webbrowser.open("https://github.com/kowyo/hitsz-connect-verge/releases/latest/")
            else:
                return
        else:
            MessageBox("检查更新", "当前已是最新版本。", parent=parent).exec()
            return
            
    except requests.RequestException:
        MessageBox("检查更新", "检查更新失败，请检查网络连接。", parent=parent).exec()
