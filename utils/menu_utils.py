from PySide6.QtWidgets import QMessageBox, QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QMainWindow, QProgressDialog
from PySide6.QtGui import QGuiApplication
import requests
from packaging import version
import webbrowser
from PySide6.QtCore import Qt, QThread, Signal
import os
import sys
import shutil
import tempfile
from platform import system
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

class UpdaterThread(QThread):
    progress = Signal(int)
    finished = Signal(bool, str)

    def __init__(self, url, parent=None):
        super().__init__(parent)
        self.url = url

    def run(self):
        try:
            # Download the file
            response = requests.get(self.url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, "update.zip")
            
            # Download with progress
            with open(temp_file, 'wb') as f:
                downloaded = 0
                for data in response.iter_content(chunk_size=4096):
                    downloaded += len(data)
                    f.write(data)
                    self.progress.emit(int(downloaded * 100 / total_size))
            
            # Extract and replace current executable
            self.replace_current_executable(temp_file)
            self.finished.emit(True, "更新成功！请重启应用。")
            
        except Exception as e:
            self.finished.emit(False, f"更新失败：{str(e)}")

    def replace_current_executable(self, update_file):
        if system() == "Windows":
            # Windows: Create update batch script
            batch_script = f"""
@echo off
timeout /t 2 /nobreak > nul
copy /Y "{update_file}" "{sys.executable}"
del "%~f0"
            """
            with open("update.bat", "w") as f:
                f.write(batch_script)
            os.system("start /b update.bat")
        elif system() == "Darwin" or system() == "Linux":
            shutil.copy2(update_file, sys.executable)

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
        latest = response.json()
        latest_version = latest["tag_name"].lstrip('v')

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

            def start_update():
                # Get correct asset URL based on platform and architecture
                assets = latest["assets"]
                arch = "arm64" if "arm" in os.uname().machine.lower() else "amd64"
                
                asset_name = None
                if system() == "Windows":
                    asset_name = f"hitsz-connect-verge-windows-{arch}.exe"
                elif system() == "Darwin":
                    asset_name = f"hitsz-connect-verge-darwin-{arch}.dmg"
                elif system() == "Linux":
                    asset_name = f"hitsz-connect-verge-linux-{arch}.zip"
                
                asset_url = next((asset["browser_download_url"] 
                                for asset in assets 
                                if asset["name"] == asset_name), None)
                
                if not asset_url:
                    QMessageBox.warning(parent, "更新失败", "未找到适配当前系统的更新包")
                    return

                progress = QProgressDialog("正在下载更新...", "取消", 0, 100, parent)
                progress.setWindowModality(Qt.WindowModal)
                
                updater = UpdaterThread(asset_url, parent)
                updater.progress.connect(progress.setValue)
                updater.finished.connect(lambda success, msg: handle_update_result(success, msg, progress))
                updater.start()

            def handle_update_result(success, message, progress):
                progress.close()
                if success:
                    QMessageBox.information(parent, "更新完成", message)
                    parent.quit_app()
                else:
                    QMessageBox.warning(parent, "更新失败", message)

            download_button = QPushButton("下载更新")
            download_button.clicked.connect(start_update)
            button_layout.addWidget(download_button)

            close_button = QPushButton("关闭")
            close_button.clicked.connect(dialog.close)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)
            dialog.setLayout(layout)
            dialog.finished.connect(dialog.deleteLater)
            dialog.exec()
        else:
            QMessageBox.information(parent, "检查更新", "当前已是最新版本！")

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
        window.silent_mode
    )
    
    if dialog.exec():
        settings = dialog.get_settings()
        window.server_address = settings['server']
        window.dns_server = settings['dns']
        window.proxy = settings['proxy']
        window.connect_startup = settings['connect_startup']
        window.silent_mode = settings['silent_mode']
