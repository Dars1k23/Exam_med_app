import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

import config
import seeder

class DB:
    def __init__(self):
        seeder.seeder.create_sample_data()
        self.df = pd.DataFrame()
        self.load_questions()


    def load_questions(self):
        """Загружает вопросы """

        try:
            # Читаем Excel через pandas
            self.df = pd.read_excel(config.QUESTIONS_FILE, engine="openpyxl")
            print(f"База загружена: {len(self.df)} строк")

        except Exception as e:
            messagebox.showerror("Критическая ошибка", f"Ошибка при чтении Excel: {e}")

    def save_result_to_excel(self, questions, score, user_name, category):
        """Добавляет результат студента в общую ведомость (all_results.xlsx)"""
        
        try:
            if questions is None:
                messagebox.showerror(
                    "Ошибка записи",
                    f"Список вопросов пуст",
                )
                return
        
            filename = config.GENERAL_RESULTS_FILE
            percent = (score / len(questions)) * 100

            # Данные для новой строки
            new_data = pd.DataFrame(
                [
                    {
                        "Дата": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "ФИО": user_name,
                        "Предмет": category,
                        "Баллы": f"{score}/{len(questions)}",
                        "Процент": f"{percent:.1f}%",
                    }
                ]
            )

            # Читаем старые, добавляем новые
            existing_df = pd.read_excel(filename)
            updated_df = pd.concat([existing_df, new_data], ignore_index=True)
            updated_df.to_excel(filename, index=False)

            print(f"✓ Результат {user_name} занесен в общую ведомость.")
        except Exception as e:
            messagebox.showerror(
                "Ошибка записи",
                f"Не удалось обновить Excel: {e}\nВозможно, файл открыт!",
            )
    
    def generate_pdf_report(self, questions, score, user_name, category, user_answers):
        """Генерация официального PDF-отчета """
        try:
            # 1. Создаем объект PDF
            pdf = FPDF()
            pdf.add_page()

            # 2. ПОДКЛЮЧАЕМ ШРИФТ ПРАВИЛЬНО
            # Файл 'arial.ttf' ОБЯЗАТЕЛЬНО должен лежать в папке с beta.py
            font_path = config.FONT_FILE

            if os.path.exists(font_path):
                # Регистрируем шрифт под именем 'MyArial'
                pdf.add_font("MyArial", "", font_path)
                pdf.set_font("MyArial", size=12)
            else:
                messagebox.showerror(
                    "Ошибка", "Не удалось подключить фонт для создания pdf - репорта"
                )
                return

            # 3. Заголовок (используем новые параметры вместо ln=True)
            pdf.set_font("MyArial", size=16)
            pdf.cell(
                0,
                10,
                text="ОФИЦИАЛЬНЫЙ ОТЧЕТ ПО ЭКЗАМЕНУ",
                align="C",
                new_x="LMARGIN",
                new_y="NEXT",
            )
            pdf.ln(10)

            # 4. Инфо о студенте
            pdf.set_font("MyArial", size=12)
            pdf.cell(
                0, 10, text=f"Студент: {user_name}", new_x="LMARGIN", new_y="NEXT"
            )
            pdf.cell(
                0,
                10,
                text=f"Направление: {category}",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            if questions is not None:
                percent = (score / len(questions)) * 100
                pdf.cell(
                    0,
                    10,
                    text=f"Результат: {percent:.1f}%",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                pdf.ln(10)

                # 5. Список вопросов
                for i in range(len(questions)):
                    data = user_answers.get(i)
                    if not data:
                        continue
                    is_correct = data["chosen"] == data["correct"]
                    status = "ВЕРНО" if is_correct else "ОШИБКА"

                    # Пишем вопрос
                    pdf.set_font("MyArial", size=10)
                    text_q = f"Вопрос {i + 1}: {data['question']} — {status}"
                    pdf.multi_cell(0, 8, text=text_q, new_x="LMARGIN", new_y="NEXT")

                    # Пишем ответы
                    pdf.set_font("MyArial", size=9)
                    pdf.multi_cell(
                        0,
                        6,
                        text=f"   Ваш ответ: {data['text_chosen']}",
                        new_x="LMARGIN",
                        new_y="NEXT",
                    )
                    if not is_correct:
                        pdf.multi_cell(
                            0,
                            6,
                            text=f"   Верный: {data['text_correct']}",
                            new_x="LMARGIN",
                            new_y="NEXT",
                        )
                    pdf.ln(2)
            else:
                messagebox.showerror(
                    "Ошибка записи",
                    f"Список вопросов пуст",
                )
                return

            # Сохранение (добавляем время, чтобы не затирать старые)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{config.REPORTS_DIR}/{user_name}/Отчет_{user_name}_{timestamp}.pdf"
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            pdf.output(filename)

            print(f"✓ PDF создан: {filename}")

        except Exception as e:
            messagebox.showerror(
                "Ошибка генерации PDF: ",
                f"{e}",
            )
    
    def generate_questions(self, category, count):
        return self.df[self.df["category"] == category].sample(n=count, replace=False).reset_index(drop=True)

db = DB()