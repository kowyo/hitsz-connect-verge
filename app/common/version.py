import sys
from . import resources
from PySide6.QtCore import QFile, QIODevice

def get_version():
    """Get version from QRC resource with fallback"""
    try:
        version_file = QFile(":/texts/.app-version")
        if version_file.open(QIODevice.ReadOnly):
            version = version_file.readAll().data().decode("utf-8")
            version_file.close()
            return version
        else:
            raise Exception("Could not read version from resource")
        
    except Exception as e:
        print(f"Error reading version from resource: {e}", file=sys.stderr)
