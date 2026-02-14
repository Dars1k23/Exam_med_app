import tkinter as tk
from tkinter import messagebox, ttk
import pandas as pd
import os
from datetime import datetime

EXCEL_FILE = "questions.xlsx"
RESULTS_FILE = "results.xlsx"

class ExamApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎓 Экзаменатор")
        self.root.geometry("1000x800")
        self.root.minsize(800, 600)
        self.root.configure(bg="#1e1e2e")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        self.root.bind('<F11>', self.toggle_fullscreen)
        self.root.bind('<Escape>', self.exit_fullscreen)

        self.df = self.load_questions()
        self.questions = None
        self.current_question = 0
        self.score = 0
        self.total_questions = 0
        self.category = ""
        self.user_name = ""
        self.is_fullscreen = False
        self.user_answers = {}
        self.wrong_questions = []

        self.show_start_screen()

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)

    def exit_fullscreen(self, event=None):
        self.is_fullscreen = False
        self.root.attributes('-fullscreen', False)

    def load_questions(self):
        if not os.path.exists(EXCEL_FILE):
            self.create_sample_data()
        try:
            df = pd.read_excel(EXCEL_FILE, engine='openpyxl')
            required_cols = ['category', 'Вопрос', 'ВариантA', 'ВариантB', 
                           'ВариантC', 'ВариантD', 'Правильный']
            if not all(col in df.columns for col in required_cols):
                raise ValueError("Неверная структура Excel файла")
            print(f"✓ Загружено {len(df)} вопросов")
            return df
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            messagebox.showerror("Ошибка", f"Не удается загрузить {EXCEL_FILE}\n{e}")
            return pd.DataFrame()

    def create_sample_data(self):
        data = {
            'category': ['Математика', 'Математика', 'Математика', 'Информатика', 'Информатика', 'Информатика',
                        'Программирование', 'Программирование', 'Программирование', 'Алгоритмы', 'Python', 'C++'],
            'Вопрос': ['2 + 2 = ?', '5 × 3 = ?', '√16 = ?', 'Что такое CPU?', 'Сколько бит в байте?',
                      'Основная память?', 'Что выведет print("Hello")?', 'Тип для целых чисел?',
                      'Сколько элементов в [1,2,3]?', 'Сложность поиска в массиве?', 
                      '"Hello" в Python?', 'int в C++?'],
            'ВариантA': ['3', '10', '2', 'Монитор', '4', 'Диск', '1', 'float', '2', 'O(1)', 'int', 'float'],
            'ВариантB': ['4', '15', '4', 'Процессор', '8', 'RAM', 'Hello', 'int', '3', 'O(n)', 'str', 'int'],
            'ВариантC': ['5', '20', '8', 'Клавиатура', '16', 'CPU', 'None', 'str', '4', 'O(log n)', 'list', 'char'],
            'ВариантD': ['6', '25', '16', 'Мышь', '32', 'Видеокарта', 'Error', 'list', '5', 'O(n²)', 'dict', 'double'],
            'Правильный': ['B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B', 'B']
        }
        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        print("✓ Создан файл questions.xlsx")

    def get_correct_letter(self, question_idx):
        return self.questions.iloc[question_idx]['Правильный']

    def update_score(self):
        """✅ Пересчитать ВСЕ вопросы: правильные, ошибки И пропуски"""
        self.wrong_questions = []
        self.score = 0
        
        for q_idx in range(self.total_questions):
            correct_letter = self.get_correct_letter(q_idx)
            
            if q_idx in self.user_answers:
                selected_letter = self.user_answers[q_idx][-1]
                if selected_letter != correct_letter:
                    question_text = self.questions.iloc[q_idx]['Вопрос']
                    self.wrong_questions.append({
                        '№': q_idx + 1,
                        'Вопрос': question_text,
                        'Выбран': selected_letter,
                        'Правильно': correct_letter,
                        'Статус': 'Ошибка'
                    })
                else:
                    self.score += 1
            else:
                question_text = self.questions.iloc[q_idx]['Вопрос']
                self.wrong_questions.append({
                    '№': q_idx + 1,
                    'Вопрос': question_text,
                    'Выбран': 'НЕ ОТВЕЧЕН',
                    'Правильно': correct_letter,
                    'Статус': 'Пропуск'
                })

    def save_result_to_excel(self):
        """💾 ПОЛНЫЙ отчет: результат + ВСЕ ошибки/пропуски"""
        try:
            percent = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
            
            results_data = [{
                'Имя': self.user_name,
                'Категория': self.category,
                'Всего вопросов': self.total_questions,
                'Правильных': self.score,
                'Ошибок': len([e for e in self.wrong_questions if e['Статус'] == 'Ошибка']),
                'Пропусков': len([e for e in self.wrong_questions if e['Статус'] == 'Пропуск']),
                'Процент': f"{percent:.1f}%",
                'Дата': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')
            }]
            
            detail_file = f"отчет_{self.user_name}_{self.category}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M')}.xlsx"
            
            with pd.ExcelWriter(detail_file, engine='openpyxl') as writer:
                results_df = pd.DataFrame(results_data)
                results_df.to_excel(writer, sheet_name='📊 Результат', index=False)
                
                if self.wrong_questions:
                    errors_df = pd.DataFrame(self.wrong_questions)
                    errors_df.to_excel(writer, sheet_name='❌ Ошибки и пропуски', index=False)
                else:
                    pd.DataFrame([{'Сообщение': 'Все ответы правильные!'}]).to_excel(writer, sheet_name='✅ Идеально!', index=False)
            
            print(f"✅ ПОЛНЫЙ отчет: {detail_file}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения: {e}")

    def save_results_to_general_sheet(self):
        """💾 КРАТКИЙ отчет в общую ведомость results.xlsx"""
        try:
            percent = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0
            timestamp = datetime.now().strftime('%d.%m.%Y %H:%M:%S')
            
            general_data = [{
                'Имя': self.user_name,
                'Категория': self.category,
                'Вопросов': self.total_questions,
                'Правильных': self.score,
                'Процент': f"{percent:.1f}%",
                'Дата и время': timestamp
            }]
            
            if os.path.exists(RESULTS_FILE):
                existing_df = pd.read_excel(RESULTS_FILE, engine='openpyxl')
                new_df = pd.concat([existing_df, pd.DataFrame(general_data)], ignore_index=True)
            else:
                new_df = pd.DataFrame(general_data)
            
            new_df.to_excel(RESULTS_FILE, index=False, engine='openpyxl')
            print(f"✅ Сохранено в {RESULTS_FILE}")
            
        except Exception as e:
            print(f"❌ Ошибка сохранения в общую ведомость: {e}")

    def show_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1e1e2e")
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        header_frame = tk.Frame(main_frame, bg="#667eea", height=200)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        title = tk.Label(header_frame, text="🎯 ЭКЗАМЕНАТОР", font=("Arial", 36, "bold"), bg="#667eea", fg="white")
        title.pack(expand=True)

        card = tk.Frame(main_frame, bg="#2d2d44", bd=2, relief="ridge")
        card.pack(fill="both", expand=True, padx=50)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        tk.Label(card, text="👤 Имя студента:", font=("Arial", 18, "bold"), bg="#2d2d44", fg="#e0e0e0").grid(row=0, column=0, pady=(40, 15), sticky="w", padx=40)

        self.name_entry = tk.Entry(card, font=("Arial", 16), width=30, bg="#40405a", fg="white", insertbackground="white", relief="flat")
        self.name_entry.grid(row=1, column=0, pady=10, sticky="ew", padx=40)
        self.name_entry.focus()

        tk.Label(card, text="📂 Выберите категорию:", font=("Arial", 18, "bold"), bg="#2d2d44", fg="#e0e0e0").grid(row=2, column=0, pady=(30, 15), sticky="w", padx=40)

        cat_frame = tk.Frame(card, bg="#2d2d44")
        cat_frame.grid(row=3, column=0, pady=10, sticky="nsew", padx=40)
        cat_frame.grid_rowconfigure(0, weight=1)
        cat_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(cat_frame, bg="#2d2d44", highlightthickness=0)
        scrollbar = tk.Scrollbar(cat_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#2d2d44")

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        self.category_var = tk.StringVar()
        categories = sorted(self.df["category"].dropna().unique())
        print(f"DEBUG: Найдено категорий: {len(categories)} = {categories}")

        for i, cat in enumerate(categories):
            rb = tk.Radiobutton(self.scrollable_frame, text=f"  {cat}", variable=self.category_var, value=cat, 
                               font=("Arial", 16), bg="#2d2d44", fg="#e0e0e0", selectcolor="#40405a",
                               activebackground="#2d2d44", activeforeground="white", width=40, anchor="w", pady=8)
            rb.grid(row=i, column=0, sticky="w")

        def on_enter(e): e.widget.config(bg="#00b894")
        def on_leave(e): e.widget.config(bg="#00d4aa")
        
        start_btn = tk.Button(card, text=" НАЧАТЬ ТЕСТ", font=("Arial", 18, "bold"), bg="#00d4aa", fg="black", 
                             width=20, height=2, relief="raised", bd=4, cursor="hand2", command=self.start_test)
        start_btn.grid(row=4, column=0, pady=40, padx=40, sticky="n")
        start_btn.bind("<Enter>", on_enter)
        start_btn.bind("<Leave>", on_leave)

        tk.Label(card, text="F11 - полноэкранный | ESC - выход | Колесико мыши - скролл", font=("Arial", 10), bg="#2d2d44", fg="#888").grid(row=5, column=0, pady=10)

    def start_test(self):
        self.user_name = self.name_entry.get().strip() or "Аноним"
        self.category = self.category_var.get()
        
        if not self.category:
            messagebox.showwarning("Предупреждение", "Выберите категорию!")
            return

        self.questions = self.df[self.df['category'] == self.category].reset_index(drop=True)
        self.current_question = 0
        self.score = 0
        self.total_questions = len(self.questions)
        self.user_answers = {}
        self.wrong_questions = []
        
        self.show_test_screen()

    def show_test_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1e1e2e")
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        if self.current_question >= self.total_questions:
            self.update_score()
            self.show_results()
            return

        # Header
        top_panel = tk.Frame(main_frame, bg="#1a1a2e", height=70)
        top_panel.pack(fill="x", pady=(0, 20))
        top_panel.pack_propagate(False)

        tk.Label(top_panel, text=f"👤 {self.user_name}", font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#00d4aa").pack(side="left", padx=30, pady=15)
        tk.Label(top_panel, text=f"📚 {self.category}", font=("Arial", 14), bg="#1a1a2e", fg="#e0e0e0").pack(side="left", padx=20, pady=15)
        
        progress = ttk.Progressbar(top_panel, length=200, mode='determinate')
        progress['maximum'] = self.total_questions
        progress['value'] = self.current_question + 1
        progress.pack(side="right", padx=10, pady=15)
        
        tk.Label(top_panel, text=f"{self.current_question + 1}/{self.total_questions}", font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#667eea").pack(side="right", padx=10, pady=15)

        # Question card
        question_card = tk.Frame(main_frame, bg="#2d2d44", bd=2, relief="ridge")
        question_card.pack(fill="both", expand=True, padx=50, pady=10)
        question_card.grid_rowconfigure(1, weight=1)
        question_card.grid_columnconfigure(0, weight=1)

        question_data = self.questions.iloc[self.current_question]
        tk.Label(question_card, text=f"Вопрос {self.current_question + 1}", font=("Arial", 18, "bold"), bg="#2d2d44", fg="#667eea").grid(row=0, column=0, pady=(30, 20), sticky="n")

        question_label = tk.Label(question_card, text=question_data['Вопрос'], font=("Arial", 22, "bold"), bg="#2d2d44", fg="#ffffff", wraplength=800, justify="center")
        question_label.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")

        # Options
        options_frame = tk.Frame(question_card, bg="#2d2d44")
        options_frame.grid(row=2, column=0, pady=20, padx=40, sticky="nsew")

        self.answer_var = tk.StringVar()
        if self.current_question in self.user_answers:
            self.answer_var.set(self.user_answers[self.current_question])
            
        options = ['ВариантA', 'ВариантB', 'ВариантC', 'ВариантD']
        for i, opt in enumerate(options):
            text = question_data[opt]
            rb = tk.Radiobutton(options_frame, text=f"{chr(65 + i)}. {text}",
                                variable=self.answer_var, value=opt,
                                font=("Arial", 16, "bold"), bg="#40405a", fg="#ffffff",
                                selectcolor="#667eea", anchor="w", pady=12, padx=20)
            rb.pack(fill="x")

        # Navigation buttons
        def on_enter(e): e.widget.config(bg="#57606f")
        def on_leave(e): e.widget.config(bg="#57606f")
        def btn_enter(e): e.widget.config(bg="#00b894")
        def btn_leave(e): e.widget.config(bg="#00d4aa")
        
        btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=20)

        if self.current_question > 0:
            prev_btn = tk.Button(btn_frame, text="◀ Назад", font=("Arial", 16, "bold"),
                                 bg="#57606f", fg="white", width=14, height=2,
                                 command=self.prev_question)
            prev_btn.pack(side="left")
            prev_btn.bind("<Enter>", on_enter)
            prev_btn.bind("<Leave>", on_leave)

        finish_btn = tk.Button(btn_frame, text="✅ ЗАВЕРШИТЬ ТЕСТ", font=("Arial", 16, "bold"),
                              bg="#00d4aa", fg="black", width=20, height=2,
                              command=self.finish_test)
        finish_btn.pack(side="right", padx=10)
        finish_btn.bind("<Enter>", btn_enter)
        finish_btn.bind("<Leave>", btn_leave)

        if self.current_question < self.total_questions - 1:
            next_btn = tk.Button(btn_frame, text="Следующий ▶", font=("Arial", 16, "bold"),
                                bg="#00d4aa", fg="black", width=16, height=2,
                                command=self.next_question)
            next_btn.pack(side="right")
            next_btn.bind("<Enter>", btn_enter)
            next_btn.bind("<Leave>", btn_leave)

    def next_question(self):
        if not self.answer_var.get():
            messagebox.showinfo("Информация", "Выберите ответ перед переходом!")
            return

        self.user_answers[self.current_question] = self.answer_var.get()
        self.current_question += 1
        self.show_test_screen()

    def prev_question(self):
        self.current_question -= 1
        self.show_test_screen()

    def finish_test(self):
        self.user_answers[self.current_question] = self.answer_var.get()
        self.update_score()
        self.save_result_to_excel()
        self.save_results_to_general_sheet()
        self.show_results()

    def show_results(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1e1e2e")
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        percent = (self.score / self.total_questions) * 100 if self.total_questions > 0 else 0

        header_frame = tk.Frame(main_frame, bg="#667eea", height=150)
        header_frame.pack(fill="x", pady=(0, 30))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🏆 ВАШ РЕЗУЛЬТАТ", font=("Arial", 40, "bold"), bg="#667eea", fg="white").pack(expand=True)

        score_card = tk.Frame(main_frame, bg="#2d2d44", bd=2, relief="ridge")
        score_card.pack(expand=True, padx=50, pady=20)
        score_card.grid_rowconfigure(2, weight=1)
        score_card.grid_columnconfigure(0, weight=1)

        tk.Label(score_card, text=self.user_name, font=("Arial", 24, "bold"), bg="#2d2d44", fg="#00d4aa").grid(row=0, column=0, pady=20)
        tk.Label(score_card, text=self.category, font=("Arial", 20), bg="#2d2d44", fg="#e0e0e0").grid(row=1, column=0, pady=10)

        score_label = tk.Label(score_card, text=f"{self.score}/{self.total_questions}", font=("Arial", 72, "bold"), bg="#2d2d44", fg="#667eea")
        score_label.grid(row=2, column=0, pady=20)

        percent_label = tk.Label(score_card, text=f"{percent:.1f}%", font=("Arial", 72, "bold"), bg="#2d2d44", fg="#ffffff")
        percent_label.grid(row=3, column=0, pady=20)

        def on_enter(e): e.widget.config(bg="#5a67d8")
        def on_leave(e): e.widget.config(bg="#667eea")
        
        restart_btn = tk.Button(score_card, text="🔄 НОВЫЙ ТЕСТ", font=("Arial", 20, "bold"),
                               bg="#667eea", fg="black", width=18, height=2,
                               command=self.restart)
        restart_btn.grid(row=4, column=0, pady=30)
        restart_btn.bind("<Enter>", on_enter)
        restart_btn.bind("<Leave>", on_leave)

    def restart(self):
        self.show_start_screen()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = ExamApp()
    app.run()

