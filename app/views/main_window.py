from PySide6.QtWidgets import (
    QMainWindow,
    QLabel,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
)
from PySide6.QtCore import QTimer
from utils.tray_utils import handle_close_event, quit_app, init_tray_icon
from utils.credential_utils import save_credentials
from utils.connection_utils import start_connection, stop_connection
from utils.password_utils import toggle_password_visibility
from views.menu_utils import setup_menubar, check_for_updates
from utils.config_utils import load_settings
from common.version import get_version

VERSION = get_version()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HITSZ Connect Verge")
        self.setMinimumSize(300, 450)

        self.worker = None
        self.version = VERSION
        self.load_settings()
        setup_menubar(self, self.version)
        self.setup_ui()
        self.tray_icon = init_tray_icon(self)

        if self.connect_startup:
            QTimer.singleShot(5000, lambda: self.connect_button.setChecked(True))

        if self.check_update:
            self.check_updates_startup()

    def setup_ui(self):
        # Layouts
        layout = QVBoxLayout()

        # Account and Password
        layout.addWidget(QLabel("用户名"))
        self.username_input = QLineEdit()
        self.username_input.setText(self.username)
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("密码"))
        self.password_input = QLineEdit()
        self.password_input.setText(self.password)
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.show_password_cb = QCheckBox("显示密码")
        self.show_password_cb.stateChanged.connect(
            lambda checked: toggle_password_visibility(self.password_input, checked)
        )
        layout.addWidget(self.show_password_cb)

        self.remember_cb = QCheckBox("记住密码")
        self.remember_cb.setChecked(self.remember)
        self.remember_cb.stateChanged.connect(self.save_credentials)
        layout.addWidget(self.remember_cb)

        # Status and Output
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("运行信息"))
        layout.addLayout(status_layout)
        status_layout.addStretch()
        self.status_label = QLabel("状态: 未连接")
        status_layout.addWidget(self.status_label)

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(self.output_text)

        # Buttons
        button_layout = QHBoxLayout()
        self.connect_button = QPushButton("连接")
        self.connect_button.setCheckable(True)
        self.connect_button.toggled.connect(
            lambda: self.start_connection()
            if self.connect_button.isChecked()
            else self.stop_connection()
        )
        self.connect_button.toggled.connect(
            lambda: self.connect_button.setText("断开")
            if self.connect_button.isChecked()
            else self.connect_button.setText("连接")
        )
        self.connect_button.toggled.connect(self.save_credentials)
        button_layout.addWidget(self.connect_button)

        button_layout.addStretch()

        self.exit_button = QPushButton("退出")
        self.exit_button.clicked.connect(self.stop_connection)
        self.exit_button.clicked.connect(self.quit_app)
        button_layout.addWidget(self.exit_button)
        layout.addLayout(button_layout)

        # Set main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def closeEvent(self, event):
        handle_close_event(self, event, self.tray_icon)

    def quit_app(self):
        quit_app(self, self.tray_icon)

    def save_credentials(self):
        save_credentials(self)

    def start_connection(self):
        start_connection(self)

    def stop_connection(self):
        stop_connection(self)

    def load_settings(self):
        load_settings(self)

    def check_updates_startup(self):
        check_for_updates(self, self.version, startup=True)
