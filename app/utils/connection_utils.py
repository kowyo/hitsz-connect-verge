import os
import sys
from platform import system
import shlex
import gc
from .set_proxy import CommandWorker

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
    if hasattr(window, 'connect_button'):
        window.connect_button.setChecked(False)

def start_connection(window):
    """Start VPN connection"""
    if window.worker and window.worker.isRunning():
        window.status_label.setText("状态: 正在运行")
        return

    username = window.username_input.text()
    password = window.password_input.text()
    server_address = window.server_address
    port = window.port
    dns_server_address = window.dns_server

    is_nuitka = '__compiled__' in globals()
    
    if is_nuitka:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    if system() == "Windows":
        command = os.path.join(base_path, "app", "core", "zju-connect.exe")
    else:
        command = os.path.join(base_path, "app", "core", "zju-connect")
        if os.path.exists(command):
            os.chmod(command, 0o755)

    command_args = [
        command,
        "-server", shlex.quote(server_address),
        "-port", shlex.quote(str(port)),
        "-username", shlex.quote(username),
        "-password", shlex.quote(password)
    ]
    
    # Add DNS server configuration
    if window.auto_dns:
        command_args.extend(["-zju-dns-server", "auto"])
    else:
        command_args.extend(["-zju-dns-server", shlex.quote(dns_server_address)])
    
    if window.http_bind:
        command_args.extend(["-http-bind", shlex.quote("127.0.0.1:" + window.http_bind)])
    
    if window.socks_bind:
        command_args.extend(["-socks-bind", shlex.quote("127.0.0.1:" + window.socks_bind)])

    if not window.keep_alive:
        command_args.append("-disable-keep-alive")
    
    if window.debug_dump:
        command_args.append("-debug-dump")

    if window.disable_multi_line:
        command_args.append("-disable-multi-line")

    # Add certificate file and password if provided
    if window.cert_file:
        command_args.extend(["-cert-file", shlex.quote(window.cert_file)])
        if window.cert_password:
            command_args.extend(["-cert-password", shlex.quote(window.cert_password)])

    command_args.append("-disable-zju-config")
    command_args.append("-skip-domain-resource")
    
    debug_command = command_args.copy()
    username_index = debug_command.index("-username") + 1
    debug_command[username_index] = "********"
    pwd_index = debug_command.index("-password") + 1
    debug_command[pwd_index] = "********"
    
    # Also mask certificate password if present
    if "-cert-password" in debug_command:
        cert_pwd_index = debug_command.index("-cert-password") + 1
        debug_command[cert_pwd_index] = "********"

    window.output_text.append(f"Running command: {' '.join(debug_command)}\n")

    window.worker = CommandWorker(command_args=command_args, proxy_enabled=window.proxy, window=window)
    window.worker.output.connect(lambda text: handle_output(window, text))
    window.worker.finished.connect(lambda: handle_connection_finished(window))
    window.worker.start()

    window.status_label.setText("状态: 正在运行")

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
