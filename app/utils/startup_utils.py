import os
import sys
from platform import system
if system() == "Windows":
    import winreg
import subprocess

def set_launch_at_login(enable: bool):
    """Set application to launch at login"""
    if system() == "Windows":
        app_path = sys.argv[0]
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    winreg.SetValueEx(key, "HITSZ Connect Verge", 0, winreg.REG_SZ, f'"{app_path}"')
                else:
                    try:
                        winreg.DeleteValue(key, "HITSZ Connect Verge")
                    except FileNotFoundError:
                        pass
        except OSError:
            pass
            
    elif system() == "Darwin":
        try:
            app_path = sys.argv[0]
            if ".app/Contents/MacOS/" in app_path:
                # Extract path to the .app bundle
                app_path = app_path.split(".app/Contents/MacOS/")[0] + ".app"
            
            if enable:
                subprocess.run([
                    'osascript',
                    '-e',
                    f'tell application "System Events" to make login item at end with properties {{path:"{app_path}", hidden:false}}'
                ])
            else:
                app_name = os.path.basename(app_path).replace(".app", "")
                subprocess.run([
                    'osascript',
                    '-e',
                    f'tell application "System Events" to delete login item "{app_name}"'
                ])
        except subprocess.SubprocessError:
            pass

def get_launch_at_login() -> bool:
    """Check if application is set to launch at login"""
    if system() == "Windows":
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ) as key:
                winreg.QueryValueEx(key, "HITSZ Connect Verge")
                return True
        except WindowsError:
            return False
            
    elif system() == "Darwin":
        try:
            app_name = os.path.basename(sys.argv[0]).replace(".app", "")     
            result = subprocess.run([
                'osascript',
                '-e',
                'tell application "System Events" to get the name of every login item'
            ], capture_output=True, text=True)
            if app_name in result.stdout:
                return True
            else:
                return False
        except subprocess.SubprocessError:
            return False
    
    return False
