import sys

from PySide6.QtWidgets import QApplication
from main_window import MainWindow
import qdarktheme

if __name__ == "__main__":
    qdarktheme.enable_hi_dpi()
    app = QApplication(sys.argv)
    qdarktheme.setup_theme("auto")
    win = MainWindow()
    win.show()
    app.exec()