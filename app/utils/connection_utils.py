import os
import sys
import socket
import time
import subprocess
from platform import system
import shlex
import gc
import logging
import datetime
from PySide6.QtGui import QTextCursor
from .set_proxy import CommandWorker

logger = logging.getLogger(__name__)

def is_port_in_use(host, port):
    """Check if a port is currently in use"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result == 0
    except Exception as e:
        logger.debug(
            "is_port_in_use check failed for %s:%s: %s", host, port, e
        )
        return True  # Assume port is in use if we can't check


def get_port_process_info(port):
    """Get information about the process using a specific port"""
    try:
        if system() == "Windows":
            # Use netstat to find the process using the port
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]

                        # Special handling for PID 0
                        if pid == "0":
                            return "System process (possibly TIME_WAIT connection)"

                        try:
                            # Get process name from PID
                            tasklist_result = subprocess.run(
                                ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                                capture_output=True,
                                text=True,
                                timeout=3,
                            )
                            lines = tasklist_result.stdout.strip().split("\n")
                            if len(lines) > 1:
                                # Parse CSV output, process name is first field
                                process_name = lines[1].split(",")[0].strip('"')
                                return process_name
                        except Exception as _:
                            logger.debug(
                                "Failed to resolve process name for PID %s while checking port %s",
                                pid,
                                port,
                            )
                            return f"PID {pid}"
        else:
            # Unix-like systems
            result = subprocess.run(
                ["lsof", "-i", f":{port}"], capture_output=True, text=True, timeout=5
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                # Parse lsof output
                parts = lines[1].split()
                if len(parts) > 0:
                    return parts[0]  # Process name
    except subprocess.TimeoutExpired:
        logger.debug("Timed out while checking process info for port %s", port)
    except FileNotFoundError as e:
        logger.debug(
            "Required tool not found while checking process info for port %s: %s",
            port,
            e,
        )
    except Exception as e:
        logger.debug("Failed to get process info for port %s: %s", port, e)
    return None


# find_available_port function removed since we no longer auto-switch ports


def is_port_in_timewait_state(port):
    """Check if a port is in TIME_WAIT state (occupied by PID 0)"""
    try:
        if system() == "Windows":
            result = subprocess.run(
                ["netstat", "-ano"], capture_output=True, text=True, timeout=5
            )
            for line in result.stdout.split("\n"):
                if f":{port}" in line:
                    parts = line.split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        state = parts[3] if len(parts) > 3 else ""
                        # Check TIME_WAIT state or PID 0
                        if pid == "0" or "TIME_WAIT" in state:
                            return True
    except subprocess.TimeoutExpired:
        logger.debug("Timed out while checking TIME_WAIT state for port %s", port)
    except Exception as e:
        logger.debug(
            "Failed to check TIME_WAIT state for port %s: %s", port, e
        )
    return False


def wait_for_port_release(host, port, max_wait=5):
    """Wait for a port to be released, useful after stopping a process"""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if not is_port_in_use(host, port):
            return True

        # Check if occupied by system process (TIME_WAIT)
        process_info = get_port_process_info(port)
        if process_info and ("系统进程" in process_info or "System process" in process_info):
            # For TIME_WAIT connections, shorter polling may help
            time.sleep(0.05)
        else:
            time.sleep(0.1)
    return False


def handle_output(window, text):
    """Handle output text from the worker with automatic log rotation"""
    # Use the enhanced append function with rotation
    append_log_with_rotation(
        window, text.rstrip()
    )  # Remove trailing newline since append_log_with_rotation doesn't add one


def _rotate_logs_if_needed(window):
    """Rotate logs if they exceed the maximum line count"""
    MAX_LOG_LINES = 200
    KEEP_LINES = 120  # Keep this many lines after rotation

    # Get current document
    document = window.output_text.document()
    line_count = document.blockCount()

    if line_count > MAX_LOG_LINES:
        # Get all text
        all_text = window.output_text.toPlainText()
        lines = all_text.split("\n")

        # Keep the most recent KEEP_LINES lines
        recent_lines = lines[-KEEP_LINES:]

        # Add a rotation marker with timestamp

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        rotation_marker = (
            f"--- Log rotated ({timestamp}) - keeping last {KEEP_LINES} lines ---"
        )

        # Combine the marker with recent lines
        new_content = rotation_marker + "\n" + "\n".join(recent_lines)

        # Replace all content efficiently
        window.output_text.setPlainText(new_content)

        # Scroll to bottom to show latest content

        cursor = window.output_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        window.output_text.setTextCursor(cursor)


def append_log_with_rotation(window, text):
    """Enhanced log append function with automatic rotation"""
    # Add the new text
    window.output_text.append(text)

    # Check if log rotation is needed
    _rotate_logs_if_needed(window)


def _check_single_port_conflict(window, port_type, bind_value, used_ports, prior_port_label=None):
    """Check a single port bind and return a list of conflict messages.

    - port_type: e.g., "SOCKS5" or "HTTP"
    - bind_value: string port value from window (e.g., window.socks_bind)
    - used_ports: a set to track already used ports within current session's check
    - prior_port_label: if provided, when current port is in used_ports,
      report conflict with this label (e.g., "SOCKS5 port")
    """
    conflict_messages = []
    if not bind_value:
        return conflict_messages

    try:
        port_value = int(bind_value)

        # Check conflict with previously recorded port(s)
        if prior_port_label and port_value in used_ports:
            conflict_messages.append(
                f"{port_type} port {port_value} conflicts with {prior_port_label}"
            )
        elif is_port_in_use("127.0.0.1", port_value):
            process_info = get_port_process_info(port_value)
            if process_info:
                if ("系统进程" in process_info) or ("System process" in process_info):
                    append_log_with_rotation(
                        window,
                        f"⚠️  {port_type} port {port_value} is in TIME_WAIT state, will attempt to wait for release...",
                    )
                    if wait_for_port_release("127.0.0.1", port_value, max_wait=3):
                        append_log_with_rotation(
                            window, f"✅ {port_type} port {port_value} has been released"
                        )
                    else:
                        conflict_messages.append(
                            f"{port_type} port {port_value} is occupied by {process_info}"
                        )
                else:
                    conflict_messages.append(
                        f"{port_type} port {port_value} is occupied by program {process_info}"
                    )
            else:
                conflict_messages.append(
                    f"{port_type} port {port_value} is occupied by another program"
                )

        # Record this port as used for subsequent checks
        used_ports.add(port_value)

    except ValueError:
        append_log_with_rotation(
            window, f"Warning: invalid {port_type} port configuration: {bind_value}"
        )

    return conflict_messages


def handle_connection_finished(window):
    """Handle connection finished event with proper cleanup"""
    if window.worker:
        window.worker.output.disconnect()
        window.worker.finished.disconnect()
        window.worker.deleteLater()
        window.worker = None
        gc.collect()

    # Use the new status update method to update text and indicator
    if hasattr(window, "update_status"):
        window.update_status("状态: 未连接", connected=False)
    else:
        # Backward compatibility
        window.status_label.setText("状态: 未连接")

    if hasattr(window, "connect_button"):
        window.connect_button.setChecked(False)


def start_connection(window):
    """Start VPN connection with automatic port conflict resolution"""
    if window.worker and window.worker.isRunning():
        if hasattr(window, "update_status"):
            window.update_status("状态: 正在运行", connected=True)
        else:
            window.status_label.setText("状态: 正在运行")
        return

    username = window.username_input.text()
    password = window.password_input.text()
    server_address = window.server_address
    port = window.port
    dns_server_address = window.dns_server

    # Check for port conflicts but do not automatically switch ports
    append_log_with_rotation(
        window,
        f"Port configuration check - SOCKS5: {getattr(window, 'socks_bind', 'None')}, HTTP: {getattr(window, 'http_bind', 'None')}",
    )

    # Check port conflicts, warn only, do not auto-switch
    used_ports = set()
    port_conflicts = []

    # SOCKS5 port check
    if hasattr(window, "socks_bind") and window.socks_bind:
        port_conflicts.extend(
            _check_single_port_conflict(
                window,
                port_type="SOCKS5",
                bind_value=window.socks_bind,
                used_ports=used_ports,
            )
        )

    # HTTP port check
    if hasattr(window, "http_bind") and window.http_bind:
        # If SOCKS5 port already recorded, pass label for clearer conflict message
        port_conflicts.extend(
            _check_single_port_conflict(
                window,
                port_type="HTTP",
                bind_value=window.http_bind,
                used_ports=used_ports,
                prior_port_label="SOCKS5 port",
            )
        )

    # If there are conflicts, warn but still attempt to connect
    if port_conflicts:
        for conflict in port_conflicts:
            append_log_with_rotation(window, f"⚠️  {conflict}")
        append_log_with_rotation(
            window,
            "Note: Port conflicts detected; will still attempt to connect. If the connection fails, please check the port configuration.",
        )

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

    # Check if executable exists
    if not os.path.exists(command):
        error_msg = (
            f"Error: zju-connect executable not found\n"
            f"Path: {command}\n"
            f"Please ensure all required files are properly installed."
        )
        append_log_with_rotation(window, error_msg)
        if hasattr(window, "update_status"):
            window.update_status("状态: 启动失败", connected=False)
        else:
            window.status_label.setText("状态: 启动失败")
        if hasattr(window, "connect_button"):
            window.connect_button.setChecked(False)
        return

    # Set executable permission on Unix-like systems
    if system() != "Windows" and os.path.exists(command):
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
        append_log_with_rotation(
            window, f"Final HTTP port configuration: 127.0.0.1:{window.http_bind}"
        )
        command_args.extend(
            ["-http-bind", shlex.quote("127.0.0.1:" + window.http_bind)]
        )

    if window.socks_bind:
        append_log_with_rotation(
            window, f"Final SOCKS5 port configuration: 127.0.0.1:{window.socks_bind}"
        )
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

    append_log_with_rotation(window, f"Running command: {' '.join(debug_command)}")

    # Create a connection finished handler
    def enhanced_connection_finished():
        handle_connection_finished(window)
        # No need to restore ports since we don't auto-switch them anymore

    window.worker = CommandWorker(
        command_args=command_args, proxy_enabled=window.proxy, window=window
    )
    window.worker.output.connect(lambda text: handle_output(window, text))
    window.worker.finished.connect(enhanced_connection_finished)
    window.worker.start()

    if hasattr(window, "update_status"):
        window.update_status("状态: 正在运行", connected=True)
    else:
        window.status_label.setText("状态: 正在运行")


def stop_connection(window):
    """Stop VPN connection with proper cleanup"""
    if window.worker:
        try:
            # First stop the worker process
            window.worker.stop()

            # Wait for thread to finish, but with timeout
            if not window.worker.wait(5000):  # 5 second timeout
                # If thread doesn't finish gracefully, terminate it
                window.worker.terminate()
                window.worker.wait(2000)  # 2 second timeout for termination

            # Safely disconnect signals
            try:
                window.worker.output.disconnect()
            except (RuntimeError, TypeError):
                pass  # Signal may already be disconnected

            try:
                window.worker.finished.disconnect()
            except (RuntimeError, TypeError):
                pass  # Signal may already be disconnected

            # Schedule thread deletion
            window.worker.deleteLater()
            window.worker = None
            gc.collect()

            # Wait a moment for ports to be released
            if hasattr(window, "output_text"):
                append_log_with_rotation(window, "Waiting for ports to be released...")

            # Check if ports are released and wait if necessary
            ports_to_check = []
            for name in ("socks_bind", "http_bind"):
                value = getattr(window, name, None)
                if not value:
                    continue
                try:
                    ports_to_check.append(int(value))
                except (TypeError, ValueError):
                    continue

            # Wait for each port to be released
            for port in ports_to_check:
                if wait_for_port_release("127.0.0.1", port, max_wait=3):
                    if hasattr(window, "output_text"):
                        append_log_with_rotation(window, f"Port {port} has been released")
                else:
                    # Check TIME_WAIT state
                    if is_port_in_timewait_state(port):
                        if hasattr(window, "output_text"):
                            append_log_with_rotation(
                                window,
                                f"Port {port} is in TIME_WAIT state (the system will release it automatically)",
                            )
                    else:
                        if hasattr(window, "output_text"):
                            append_log_with_rotation(
                                window, f"Warning: Port {port} may still be in use"
                            )

        except Exception as e:
            # Handle any cleanup errors gracefully
            if hasattr(window, "output_text"):
                append_log_with_rotation(window, f"Error occurred while cleaning up connection: {str(e)}")

    if hasattr(window, "update_status"):
        window.update_status("状态: 未连接", connected=False)
    elif hasattr(window, "status_label"):
        window.status_label.setText("状态: 未连接")
