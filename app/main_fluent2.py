import sys

from PySide6.QtWidgets import QApplication
from app.view.main_window_fluent import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

sys.exit(app.exec())
