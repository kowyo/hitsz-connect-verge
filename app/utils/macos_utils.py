import objc
from platform import system

def hide_dock_icon(hide=True):
    """ Control the visibility of the app icon in the dock using macOS API """
    if system() == "Darwin":
        NSApp = objc.lookUpClass("NSApplication").sharedApplication()
        NSApp.setActivationPolicy_(1 if hide else 0)  # 1 = NSApplicationActivationPolicyAccessory, 0 = NSApplicationActivationPolicyRegular
