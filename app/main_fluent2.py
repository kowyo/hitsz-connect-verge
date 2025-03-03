import sys

from PySide6.QtWidgets import QApplication
from views.main_window_fluent import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show()

sys.exit(app.exec())
