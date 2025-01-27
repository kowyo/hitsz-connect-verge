from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget
)
from qfluentwidgets import (PushButton, CheckBox, LineEdit, TextEdit, PasswordLineEdit, 
                          BodyLabel, TogglePushButton, IconInfoBadge, FluentIcon, setTheme, Theme,
                          SystemThemeListener)
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer
from platform import system
from utils.tray_utils import handle_close_event, quit_app, init_tray_icon
from utils.credential_utils import load_credentials, save_credentials
from utils.connection_utils import start_connection, stop_connection
from utils.common import get_resource_path, get_version
from utils.menu_utils_fluent import setup_menubar, check_for_updates
from utils.config_utils import load_settings

VERSION = get_version()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.themeListener = SystemThemeListener(self)
        self.setWindowTitle("HITSZ Connect Verge")
        self.setMinimumSize(300, 450)
        self.service_name = "hitsz-connect-verge"
        self.username_key = "username"    
        self.password_key = "password"    
        
        self.worker = None
        
        # Create central widget and main layout first
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Setup interface
        self.command_bar = setup_menubar(self, VERSION)
        self.main_layout.addWidget(self.command_bar)
        self.setup_ui()
        self.load_credentials()
        self.load_settings()
        self.tray_icon = init_tray_icon(self)
        
        # Initialize default values
        self.connect_startup = getattr(self, 'connect_startup', False)
        self.silent_mode = getattr(self, 'silent_mode', False)
        self.check_update = getattr(self, 'check_update', True)

        if self.connect_startup:
            QTimer.singleShot(5000, lambda: self.connect_button.setChecked(True))
        
        if self.silent_mode:
            QTimer.singleShot(0, lambda: self.hide())

        if self.check_update:
            QTimer.singleShot(1000, lambda: check_for_updates(parent=self, current_version=VERSION, startup=True))

        setTheme(Theme.AUTO)
        self.themeListener.start()
        self.themeListener.systemThemeChanged.connect(lambda: setTheme(Theme.AUTO))

    def setup_ui(self):
        # Create a container for the main content
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # Account and Password
        layout.addWidget(BodyLabel("用户名"))
        self.username_input = LineEdit(self)  # Add self as parent
        layout.addWidget(self.username_input)

        # layout.PasswordLineEdit()
        layout.addWidget(BodyLabel("密码"))
        self.password_input = PasswordLineEdit(self)  # Add self as parent
        layout.addWidget(self.password_input)

        layout.addSpacing(5)
        self.remember_cb = CheckBox("记住密码")
        layout.addWidget(self.remember_cb)

        layout.addSpacing(5)
        # Status and Output
        status_layout = QHBoxLayout()
        status_layout.addWidget(BodyLabel("运行信息"))
        status_layout.addStretch()
        self.status_icon = IconInfoBadge(FluentIcon.CANCEL_MEDIUM)
        status_layout.addWidget(self.status_icon)
        self.status_label = BodyLabel("状态: 未连接")
        status_layout.addWidget(self.status_label)
        layout.addLayout(status_layout)
        self.output_text = TextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.connect_button = TogglePushButton("连接")
        self.connect_button.toggled.connect(lambda: self.start_connection() if self.connect_button.isChecked() else self.stop_connection())
        self.connect_button.toggled.connect(lambda: self.connect_button.setText("断开") if self.connect_button.isChecked() else self.connect_button.setText("连接"))
        self.connect_button.clicked.connect(self.save_credentials)
        button_layout.addWidget(self.connect_button)

        button_layout.addStretch()
        self.exit_button = PushButton("退出")
        self.exit_button.clicked.connect(self.quit_app)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        # Add content widget to main layout
        self.main_layout.addWidget(content_widget)

    def closeEvent(self, event):
        handle_close_event(self, event, self.tray_icon)

    def quit_app(self):
        self.themeListener.terminate()
        self.themeListener.deleteLater()
        quit_app(self, self.tray_icon)

    def load_credentials(self):
        load_credentials(self)

    def save_credentials(self):
        save_credentials(self)

    def start_connection(self):
        start_connection(self)

    def stop_connection(self):
        stop_connection(self)

    def load_settings(self):
        load_settings(self)

# Run the application
if __name__ == "__main__":
    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)
    
    if system() == "Windows":
        icon_path = get_resource_path("assets/icon.ico")
    elif system() == "Darwin":
        icon_path = get_resource_path("assets/icon.icns")
    elif system() == "Linux":
        icon_path = get_resource_path("assets/icon.png")
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    
    window = MainWindow()
    window.show()
    app.exec()
