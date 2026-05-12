import sys
from PyQt6.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.db_paths import get_db_paths
from src.kr_mapper import map_kr_to_rows

if __name__ == "__main__":
    # Получаем пути до БД
    db_list = get_db_paths("dataBasePath.txt")
    print("Список БД:", db_list)
    
    print(map_kr_to_rows("/home/semyon/Downloads/Telegram Desktop/NOK_pediatric_surgery_1000_items_v3.xlsx"))
    

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

