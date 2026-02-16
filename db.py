import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

import config
import seeder
import logs

class DB:
    def __init__(self):
        seeder.create_sample_data()

        self.df = pd.DataFrame()


    def load_questions(self):
        """Загружает вопросы """

        try:
            # Читаем Excel через pandas
            self.df = pd.read_excel(config.QUESTIONS_FILE, engine="openpyxl")
            logs.log.write(f"База загружена: {len(self.df)} строк", logs.Status.OK)

        except Exception as e:
            logs.log.write(f"Ошибка при чтении Excel: {e}", logs.Status.CRITICAL_ERROR)
            # messagebox.showerror("Критическая ошибка", f"Ошибка при чтении Excel: {e}")