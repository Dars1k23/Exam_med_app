import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

import db

class UI:
    def __init__(self, databas: db.DB):
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
