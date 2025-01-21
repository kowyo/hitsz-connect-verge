import os
import sys

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_version():
    """Get version from .app-version file with fallback"""
    version_file = get_resource_path('.app-version')
    with open(version_file, 'r') as f:
        return f.read().strip()
