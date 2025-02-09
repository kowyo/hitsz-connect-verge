import objc
from platform import system

def hide_dock_icon(hide=True):
    """ 使用 macOS API 控制 Dock 图标显示状态 """
    if system() == "Darwin":
        NSApp = objc.lookUpClass("NSApplication").sharedApplication()
        NSApp.setActivationPolicy_(1 if hide else 0)  # 1 = NSApplicationActivationPolicyAccessory, 0 = NSApplicationActivationPolicyRegular
