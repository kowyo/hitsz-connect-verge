import os
import sys
import socket
import time
from platform import system
import shlex
import gc
from .set_proxy import CommandWorker


def is_port_in_use(host, port):
    """Check if a port is currently in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except:
        return True  # Assume port is in use if we can't check


def find_available_port(base_port, max_attempts=10):
    """Find an available port starting from base_port"""
    for i in range(max_attempts):
        port = base_port + i
        if not is_port_in_use("127.0.0.1", port):
            return port
    return None


def wait_for_port_release(host, port, max_wait=5):
    """Wait for a port to be released, useful after stopping a process"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if not is_port_in_use(host, port):
            return True
        time.sleep(0.5)
    return False
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
    if hasattr(window, "connect_button"):
        window.connect_button.setChecked(False)


def start_connection(window):
    """Start VPN connection with automatic port conflict resolution"""
    if window.worker and window.worker.isRunning():
        window.status_label.setText("状态: 正在运行")
        return

    username = window.username_input.text()
    password = window.password_input.text()
    server_address = window.server_address
    port = window.port
    dns_server_address = window.dns_server

    # Check for port conflicts and find alternatives if needed
    original_socks_port = None
    original_http_port = None
    
    if hasattr(window, 'socks_bind') and window.socks_bind:
        try:
            original_socks_port = int(window.socks_bind)
            if is_port_in_use("127.0.0.1", original_socks_port):
                new_port = find_available_port(original_socks_port)
                if new_port:
                    window.output_text.append(f"SOCKS5 端口 {original_socks_port} 被占用，自动切换到端口 {new_port}\n")
                    window.socks_bind = str(new_port)
                else:
                    window.output_text.append(f"警告: 无法找到可用的 SOCKS5 端口，使用原端口 {original_socks_port} 尝试连接\n")
        except ValueError:
            pass
    
    if hasattr(window, 'http_bind') and window.http_bind:
        try:
            original_http_port = int(window.http_bind)
            if is_port_in_use("127.0.0.1", original_http_port):
                new_port = find_available_port(original_http_port)
                if new_port:
                    window.output_text.append(f"HTTP 端口 {original_http_port} 被占用，自动切换到端口 {new_port}\n")
                    window.http_bind = str(new_port)
                else:
                    window.output_text.append(f"警告: 无法找到可用的 HTTP 端口，使用原端口 {original_http_port} 尝试连接\n")
        except ValueError:
            pass

    is_nuitka = "__compiled__" in globals()

    if is_nuitka:
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        base_path = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )

    if system() == "Windows":
        command = os.path.join(base_path, "app", "core", "zju-connect.exe")
    else:
        command = os.path.join(base_path, "app", "core", "zju-connect")
        if os.path.exists(command):
            os.chmod(command, 0o755)

    command_args = [
        command,
        "-server",
        shlex.quote(server_address),
        "-port",
        shlex.quote(str(port)),
        "-username",
        shlex.quote(username),
        "-password",
        shlex.quote(password),
    ]

    # Add DNS server configuration
    if window.auto_dns:
        command_args.extend(["-zju-dns-server", "auto"])
    else:
        command_args.extend(["-zju-dns-server", shlex.quote(dns_server_address)])

    if window.http_bind:
        command_args.extend(
            ["-http-bind", shlex.quote("127.0.0.1:" + window.http_bind)]
        )

    if window.socks_bind:
        command_args.extend(
            ["-socks-bind", shlex.quote("127.0.0.1:" + window.socks_bind)]
        )

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

    # Create a connection finished handler that restores original ports
    def enhanced_connection_finished():
        handle_connection_finished(window)
        # Restore original port settings if they were changed
        if original_socks_port and hasattr(window, 'socks_bind'):
            window.socks_bind = str(original_socks_port)
        if original_http_port and hasattr(window, 'http_bind'):
            window.http_bind = str(original_http_port)

    window.worker = CommandWorker(
        command_args=command_args, proxy_enabled=window.proxy, window=window
    )
    window.worker.output.connect(lambda text: handle_output(window, text))
    window.worker.finished.connect(enhanced_connection_finished)
    window.worker.start()

    window.status_label.setText("状态: 正在运行")


def stop_connection(window):
    """Stop VPN connection with proper cleanup"""
    if window.worker:
        # First stop the worker process
        window.worker.stop()
        window.worker.wait()
        window.worker.output.disconnect()
        window.worker.finished.disconnect()
        window.worker.deleteLater()
        window.worker = None
        gc.collect()
        
        # Wait a moment for ports to be released
        window.output_text.append("等待端口释放...\n")
        
        # Check if ports are released and wait if necessary
        ports_to_check = []
        if hasattr(window, 'socks_bind') and window.socks_bind:
            try:
                ports_to_check.append(int(window.socks_bind))
            except ValueError:
                pass
        
        if hasattr(window, 'http_bind') and window.http_bind:
            try:
                ports_to_check.append(int(window.http_bind))
            except ValueError:
                pass
        
        # Wait for each port to be released
        for port in ports_to_check:
            if wait_for_port_release("127.0.0.1", port, max_wait=3):
                window.output_text.append(f"端口 {port} 已释放\n")
            else:
                window.output_text.append(f"警告: 端口 {port} 可能仍在使用中\n")

    window.status_label.setText("状态: 未连接")
