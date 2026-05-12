import pandas as pd
import os

def map_variant_to_rows(db_path: str) -> dict:
    """
    Считывает файл БД (Excel), находит колонку 'Вариант' и 
    возвращает словарь, где ключ - название варианта, 
    а значение - список номеров строк (индексов), где это название встречается.
    """
    if not os.path.exists(db_path):
        print(f"Файл не найден: {db_path}")
        return {}

    try:
        df = pd.read_excel(db_path)
        
        # Приводим названия колонок к нижнему регистру для поиска
        columns_lower = {str(c).strip().lower(): c for c in df.columns}
        
        variant_col_name = None
        for col_lower, original_col in columns_lower.items():
            if "вариант" in col_lower:
                variant_col_name = original_col
                break
                
        if not variant_col_name:
            print("Колонка 'Вариант' не найдена в файле.")
            return {}

        variant_dict = {}
        # Проходим по строкам и собираем индексы
        # Используем iterrows, индекс (row_idx) будет номером строки (начиная с 0, без учета заголовка)
        for row_idx, val in df[variant_col_name].items():
            variant_name = str(val).strip()
            if variant_name and variant_name.lower() != "nan":
                if variant_name not in variant_dict:
                    variant_dict[variant_name] = []
                variant_dict[variant_name].append(row_idx)
                
        return variant_dict

    except Exception as e:
        print(f"Ошибка при обработке {db_path}: {e}")
        return {}
