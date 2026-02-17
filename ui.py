import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime
import re

import db

class UI:
    def __init__(self, question_count):
        """Инициализация приложения: создание окна и загрузка данных"""
        self.root = tk.Tk()
        self.root.title("🎓 MedExam v1.0")
        self.root.geometry("1000x800")
        self.root.configure(bg="#1e1e2e")  # Темная тема (VS Code style)

        # Растягиваем сетку окна, чтобы элементы центрировались
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Переменные состояния (хранят данные текущей сессии)
        self.question_count = question_count # количество вопросов
        self.questions = None  # Вопросы выбранной категории
        self.current_question = 0  # Индекс текущего вопроса
        self.user_answers = {}  # Словарь ответов: {индекс: "ВариантA"}
        self.nav_buttons = {}
        self.answer_buttons = {}
        self.visited_questions = ( # ----------------------------------нужно сделать так чтобы сдесь были отвеченные вопросы
            set()
        )  # Для отслеживания, какие вопросы уже открывали (для подсветки в навигашке)

        self.name_label = None # Поле в котором хранится имя студента
        self.category_label = None # Поле в котором хранится категория теста
        self.nav_grid_label = None # Поле в котором хранится сетка для nav buttons
        self.question_label_var = None  # Для текста "Вопрос X / Y"
        self.question_text_widget = None # Поле для widget
        self.ans_var = None # Поле в котором хранится выбранные ответ на открытый вопрос

        self.user_name = "" # ФИО студента
        self.category = "" # Категория теста

        self.btn_prev = None # Кнопка перехода на предыдущий вопрос
        self.btn_next = None # Кнопка перехода на следующий вопрос

        self.show_start_screen()
    

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
        self.name_label = tk.Entry(container, font=("Arial", 14), width=30)
        self.name_label.pack(pady=10)

        # Список категорий из Excel
        tk.Label(container, text="Выберите предмет:", bg="#2d2d44", fg="white").pack()
        self.category_label = tk.StringVar()
        categories = sorted(db.db.df["category"].unique().tolist())

        cat_combo = ttk.Combobox(
            container, textvariable=self.category_label, values=categories, state="readonly"
        )
        cat_combo.pack(pady=10, fill="x")

        # Кнопка старта
        tk.Button(
            container,
            text="НАЧАТЬ",
            bg="#667eea",
            fg="white",
            font=("Arial", 12, "bold"),
            command=self.start_test,
        ).pack(pady=20)

    def start_test(self):
        """Подготовка данных перед началом теста с проверкой ФИО"""
        # Убираем лишние пробелы по краям
        self.user_name = self.name_label.get().strip()
        self.category = self.category_label.get()

        # Проверка на пустое имя (или если ввели только пробелы)
        if not self.validate_fio():
            messagebox.showwarning(
                "Доступ запрещен",
                "Пожалуйста, введите ваше полное ФИО для идентификации в отчете!",
            )
            return

        # Проверка на выбор категории
        if not self.category:
            messagebox.showwarning("Внимание", "Выберите предмет экзамена!")
            return

        # Если проверки пройдены — сохраняем категорию и грузим вопросы
        self.questions = db.db.generate_questions(self.category, count=self.question_count)

        # Проверка, есть ли вопросы в этой категории вообще
        if self.questions.empty:
            messagebox.showerror(
                "Ошибка базы", f"В категории '{self.category}' нет вопросов!"
            )
            return

        self.init_test_screen()

    def init_test_screen(self):
        """Создание окружения для выполнения теста"""
        self.clear_screen()
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

        self.nav_grid_label = tk.Frame(nav_frame, bg="#2d2d44")
        self.nav_grid_label.pack(padx=10)
        self.init_nav_buttons()

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
            controls, 
            text="<< Назад", 
            command=self.prev_question, 
            width=12,
            font=("Arial", 11, "bold"),
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

    def clear_screen(self):
        """Очистка всех виджетов с экрана перед отрисовкой нового"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def get_score(self):
        """Возвращает количество верных ответов"""
        return sum(
            1 for a in self.user_answers.values() if a["chosen"] == a["correct"]
        )
    
    def validate_fio(self):
        pattern = r'^[А-ЯЁ][а-яё\-\']{1,}[а-яё]*\s+[А-ЯЁ][а-яё\-\']{1,}[а-яё]*(?:\s+[А-ЯЁ][а-яё\-\']{1,}[а-яё]*){0,2}$'

        return bool(re.match(pattern, self.user_name))

ui = UI(question_count=10)
