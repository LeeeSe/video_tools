from front_end.logic_code.main import MainWindow
from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    app.exec_()
