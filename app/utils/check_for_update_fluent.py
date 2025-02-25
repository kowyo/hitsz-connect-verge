import webbrowser
from packaging import version
import requests
from qfluentwidgets import MessageBox

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
            dialog = MessageBox(title, message, parent=parent)
            if dialog.exec():
                webbrowser.open("https://github.com/kowyo/hitsz-connect-verge/releases/latest/")
            else:
                return
        else:
            if not startup:
                MessageBox("检查更新", "当前已是最新版本。", parent=parent).exec()
            else:
                parent.output_text.append("App is up to date.\n")
            
    except requests.RequestException:
        if not startup:
            MessageBox("检查更新", "检查更新失败，请检查网络连接。", parent=parent).exec()
        else:
            parent.output_text.append("Failed to check for updates. Please check your network connection.\n")