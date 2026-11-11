import multiprocessing
import sys


def main() -> int:
    from PyQt6.QtWidgets import QApplication
    from app.main_window import MainWindow
    application = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return application.exec()


if __name__ == '__main__':
    multiprocessing.freeze_support()
    sys.exit(main())
