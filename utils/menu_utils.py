from PySide6.QtWidgets import QMessageBox, QDialog, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit
from PySide6.QtCore import Qt
from PySide6.QtGui import QClipboard
from .check_for_update import check_for_updates

def setup_menubar(window, version):
    """Set up the main window menu bar"""
    menubar = window.menuBar()
    
    # Settings Menu
    settings_menu = menubar.addMenu("设置")
    window.advanced_action = settings_menu.addAction("高级设置")
    # window.advanced_action.triggered.connect(window.toggle_advanced_settings)
    
    # Help Menu
    about_menu = menubar.addMenu("帮助")
    about_menu.addAction("查看日志").triggered.connect(lambda: show_log(window))
    about_menu.addAction("检查更新").triggered.connect(lambda: check_for_updates(window, version))
    about_menu.addAction("关于").triggered.connect(lambda: show_about(window, version))

def show_about(window, version):
    """Show about dialog"""
    about_text = f'''<p style="font-size: 15pt;">HITSZ Connect Verge</p>
    <p style="font-size: 10pt;">Version: {version}</p>
    <p style="font-size: 10pt;">Repository: <a href="https://github.com/kowyo/hitsz-connect-verge">github.com/kowyo/hitsz-connect-verge</a></p>
    <p style="font-size: 10pt;">Author: <a href="https://github.com/kowyo">Kowyo</a></p> '''
    QMessageBox.about(window, "关于 HITSZ Connect Verge", about_text)

def show_log(window):
    """Show the log window"""
    dialog = QDialog(window)
    dialog.setWindowTitle("查看日志")
    dialog.setMinimumSize(300, 400)
    
    layout = QVBoxLayout()
    
    log_text = QTextEdit()
    log_text.setReadOnly(True)
    log_text.setText(window.output_text.toPlainText())
    layout.addWidget(log_text)
    
    copy_button = QPushButton("复制")
    copy_button.clicked.connect(
        lambda: window.QApplication.clipboard().setText(log_text.toPlainText())
    )
    
    close_button = QPushButton("关闭")
    close_button.clicked.connect(dialog.close)

    button_layout = QHBoxLayout()
    button_layout.addWidget(copy_button)
    button_layout.addWidget(close_button)
    layout.addLayout(button_layout)
    
    dialog.setLayout(layout)
    dialog.show()
