from PySide6.QtWidgets import QMessageBox, QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QMainWindow
from PySide6.QtGui import QGuiApplication
import requests
from packaging import version
import webbrowser
from PySide6.QtCore import Qt
from .advanced_panel import AdvancedSettingsDialog

def setup_menubar(window: QMainWindow, version):
    """Set up the main window menu bar"""
    menubar = window.menuBar()
    
    # Settings Menu
    settings_menu = menubar.addMenu("设置")
    window.advanced_action = settings_menu.addAction("高级设置")
    window.advanced_action.triggered.connect(lambda: show_advanced_settings(window))
    
    # Help Menu
    about_menu = menubar.addMenu("帮助")
    about_menu.addAction("复制日志").triggered.connect(lambda: copy_log(window))  # Changed text and function
    about_menu.addAction("检查更新").triggered.connect(lambda: check_for_updates(window, version))
    about_menu.addAction("关于").triggered.connect(lambda: show_about(window, version))

def show_about(window, version):
    """Show about dialog"""
    about_text = f'''<p style="font-size: 15pt;">HITSZ Connect Verge</p>
    <p style="font-size: 10pt;">Version: {version}</p>
    <p style="font-size: 10pt;">Repository: <a href="https://github.com/kowyo/hitsz-connect-verge">github.com/kowyo/hitsz-connect-verge</a></p>
    <p style="font-size: 10pt;">Author: <a href="https://github.com/kowyo">Kowyo</a></p> '''
    QMessageBox.about(window, "关于 HITSZ Connect Verge", about_text)


def copy_log(window):
    """Copy log text to clipboard directly"""
    QGuiApplication.clipboard().setText(window.output_text.toPlainText())
    QMessageBox.information(window, "复制日志", "日志已复制到剪贴板")

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
            dialog = QDialog(parent)
            dialog.setWindowTitle("检查更新")
            dialog.setMinimumWidth(300)

            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            message = f"""<div style='text-align: center;'>
            <h3 style='margin-bottom: 15px;'>发现新版本！</h3>
            <p>当前版本：{current_version}</p>
            <p>最新版本：{latest_version}</p>
            </div>"""
            message_label = QLabel(message)
            message_label.setTextFormat(Qt.RichText)
            layout.addWidget(message_label)

            button_layout = QHBoxLayout()
            button_layout.setSpacing(10)

            download_button = QPushButton("下载更新")
            download_button.clicked.connect(
                lambda: webbrowser.open("https://github.com/kowyo/hitsz-connect-verge/releases/latest")
            )
            button_layout.addWidget(download_button)

            close_button = QPushButton("关闭")
            close_button.clicked.connect(dialog.close)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            dialog.finished.connect(dialog.deleteLater)
            dialog.exec()
        else:
            if not startup:
                QMessageBox.information(parent, "检查更新", "当前已是最新版本！")
            else:
                parent.output_text.append("App is up to date.")

    except requests.RequestException:
        QMessageBox.warning(parent, "检查更新", "检查更新失败，请检查网络连接。")

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
