import os
import sys
from app.common import resources

def get_version():
    """Get version from .app-version file with fallback"""
    version_file = ':/../.app-version'
    with open(version_file, 'r') as f:
        return f.read().strip()
