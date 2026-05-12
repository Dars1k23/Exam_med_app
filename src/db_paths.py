import os
from src.config import DATA_DIR

def get_db_paths(file_path="dataBasePath.txt"):
    """
    Читает файл построчно, где каждая строка — путь до файла БД.
    Создает и возвращает список строк в формате "название файла:путь до бд".
    """
    result = dict()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                filename = line.strip()
                if filename:
                    path = DATA_DIR / (filename + ".xlsx")
                    result[filename]=str(path)
    else:
        print(f"Файл {file_path} не найден.")
    
    return result
