import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.db_paths import get_db_paths 

if __name__ == "__main__":
    print(get_db_paths())
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
