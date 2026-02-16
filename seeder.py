import os
import config
import pandas as pd

import logs

class Seeder:
    def __init__(self, log: logs.LOGS):
        self.log = log

    def create_sample_data(self, empty = True):
        """Создает пустой шаблон Excel, если его нет"""

        os.makedirs(config.SECURE_FOLDER+config.REPORTS_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(config.SECURE_FOLDER+config.QUESTIONS_FILE), exist_ok=True)
        os.makedirs(os.path.dirname(config.SECURE_FOLDER+config.GENERAL_RESULTS_FILE),exist_ok=True)

        if not empty: 
            data = {
                    'category': ['Математика', 'Математика', 'Математика', 'Информатика', 'Информатика', 'Информатика',
                                'Программирование', 'Программирование', 'Программирование', 'Алгоритмы'],
                    'Вопрос': ['2 + 2 = ?', '5 × 3 = ?', '√16 = ?', 'Что такое CPU?', 'Сколько бит в байте?',
                            'Основная память?', 'Что выведет print("Hello")?', 'Тип для целых чисел?',
                            'Сколько элементов в [1,2,3]?', 'Сложность поиска в массиве?'],
                    'ВариантA': ['3', '10', '2', 'Монитор', '4', 'Диск', '1', 'float', '2', 'O(1)'],
                    'ВариантB': ['4', '15', '4', 'Процессор', '8', 'RAM', 'Hello', 'int', '3', 'O(n)'],
                    'ВариантC': ['5', '20', '8', 'Клавиатура', '16', 'CPU', 'None', 'str', '4', 'O(log n)'],
                    'ВариантD': ['6', '25', '16', 'Мышь', '32', 'Видеокарта', 'Error', 'list', '5', 'O(n²)'],
                    'Правильный': ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
                }
        else:
            data = {}

        
        if not os.path.exists(config.SECURE_FOLDER+config.QUESTIONS_FILE):
            pd.DataFrame(data).to_excel(config.SECURE_FOLDER+config.QUESTIONS_FILE, index=False)

        if not os.path.exists(config.SECURE_FOLDER+config.GENERAL_RESULTS_FILE):
            pd.DataFrame({}).to_excel(config.SECURE_FOLDER+config.GENERAL_RESULTS_FILE, index = False)

        if not os.path.exists(config.SECURE_FOLDER+config.LOG_FILE):
            open(config.SECURE_FOLDER+config.LOG_FILE, "w")

