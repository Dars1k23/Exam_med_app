import tkinter as tk
from tkinter import messagebox
import pandas as pd
import os

EXCEL_FILE = "questions.xlsx"


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
            print(f"✓ Загружено {len(df)} вопросов")
            return df
        except:
            return pd.DataFrame()

    def create_sample_data(self):
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
        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE, index=False, engine='openpyxl')
        print("✓ Создан файл questions.xlsx")

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

        title = tk.Label(header_frame, text="🎯 ЭКЗАМЕНАТОР",
                         font=("Arial", 36, "bold"), bg="#667eea", fg="white")
        title.pack(expand=True)

      
        card = tk.Frame(main_frame, bg="#2d2d44", bd=2, relief="ridge")
        card.pack(fill="both", expand=True, padx=50)
        card.grid_rowconfigure(3, weight=1)
        card.grid_columnconfigure(0, weight=1)

        
        tk.Label(card, text="👤 Имя студента:", font=("Arial", 18, "bold"),
                 bg="#2d2d44", fg="#e0e0e0").grid(row=0, column=0, pady=(40, 15), sticky="w", padx=40)

        self.name_entry = tk.Entry(card, font=("Arial", 16), width=30, bg="#40405a",
                                   fg="white", insertbackground="white", relief="flat")
        self.name_entry.grid(row=1, column=0, pady=10, sticky="ew", padx=40)
        self.name_entry.focus()

      
        tk.Label(card, text="📂 Выберите категорию:", font=("Arial", 18, "bold"),
                 bg="#2d2d44", fg="#e0e0e0").grid(row=2, column=0, pady=(30, 15), sticky="w", padx=40)

        cat_frame = tk.Frame(card, bg="#2d2d44")
        cat_frame.grid(row=3, column=0, pady=10, sticky="nsew", padx=40)

        self.category_var = tk.StringVar()
        categories = sorted(self.df["category"].dropna().unique())
        for i, cat in enumerate(categories):
            rb = tk.Radiobutton(cat_frame, text=f"  {cat}", variable=self.category_var,
                                value=cat, font=("Arial", 16),
                                bg="#2d2d44", fg="#e0e0e0", selectcolor="#40405a",
                                activebackground="#2d2d44", activeforeground="white",
                                width=40, anchor="w", pady=8)
            rb.grid(row=i, column=0, sticky="w")

        
        start_btn = tk.Button(card, text=" НАЧАТЬ ТЕСТ", font=("Arial", 18, "bold"),
                              bg="#00d4aa", fg="black", width=20, height=2,
                              relief="raised", bd=4, cursor="hand2",
                              activebackground="#00b894",
                              command=self.start_test)
        start_btn.grid(row=4, column=0, pady=40, padx=40, sticky="n")

        tk.Label(card, text="F11 - полноэкранный | ESC - выход",
                 font=("Arial", 10), bg="#2d2d44", fg="#888").grid(row=5, column=0, pady=10)

    def start_test(self):
        self.user_name = self.name_entry.get().strip()
        if not self.user_name:
            messagebox.showerror("Ошибка", "Введите имя!")
            return

        self.category = self.category_var.get()
        if not self.category:
            messagebox.showerror("Ошибка", "Выберите категорию!")
            return

        self.questions = self.df[self.df['category'] == self.category]
        if len(self.questions) == 0:
            self.questions = self.df

        self.current_question = 0
        self.score = 0
        self.total_questions = len(self.questions)
        print(f"🚀 Тест: {self.user_name} | {self.category} | {self.total_questions} вопросов")
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
            self.show_results()
            return

        
        top_panel = tk.Frame(main_frame, bg="#1a1a2e", height=70)
        top_panel.pack(fill="x", pady=(0, 20))
        top_panel.pack_propagate(False)

        tk.Label(top_panel, text=f"👤 {self.user_name}", font=("Arial", 14, "bold"),
                 bg="#1a1a2e", fg="#00d4aa").pack(side="left", padx=30, pady=15)
        tk.Label(top_panel, text=f"📚 {self.category}", font=("Arial", 14),
                 bg="#1a1a2e", fg="#e0e0e0").pack(side="left", padx=20, pady=15)
        tk.Label(top_panel, text=f"📖 {self.current_question + 1}/{self.total_questions}",
                 font=("Arial", 14, "bold"), bg="#1a1a2e", fg="#667eea").pack(side="right", padx=30, pady=15)

      
        question_card = tk.Frame(main_frame, bg="#2d2d44", bd=2, relief="ridge")
        question_card.pack(fill="both", expand=True, padx=50, pady=10)
        question_card.grid_rowconfigure(1, weight=1)
        question_card.grid_columnconfigure(0, weight=1)

        question_data = self.questions.iloc[self.current_question]

        tk.Label(question_card, text=f"Вопрос {self.current_question + 1}",
                 font=("Arial", 18, "bold"), bg="#2d2d44", fg="#667eea").grid(row=0, column=0, pady=(30, 20),
                                                                              sticky="n")

        question_label = tk.Label(question_card, text=question_data['Вопрос'],
                                  font=("Arial", 22, "bold"), bg="#2d2d44", fg="#ffffff",
                                  wraplength=800, justify="center")
        question_label.grid(row=1, column=0, padx=40, pady=20, sticky="nsew")

        
        options_frame = tk.Frame(question_card, bg="#2d2d44")
        options_frame.grid(row=2, column=0, pady=20, padx=40, sticky="nsew")

        self.answer_var = tk.StringVar()
        options = ['ВариантA', 'ВариантB', 'ВариантC', 'ВариантD']
        for i, opt in enumerate(options):
            text = question_data[opt]
            rb = tk.Radiobutton(options_frame, text=f"{chr(65 + i)}. {text}",
                                variable=self.answer_var, value=opt,  # value = 'ВариантA', 'ВариантB' и т.д.
                                font=("Arial", 16, "bold"), bg="#40405a", fg="#ffffff",
                                selectcolor="#667eea", anchor="w", pady=12, padx=20)
            rb.pack(fill="x")

      
        btn_frame = tk.Frame(main_frame, bg="#1e1e2e")
        btn_frame.pack(fill="x", pady=20)

        if self.current_question > 0:
            prev_btn = tk.Button(btn_frame, text="◀ Назад", font=("Arial", 16, "bold"),
                                 bg="#57606f", fg="black", width=14, height=2,
                                 command=self.prev_question)
            prev_btn.pack(side="left")

        next_btn = tk.Button(btn_frame, text="Следующий ▶", font=("Arial", 16, "bold"),
                             bg="#00d4aa", fg="black", width=16, height=2,
                             command=self.next_question)
        next_btn.pack(side="right")

    def next_question(self):
        if not self.answer_var.get():
            messagebox.showwarning("Внимание", "Выберите ответ!")
            return

        selected_column = self.answer_var.get()  # 'ВариантB'
        question_data = self.questions.iloc[self.current_question]


        selected_letter = selected_column[-1]  # Берем последнюю букву: 'B'
        correct_letter = question_data['Правильный']  # 'B'

        print(f"DEBUG: Выбрано: {selected_column} → {selected_letter} | Правильно: {correct_letter}")

        if selected_letter == correct_letter:
            self.score += 1
            print(f"✅ ПРАВИЛЬНО! Всего баллов: {self.score}")
        else:
            print(f"❌ НЕПРАВИЛЬНО (правильный: {correct_letter})")

        self.current_question += 1
        self.show_test_screen()

    def prev_question(self):
        self.current_question -= 1
        self.show_test_screen()

    def show_results(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.configure(bg="#1e1e2e")
        main_frame = tk.Frame(self.root, bg="#1e1e2e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        percent = (self.score / self.total_questions) * 100

        
        header_frame = tk.Frame(main_frame, bg="#667eea", height=150)
        header_frame.pack(fill="x", pady=(0, 30))
        header_frame.pack_propagate(False)

        tk.Label(header_frame, text="🏆 ВАШ РЕЗУЛЬТАТ", font=("Arial", 40, "bold"),
                 bg="#667eea", fg="white").pack(expand=True)

      
        score_card = tk.Frame(main_frame, bg="#2d2d44", bd=2, relief="ridge")
        score_card.pack(expand=True, padx=50, pady=20)
        score_card.grid_rowconfigure(4, weight=1)
        score_card.grid_columnconfigure(0, weight=1)

        tk.Label(score_card, text=self.user_name, font=("Arial", 24, "bold"),
                 bg="#2d2d44", fg="#00d4aa").grid(row=0, column=0, pady=20)
        tk.Label(score_card, text=self.category, font=("Arial", 20),
                 bg="#2d2d44", fg="#e0e0e0").grid(row=1, column=0, pady=10)

        score_label = tk.Label(score_card, text=f"{self.score}/{self.total_questions}",
                               font=("Arial", 72, "bold"), bg="#2d2d44", fg="#667eea")
        score_label.grid(row=2, column=0, pady=20)

        percent_label = tk.Label(score_card, text=f"{percent:.1f}%",
                                 font=("Arial", 32, "bold"), bg="#2d2d44", fg="#ffffff")
        percent_label.grid(row=3, column=0, pady=10)

      
        if percent >= 80:
            grade = "🎉 ОТЛИЧНО! 5"
            color = "#00d4aa"
        elif percent >= 60:
            grade = "👍 ХОРОШО! 4"
            color = "#f39c12"
        elif percent >= 40:
            grade = "📚 УДОВЛ. 3"
            color = "#f1c40f"
        else:
            grade = "🔄 ПОВТОРИТЬ! 2"
            color = "#e74c3c"

        tk.Label(score_card, text=grade, font=("Arial", 28, "bold"),
                 bg=color, fg="white", width=20, height=2).grid(row=4, column=0, pady=30, sticky="n")

        tk.Button(score_card, text="🔄 НОВЫЙ ТЕСТ", font=("Arial", 20, "bold"),
                  bg="#667eea", fg="black", width=18, height=2,
                  command=self.restart).grid(row=5, column=0, pady=30)

    def restart(self):
        self.show_start_screen()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = ExamApp()
    app.run()
