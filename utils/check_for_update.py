import requests
from packaging import version
import webbrowser
from PySide6.QtWidgets import QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PySide6.QtCore import Qt

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
            dialog.exec()
        else:
            QMessageBox.information(parent, "检查更新", "当前已是最新版本！")
            
    except requests.RequestException:
        QMessageBox.warning(parent, "检查更新", "检查更新失败，请检查网络连接。")
