import os
import sys
from platform import system
if system() == "Windows":
    import winreg
import plistlib

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
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.kowyo.hitsz-connect-verge.plist")
        app_path = sys.argv[0]
        
        plist_content = {
            'Label': 'com.kowyo.hitsz-connect-verge',
            'ProgramArguments': [app_path],
            'RunAtLoad': True,
        }
        
        if enable:
            with open(plist_path, 'wb') as f:
                plistlib.dump(plist_content, f)
            os.chmod(plist_path, 0o644)
        else:
            try:
                os.remove(plist_path)
            except FileNotFoundError:
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
        plist_path = os.path.expanduser("~/Library/LaunchAgents/com.kowyo.hitsz-connect-verge.plist")
        return os.path.exists(plist_path)
    
    return False
