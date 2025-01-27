import requests
from packaging import version
import webbrowser
from qfluentwidgets import (CommandBar, Action,
                          FluentIcon, TransparentPushButton, TransparentDropDownPushButton, RoundMenu, MessageBox, Dialog)
from PySide6.QtGui import QGuiApplication
from .advanced_panel_fluent import AdvancedSettingsDialog  # Update this import

def setup_menubar(window, version):
    """Set up the command bar instead of traditional menu bar"""
    command_bar = CommandBar(window)
    
    # Settings button
    settings_button = TransparentPushButton('设置', window, FluentIcon.SETTING)
    settings_button.setFixedHeight(34)
    settings_button.clicked.connect(lambda: show_advanced_settings(window))
    command_bar.addWidget(settings_button)
    
    # Help button with dropdown
    help_button = TransparentDropDownPushButton('帮助', window, FluentIcon.HELP)
    help_button.setFixedHeight(34)
    help_menu = RoundMenu(parent=window)
    help_menu.addActions([
        Action(FluentIcon.COPY, '复制日志', triggered=lambda: copy_log(window)),
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

def copy_log(window):
    """Copy log text to clipboard directly"""
    QGuiApplication.clipboard().setText(window.output_text.toPlainText())
    MessageBox("复制日志", "日志已复制到剪贴板", parent=window).exec()

def check_for_updates(parent, current_version, startup=False):
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
            if parent:
                dialog = MessageBox(title, message, parent=parent)
            else:
                dialog = MessageBox(title, message, parent=parent)
            if dialog.exec():
                webbrowser.open("https://github.com/kowyo/hitsz-connect-verge/releases/latest/")
            else:
                return
        else:
            if not startup:
                MessageBox("检查更新", "当前已是最新版本。", parent=parent).exec()
            else:
                parent.output_text.append("App is up to date.")
            
    except requests.RequestException:
        MessageBox("检查更新", "检查更新失败，请检查网络连接。", parent=parent).exec()

def show_advanced_settings(window):
    """Show advanced settings dialog with proper cleanup"""
    dialog = AdvancedSettingsDialog(window)
    dialog.set_settings(
        window.server_address,
        window.dns_server,
        window.proxy,
        window.connect_startup,
        window.silent_mode,
        window.check_update
    )
    
    if dialog.exec():
        settings = dialog.get_settings()
        window.server_address = settings['server']
        window.dns_server = settings['dns']
        window.proxy = settings['proxy']
        window.connect_startup = settings['connect_startup']
        window.silent_mode = settings['silent_mode']
        window.check_update = settings['check_update']
