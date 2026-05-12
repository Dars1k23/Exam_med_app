import pandas as pd
import os

def map_kr_to_rows(db_path: str) -> dict:
    """
    Считывает файл БД (Excel), находит колонку 'КР (название)' и 
    возвращает словарь, где ключ - название КР, 
    а значение - список номеров строк (индексов), где это название встречается.
    """
    if not os.path.exists(db_path):
        print(f"Файл не найден: {db_path}")
        return {}

    try:
        df = pd.read_excel(db_path)
        
        # Приводим названия колонок к нижнему регистру для поиска
        columns_lower = {str(c).strip().lower(): c for c in df.columns}
        
        kr_col_name = None
        for col_lower, original_col in columns_lower.items():
            if "кр (название)" in col_lower or "кр" in col_lower and "название" in col_lower:
                kr_col_name = original_col
                break
                
        if not kr_col_name:
            print("Колонка 'КР (название)' не найдена в файле.")
            return {}

        kr_dict = {}
        # Проходим по строкам и собираем индексы
        # Используем iterrows, индекс (row_idx) будет номером строки (начиная с 0, без учета заголовка)
        for row_idx, val in df[kr_col_name].items():
            kr_name = str(val).strip()
            if kr_name and kr_name.lower() != "nan":
                if kr_name not in kr_dict:
                    kr_dict[kr_name] = []
                kr_dict[kr_name].append(row_idx)
                
        return kr_dict

    except Exception as e:
        print(f"Ошибка при обработке {db_path}: {e}")
        return {}
