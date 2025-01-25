import os
import sys
from platform import system
import shlex
import gc
import shutil
from .set_proxy import CommandWorker
from qfluentwidgets import FluentIcon

def handle_output(window, text):
    """Handle output text from the worker"""
    window.output_text.append(text)

def handle_connection_finished(window):
    """Handle connection finished event with proper cleanup"""
    if window.worker:
        window.worker.output.disconnect()
        window.worker.finished.disconnect()
        window.worker.deleteLater()
        window.worker = None
        gc.collect()

    window.status_label.setText("状态: 未连接")
    if hasattr(window, 'status_icon'):
        window.status_icon.setIcon(FluentIcon.CANCEL_MEDIUM)
    if hasattr(window, 'connect_button'):
        window.connect_button.setChecked(False)

def start_connection(window):
    """Start VPN connection"""
    if window.worker and window.worker.isRunning():
        window.status_label.setText("状态: 正在运行")
        if hasattr(window, 'status_icon'):
            window.status_icon.setIcon(FluentIcon.ACCEPT_MEDIUM)
        return

    username = window.username_input.text()
    password = window.password_input.text()
    server_address = window.server_address
    dns_server_address = window.dns_server

    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    if system() == "Windows":
        stable_path = os.path.join(os.path.expanduser("~"), "hitsz-connect-verge", "zju-connect.exe")
        if not os.path.exists(stable_path):
            os.makedirs(os.path.dirname(stable_path), exist_ok=True)
            shutil.copy(os.path.join(base_path, "core", "zju-connect.exe"), stable_path)
        command = stable_path
    else:
        command = os.path.join(base_path, "core", "zju-connect")
        if os.path.exists(command):
            os.chmod(command, 0o755)

    command_args = [
        command, "-server", shlex.quote(server_address),
        "-zju-dns-server", shlex.quote(dns_server_address),
        "-username", shlex.quote(username), "-password", shlex.quote(password)
    ]
    
    window.worker = CommandWorker(command_args=command_args, proxy_enabled=window.proxy)
    window.worker.output.connect(lambda text: handle_output(window, text))
    window.worker.finished.connect(lambda: handle_connection_finished(window))
    window.worker.start()

    window.status_label.setText("状态: 正在运行")
    if hasattr(window, 'status_icon'):
        window.status_icon.setIcon(FluentIcon.ACCEPT_MEDIUM)

def stop_connection(window):
    """Stop VPN connection with proper cleanup"""
    if window.worker:
        window.worker.stop()
        window.worker.wait()
        window.worker.output.disconnect()
        window.worker.finished.disconnect()
        window.worker.deleteLater()
        window.worker = None
        gc.collect()

    window.status_label.setText("状态: 未连接")
    if hasattr(window, 'status_icon'):
        window.status_icon.setIcon(FluentIcon.CANCEL_MEDIUM)
