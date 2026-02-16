import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

import config

class ExamApp:
    def __init__(self):
        """Инициализация приложения: создание окна и загрузка данных"""
        self.root = tk.Tk()
        self.root.title("🎓 MedExam v1.0")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1e1e2e")  # Темная тема (VS Code style)

        # Растягиваем сетку окна, чтобы элементы центрировались
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Переменные состояния (хранят данные текущей сессии)
        self.df = self.load_questions()  # Вся таблица из Excel
        self.questions = None  # Вопросы выбранной категории
        self.current_question = 0  # Индекс текущего вопроса
        self.score = 0  # Счетчик правильных ответов
        self.user_answers = {}  # Словарь ответов: {индекс: "ВариантA"}
        self.nav_buttons = {}
        self.answer_buttons = {}
        self.question_text_widget = None
        self.question_label_var = None  # Для текста "Вопрос X / Y"
        self.visited_questions = (
            set()
        )  # Для отслеживания, какие вопросы уже открывали (для подсветки в навигашке)

        self.show_start_screen()

    # --- ЛОГИКА РАБОТЫ С ДАННЫМИ (BACKEND) ---

    

    def save_result_to_excel(self):
        """Добавляет результат студента в общую ведомость (all_results.xlsx)"""
        try:
            if self.questions is None:
                return
            filename = config.GENERAL_RESULTS_FILE
            percent = (self.score / len(self.questions)) * 100

            # Данные для новой строки
            new_data = pd.DataFrame(
                [
                    {
                        "Дата": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "ФИО": self.user_name,
                        "Предмет": self.category,
                        "Баллы": f"{self.score}/{len(self.questions)}",
                        "Процент": f"{percent:.1f}%",
                    }
                ]
            )

            # Читаем старые, добавляем новые
            existing_df = pd.read_excel(filename)
            updated_df = pd.concat([existing_df, new_data], ignore_index=True)
            updated_df.to_excel(filename, index=False)

            print(f"✓ Результат {self.user_name} занесен в общую ведомость.")
        except Exception as e:
            messagebox.showerror(
                "Ошибка записи",
                f"Не удалось обновить Excel: {e}\nВозможно, файл открыт!",
            )

    # --- ИНТЕРФЕЙС (FRONTEND) ---

    def show_start_screen(self):
        """Экран приветствия и выбора категории"""
        self.clear_screen()

        # Главный контейнер (Frame)
        container = tk.Frame(
            self.root, bg="#2d2d44", padx=30, pady=30, relief="ridge", bd=2
        )
        container.place(relx=0.5, rely=0.5, anchor="center")  # Центрируем

        tk.Label(
            container,
            text="Вход в систему",
            font=("Arial", 20, "bold"),
            bg="#2d2d44",
            fg="#00d4aa",
        ).pack(pady=10)

        # Поле ввода имени
        tk.Label(container, text="Введите ФИО:", bg="#2d2d44", fg="white").pack()
        self.name_entry = tk.Entry(container, font=("Arial", 14), width=30)
        self.name_entry.pack(pady=10)

        # Список категорий из Excel
        tk.Label(container, text="Выберите предмет:", bg="#2d2d44", fg="white").pack()
        self.cat_var = tk.StringVar()
        categories = sorted(self.df["category"].unique().tolist())

        self.cat_combo = ttk.Combobox(
            container, textvariable=self.cat_var, values=categories, state="readonly"
        )
        self.cat_combo.pack(pady=10, fill="x")
        # Кнопка старта
        tk.Button(
            container,
            text="НАЧАТЬ",
            bg="#667eea",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.start_test,
        ).pack(pady=20)

    def update_nav_button(self, index, color):
        """Меняет цвет конкретной кнопки без перерисовки окна"""
        if index in self.nav_buttons:
            self.nav_buttons[index].config(bg=color)

    def save_current_answer(self):
        """Сохраняет ответ БЕЗ перерисовки всего экрана"""
        if self.questions is None:
            return
        ans = self.ans_var.get()
        q_idx = self.current_question
        q_data = self.questions.iloc[q_idx]

        self.user_answers[q_idx] = {
            "question": q_data["Вопрос"],
            "chosen": ans,
            "correct": q_data["Правильный"],
            "text_chosen": q_data[f"Вариант{ans}"],
            "text_correct": q_data[f"Вариант{q_data['Правильный']}"],
        }

        # Вместо show_test_screen() обновляем только навигационную кнопку
        self.update_nav_button(q_idx, "#00d4aa")  # Красим в зеленый

    def jump_to_question(self, index):
        self.current_question = index
        self.show_test_screen()

    def next_question_nav(self):
        """Логика кнопки 'Вперед'"""
        if self.questions is None:
            return
        self.visited_questions.add(
            self.current_question
        )  # Помечаем текущий как посещенный
        if self.current_question < len(self.questions) - 1:
            self.current_question += 1
            self.show_test_screen()
        else:
            # Если это был последний вопрос
            self.confirm_finish()

    def prev_question(self):
        if self.current_question > 0:
            self.current_question -= 1
            self.show_test_screen()

    def confirm_finish(self):
        if self.questions is None:
            return
        answered = len(self.user_answers)
        total = len(self.questions)
        if answered < total:
            if not messagebox.askyesno(
                "Внимание", f"Вы ответили только на {answered} из {total}. Закончить?"
            ):
                return

        # Считаем итоговый score перед финишем
        self.score = sum(
            1 for a in self.user_answers.values() if a["chosen"] == a["correct"]
        )
        self.finish_test()

    def create_nav_buttons(self):
        """Создает кнопки навигации один раз"""
        if self.questions is None:
            return
        for i in range(len(self.questions)):
            btn = tk.Button(
                self.nav_grid,
                text=str(i + 1),
                width=3,
                font=("Arial", 7),
                command=lambda x=i: self.jump_to_question(x),
            )
            btn.grid(row=i // 10, column=i % 10, padx=1, pady=1)
            self.nav_buttons[i] = btn
        self.refresh_nav_colors()

    def update_question_data(self):
        """Обновляет только содержимое виджетов"""
        # Safety check: ensure all required objects are initialized
        if (
            self.questions is None
            or self.question_label_var is None
            or self.question_text_widget is None
            or not self.answer_buttons
            or not self.nav_buttons
        ):
            return

        q_data = self.questions.iloc[self.current_question]

        # Обновляем заголовок и текст вопроса
        self.question_label_var.set(
            f"ВОПРОС {self.current_question + 1} / {len(self.questions)}"
        )

        self.question_text_widget.configure(state="normal")
        self.question_text_widget.delete("1.0", "end")
        self.question_text_widget.insert("1.0", q_data["Вопрос"])
        self.question_text_widget.tag_add("center", "1.0", "end-1c")
        self.question_text_widget.configure(state="disabled")

        # Обновляем варианты ответов
        for letter in ["A", "B", "C", "D"]:
            self.answer_buttons[letter].config(
                text=f"{letter}) {q_data[f'Вариант{letter}']}"
            )

        # Сбрасываем или устанавливаем галку
        if self.current_question in self.user_answers:
            self.ans_var.set(self.user_answers[self.current_question]["chosen"])
        else:
            self.ans_var.set("")

        # Обновляем кнопки навигации и управления
        self.refresh_nav_colors()

        # Настройка кнопки Вперед/Финиш
        if self.current_question == len(self.questions) - 1:
            self.btn_next.config(text="ФИНИШ >>", bg="#00d4aa")
        else:
            self.btn_next.config(text="Вперед >>", bg="#4e4e6a")

    def refresh_nav_colors(self):
        """Перекрашивает кнопки навигации"""
        for i, btn in self.nav_buttons.items():
            if i == self.current_question:
                color = "#667eea"
            elif i in self.user_answers:
                color = "#00d4aa"
            elif i in self.visited_questions:
                color = "#f39c12"
            else:
                color = "#444444"
            btn.config(bg=color, fg="white")

    def show_test_screen(self):
        # Если экран уже отрисован, просто обновляем контент и выходим
        if hasattr(self, "test_ui_created") and self.test_ui_created:
            self.update_question_data()
            return

        self.clear_screen()
        self.test_ui_created = True
        self.visited_questions.add(self.current_question)

        # --- ЛЕВАЯ ПАНЕЛЬ (Навигация) ---
        nav_frame = tk.Frame(self.root, bg="#2d2d44", width=250)
        nav_frame.pack(side="left", fill="y", padx=5, pady=5)

        tk.Label(
            nav_frame,
            text="НАВИГАЦИЯ",
            font=("Arial", 12, "bold"),
            bg="#2d2d44",
            fg="white",
        ).pack(pady=10)

        self.nav_grid = tk.Frame(nav_frame, bg="#2d2d44")
        self.nav_grid.pack(padx=10)
        self.create_nav_buttons()

        # --- ПРАВАЯ ЧАСТЬ (Контент) ---
        right_area = tk.Frame(self.root, bg="#1e1e2e")
        right_area.pack(side="right", fill="both", expand=True)

        content_wrapper = tk.Frame(right_area, bg="#1e1e2e")
        content_wrapper.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85)

        # Переменная для заголовка (Вопрос 1 / 10)
        self.question_label_var = tk.StringVar()
        tk.Label(
            content_wrapper,
            textvariable=self.question_label_var,
            bg="#1e1e2e",
            fg="#888",
            font=("Arial", 10),
        ).pack()

        # Поле вопроса
        text_frame = tk.Frame(content_wrapper, bg="#1e1e2e")
        text_frame.pack(pady=10, fill="x")

        self.question_text_widget = tk.Text(
            text_frame,
            font=("Arial", 16, "bold"),
            bg="#1e1e2e",
            fg="white",
            relief="flat",
            height=8,
            padx=20,
            wrap="word",
            state="disabled",
        )
        self.question_text_widget.tag_configure("center", justify="center")
        self.question_text_widget.pack(side="left", fill="x", expand=True)

        # Варианты ответов
        self.ans_var = tk.StringVar()
        self.answer_buttons = {}
        for letter in ["A", "B", "C", "D"]:
            rb = tk.Radiobutton(
                content_wrapper,
                text="",
                variable=self.ans_var,
                value=letter,
                indicatoron=False,
                bg="#2d2d44",
                fg="white",
                selectcolor="#667eea",
                font=("Arial", 12),
                width=55,
                anchor="w",
                padx=20,
                pady=10,
                command=self.save_current_answer,
                cursor="hand2",
            )
            rb.pack(pady=4)
            rb.bind("<Enter>", lambda e, b=rb: b.config(bg="#3d3d5c"))
            rb.bind("<Leave>", lambda e, b=rb: b.config(bg="#2d2d44"))
            self.answer_buttons[letter] = rb

        # Кнопки управления
        controls = tk.Frame(content_wrapper, bg="#1e1e2e")
        controls.pack(fill="x", pady=20)

        self.btn_prev = tk.Button(
            controls, text="<< Назад", command=self.prev_question, width=12
        )
        self.btn_prev.pack(side="left")

        self.btn_next = tk.Button(
            controls,
            text="Вперед >>",
            command=self.next_question_nav,
            width=12,
            font=("Arial", 11, "bold"),
        )
        self.btn_next.pack(side="right")

        # Заполняем данными первый раз
        self.update_question_data()

    # --- СЛУЖЕБНЫЕ МЕТОДЫ ---

    def start_test(self):
        """Подготовка данных перед началом теста с проверкой ФИО"""
        # Убираем лишние пробелы по краям
        self.user_name = self.name_entry.get().strip()
        category = self.cat_var.get()

        # Проверка на пустое имя (или если ввели только пробелы)
        if not self.user_name or self.user_name == "Студент":
            messagebox.showwarning(
                "Доступ запрещен",
                "Пожалуйста, введите ваше полное ФИО для идентификации в отчете!",
            )
            return

        # Проверка на выбор категории
        if not category:
            messagebox.showwarning("Внимание", "Выберите предмет экзамена!")
            return

        # Если проверки пройдены — сохраняем категорию и грузим вопросы
        self.category = category
        self.questions = self.df[self.df["category"] == category].reset_index(drop=True)

        # Проверка, есть ли вопросы в этой категории вообще
        if self.questions.empty:
            messagebox.showerror(
                "Ошибка базы", f"В категории '{category}' нет вопросов!"
            )
            return

        self.show_test_screen()

    def generate_pdf_report(self):
        """Генерация официального PDF-отчета (исправленная версия)"""
        try:
            # 1. Создаем объект PDF
            pdf = FPDF()
            pdf.add_page()

            # 2. ПОДКЛЮЧАЕМ ШРИФТ ПРАВИЛЬНО
            # Файл 'arial.ttf' ОБЯЗАТЕЛЬНО должен лежать в папке с beta.py
            font_path = "ARIAL.TTF"

            if os.path.exists(font_path):
                # Регистрируем шрифт под именем 'MyArial'
                pdf.add_font("MyArial", "", font_path)
                pdf.set_font("MyArial", size=12)
            else:
                messagebox.showerror(
                    "Ошибка", "Файл arial.ttf не найден в папке с программой!"
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
                0, 10, text=f"Студент: {self.user_name}", new_x="LMARGIN", new_y="NEXT"
            )
            pdf.cell(
                0,
                10,
                text=f"Направление: {self.category}",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            if self.questions is not None:
                percent = (self.score / len(self.questions)) * 100
                pdf.cell(
                    0,
                    10,
                    text=f"Результат: {percent:.1f}%",
                    new_x="LMARGIN",
                    new_y="NEXT",
                )
                pdf.ln(10)

                # 5. Список вопросов
                for i in range(len(self.questions)):
                    data = self.user_answers.get(i)
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

            # Сохранение (добавляем время, чтобы не затирать старые)
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"{config.REPORTS_DIR}/Отчет_{self.user_name}_{timestamp}.pdf"
            pdf.output(filename)
            print(f"✓ PDF создан: {filename}")

        except Exception as e:
            print(f"❌ Ошибка генерации PDF: {e}")

    def finish_test(self):
        """Финал: Запись в ведомость, создание PDF и показ итогов"""
        self.save_result_to_excel()  # Теперь пишет в общую таблицу
        self.generate_pdf_report()  # DF
        self.show_results_screen()

    def show_results_screen(self):
        """Финальный экран: диаграмма слева + список разбора справа"""
        self.clear_screen()

        if self.questions is None:
            return
        total = len(self.questions)
        percent = (self.score / total) * 100

        # --- ЛЕВАЯ ПАНЕЛЬ (Статистика) ---
        left_panel = tk.Frame(self.root, bg="#1e1e2e", width=350)
        left_panel.pack(side="left", fill="y", padx=20)

        tk.Label(
            left_panel,
            text="ИТОГИ ТЕСТА",
            font=("Arial", 22, "bold"),
            bg="#1e1e2e",
            fg="#00d4aa",
        ).pack(pady=20)

        tk.Label(
            left_panel,
            text=f"Баллы: {self.score} из {total}\n({percent:.1f}%)",
            font=("Arial", 16),
            bg="#1e1e2e",
            fg="white",
        ).pack(pady=20)

        tk.Button(
            left_panel,
            text="В ГЛАВНОЕ МЕНЮ",
            command=self.show_start_screen,
            bg="#667eea",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=8,
        ).pack(side="bottom", pady=40)

        # --- ПРАВАЯ ПАНЕЛЬ (Список ответов) ---
        right_panel = tk.Frame(self.root, bg="#2d2d44")
        right_panel.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        tk.Label(
            right_panel,
            text="Разбор полетов:",
            font=("Arial", 14, "bold"),
            bg="#2d2d44",
            fg="white",
        ).pack(pady=5)

        # Текстовое поле с прокруткой
        txt_area = tk.Text(
            right_panel, bg="#1e1e2e", fg="white", font=("Arial", 11), padx=10, pady=10
        )
        scrollbar = tk.Scrollbar(right_panel, command=txt_area.yview)
        txt_area.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        txt_area.pack(side="left", fill="both", expand=True)

        # Генерируем текст разбора
        for i in range(total):
            data = self.user_answers.get(i)
            if not data:
                continue
            is_correct = data["chosen"] == data["correct"]
            mark = "✅" if is_correct else "❌"

            txt_area.insert("end", f"{mark} Вопрос {i + 1}: {data['question']}\n")

            if not is_correct:
                txt_area.insert(
                    "end", f"   Вы выбрали: {data['text_chosen']}\n", "wrong"
                )
                txt_area.insert(
                    "end", f"   Правильно:  {data['text_correct']}\n", "right"
                )

            txt_area.insert("end", "-" * 50 + "\n")

        # Настройка цветов текста
        txt_area.tag_config("wrong", foreground="#ff5e57")
        txt_area.tag_config("right", foreground="#00d4aa")
        txt_area.configure(state="disabled")  # Чтобы нельзя было стереть результаты

    def clear_screen(self):
        """Очистка всех виджетов с экрана перед отрисовкой нового"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ExamApp()
    app.run()