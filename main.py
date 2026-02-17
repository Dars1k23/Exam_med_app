import tkinter as tk
from tkinter import messagebox, ttk
from fpdf import FPDF
import pandas as pd
import os
from datetime import datetime

import config

class ExamApp:

    # --- ЛОГИКА РАБОТЫ С ДАННЫМИ (BACKEND) ---

    

    

    # --- ИНТЕРФЕЙС (FRONTEND) ---

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

    

    # --- СЛУЖЕБНЫЕ МЕТОДЫ ---
    

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
    
    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ExamApp()
    app.run()