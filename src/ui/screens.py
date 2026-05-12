from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, 
                             QMessageBox, QScrollArea, QCheckBox, QRadioButton, QButtonGroup, QGridLayout, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import datetime

from src.config import REPORTS_DIR, TIME_FOR_EXAM
from src.core import load_questions, save_result_to_excel
from src.db_paths import get_db_paths
from src.utils import ProctorThread, WebcamThread, generate_pdf, get_number_of_test
from src.ui.widgets import ActionButton, SuccessButton, DangerButton,SkipButton, QuestionCard, AppTitle, SectionTitle, IconLabel

import re

import os
import json
from pathlib import Path

# --- ЭКРАН 1: ФИО ---
class NameScreen(QWidget):
    next_step = pyqtSignal(str)
    go_validator = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        layout.addWidget(IconLabel("👤"))
        layout.addWidget(AppTitle("Вход в систему"))
        
        sub = QLabel("Шаг 1: Введите ваше ФИО")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QuestionCard()
        card.add_widget(SectionTitle("ФИО СТУДЕНТА"))
        self.inp = QLineEdit()
        self.inp.setPlaceholderText("Иванов Иван Иванович")
        self.inp.returnPressed.connect(self._start)
        card.add_widget(self.inp)
        layout.addWidget(card)

        btn_row = QHBoxLayout()
        s_btn = ActionButton("Далее →")
        s_btn.clicked.connect(self._start)
        btn_row.addWidget(s_btn)
        layout.addLayout(btn_row)

        warn = QLabel("🎥 Прокторинг: скриншоты каждые 30 сек, веб-камера каждую минуту")
        warn.setStyleSheet("color: #718096; font-size: 12px; margin-top: 20px;")
        warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warn)
        layout.addStretch()

        val_btn = QPushButton("Валидация")
        val_btn.setStyleSheet("color: #718096; background: transparent; border: none; text-decoration: underline;")
        val_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        val_btn.clicked.connect(self.go_validator.emit)
        layout.addWidget(val_btn, alignment=Qt.AlignmentFlag.AlignRight)

    def _start(self):
        if self._validate_fio(self.inp.text().strip()):
            self.next_step.emit(self.inp.text().strip())
        else:
            self.inp.setStyleSheet("border: 2px solid #FC8181;")

    def _validate_fio(self, user_name):
        pattern = r'^[А-ЯЁ][а-яё\-\']{1,}[а-яё]*\s+[А-ЯЁ][а-яё\-\']{1,}[а-яё]*(?:\s+[А-ЯЁ][а-яё\-\']{1,}[а-яё]*){0,2}$'

        return bool(re.match(pattern, user_name))


# --- ЭКРАН 2: ВЫБОР БАЗЫ ДАННЫХ ---
class DatabaseScreen(QWidget):
    start_test = pyqtSignal(str)
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        layout.addWidget(IconLabel("⚕", "#3182CE"))
        layout.addWidget(AppTitle("Medical Test System"))
        
        sub = QLabel("Шаг 2: Выберите базу данных для экзамена")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QuestionCard()
        card.add_widget(SectionTitle("БАЗА ДАННЫХ"))
        
        self.combo = QComboBox()
        self.combo.addItem("Выберите базу данных...", "")
        
        db_list = get_db_paths("dataBasePath.txt")
        if isinstance(db_list, dict):
            for name, path in db_list.items():
                self.combo.addItem(name, path)
        else:
            for item in db_list:
                if ":" in item:
                    name, path = item.split(":", 1)
                    self.combo.addItem(name, path)
            
        card.add_widget(self.combo)
        
        layout.addWidget(card)

        btn_row = QHBoxLayout()
        b_btn = ActionButton("← Назад")
        b_btn.clicked.connect(self.back.emit)
        btn_row.addWidget(b_btn)
        
        self.s_btn = SuccessButton("▶ Начать тест")
        self.s_btn.setEnabled(False)
        self.s_btn.clicked.connect(lambda: self.start_test.emit(self.combo.currentData() or ""))
        
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        
        btn_row.addWidget(self.s_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def _on_combo_changed(self):
        if self.combo.currentData():
            self.s_btn.setEnabled(True)
        else:
            self.s_btn.setEnabled(False)

from src.kr_mapper import map_kr_to_rows

# --- ЭКРАН 3: ВЫБОР КР ---
class KRScreen(QWidget):
    start_test = pyqtSignal(str)
    back = pyqtSignal()

    def __init__(self, db_path):
        super().__init__()
        self.db_path = db_path
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        layout.addWidget(IconLabel("⚕", "#3182CE"))
        layout.addWidget(AppTitle("Medical Test System"))
        
        sub = QLabel("Шаг 3: Выберите КР для экзамена")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QuestionCard()
        card.add_widget(SectionTitle("КЛИНИЧЕСКИЕ РЕКОМЕНДАЦИИ"))
        
        self.combo = QComboBox()
        self.combo.addItem("Выберите КР...", "")
        
        kr_mapping = map_kr_to_rows(db_path)
        for kr_name, rows in kr_mapping.items():
            self.combo.addItem(f"{kr_name} ({len(rows)} вопросов)", kr_name)
            
        card.add_widget(self.combo)
        
        layout.addWidget(card)

        btn_row = QHBoxLayout()
        b_btn = ActionButton("← Назад")
        b_btn.clicked.connect(self.back.emit)
        btn_row.addWidget(b_btn)
        
        self.s_btn = SuccessButton("▶ Начать тест")
        self.s_btn.setEnabled(False)
        self.s_btn.clicked.connect(lambda: self.start_test.emit(self.combo.currentData() or ""))
        
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        
        btn_row.addWidget(self.s_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def _on_combo_changed(self):
        if self.combo.currentData():
            self.s_btn.setEnabled(True)
        else:
            self.s_btn.setEnabled(False)

# --- ЭКРАН 4: ТЕСТ (Сложная верстка с панелью) ---
class TestScreen(QWidget):
    finished = pyqtSignal(dict)

    def __init__(self, student, db_path, kr_name):
        super().__init__()
        self.student = student
        self.db_path = db_path
        self.kr_name = kr_name
        self.kr = kr_name if kr_name else (os.path.basename(db_path) if db_path else "Unknown DB")
        self.questions = load_questions(db_path, kr_name=kr_name)
        self.answers = {}
        self.skipped = set()
        self.current_idx = 0
        self.widgets = [] # Инициализируем сразу! (Fix AttributeError)
        self.nav_buttons = []
        self.data_for_tmp = { "start_exams": 0, "answers": {}}
        
        
        # Основной Layout
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        
        # === ЛЕВАЯ ПАНЕЛЬ (Навигация) ===
        nav_panel = QWidget()
        nav_panel.setObjectName("nav_panel")
        nav_panel.setFixedWidth(260)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(14, 16, 14, 16)
        
        nav_layout.addWidget(SectionTitle("НАВИГАЦИЯ"))
        
        nav_layout.addSpacing(5)
        

        nav_container = QWidget()
        nav_container.setObjectName("nav_grid_container")  
        
        # Настройка лейаута для отступов внутри контейнера
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)         # Чуть больше воздуха между кнопками
        grid_layout.setContentsMargins(12, 12, 12, 12) # Отступы от краев рамки
        
        total = len(self.questions)
        for i in range(total):
            btn = QPushButton(str(i + 1))
            btn.setObjectName("nav_btn_empty")
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._load_q(idx))
            grid_layout.addWidget(btn, i // 7, i % 7) # 7 в ряд
            self.nav_buttons.append(btn)
            
        nav_container.setLayout(grid_layout)
        nav_layout.addWidget(nav_container)        
        nav_layout.addStretch()
        
        self.timer_lbl = QLabel("00:00")
        self.timer_lbl.setObjectName("timer_label") # Подключаем стиль из QSS
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_lbl.setFixedSize(120, 50) # Фиксируем размер, чтобы не прыгал
        
        # Можно добавить иконку часов, если хочется (через Unicode)
        # self.timer_lbl.setText("⏱ 00:00") 
        
        # Центрируем виджет таймера в панели
        timer_container = QWidget()
        timer_container.setStyleSheet("background-color: #161B27;")
        tl = QVBoxLayout(timer_container)
        tl.addWidget(self.timer_lbl)
        tl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(timer_container)
        
        self.proc_lbl = QLabel("● Прокторинг активен")
        self.proc_lbl.setStyleSheet("color: #68D391; font-size: 11px; background-color: #161B27;")
        nav_layout.addWidget(self.proc_lbl)

        root.addWidget(nav_panel)
        
        # === ЦЕНТРАЛЬНАЯ ЧАСТЬ ===
        center = QWidget()
        c_layout = QVBoxLayout(center)
        c_layout.setContentsMargins(32, 28, 32, 28)
        
        self.prog_lbl = QLabel()
        self.prog_lbl.setStyleSheet("color: #A0AEC0; font-size: 13px;")
        c_layout.addWidget(self.prog_lbl)
        
        # Карточка вопроса
        self.q_card = QuestionCard()
        self.q_lbl = QLabel()
        self.q_lbl.setObjectName("question_label")
        self.q_lbl.setWordWrap(True)
        self.q_card.add_widget(self.q_lbl)
        
        self.opt_container = QWidget()
        self.opt_layout = QVBoxLayout(self.opt_container)
        self.opt_layout.setContentsMargins(0,10,0,0)
        self.opt_container.setObjectName("question_layout")
        self.q_card.add_widget(self.opt_container)
        
        c_layout.addWidget(self.q_card)
        c_layout.addStretch()

         # Кнопки внизу
        nav_btns = QHBoxLayout()
        nav_btns.setSpacing(15) # Расстояние между кнопками
        
        # Левая группа (Назад + Пропустить)
        self.btn_back = ActionButton("← Назад")
        self.btn_back.clicked.connect(self._back)
        nav_btns.addWidget(self.btn_back)
        
        self.btn_skip = SkipButton("Пропустить")
        self.btn_skip.clicked.connect(self._skip)
        nav_btns.addWidget(self.btn_skip)
        
        nav_btns.addStretch() # Распорка посередине
        
        # Правая группа (Вперед / Завершить)
        self.btn_next = ActionButton("Вперёд →")
        self.btn_next.clicked.connect(self._next)
        nav_btns.addWidget(self.btn_next)
        
        self.btn_finish = SuccessButton("✓ Завершить")
        self.btn_finish.clicked.connect(self._finish_confirm)
        nav_btns.addWidget(self.btn_finish)
        self.btn_finish.hide()
        
        c_layout.addLayout(nav_btns)
        root.addWidget(center)
        
        

        # Логика

        # Используем название БД и КР для сохранения временных файлов
        import re
        db_name = os.path.basename(self.db_path).replace('.xlsx', '') if self.db_path else "Unknown_DB"
        safe_db_name = re.sub(r'[\\/*?:"<>|]', "_", db_name)
        safe_kr_name = re.sub(r'[\\/*?:"<>|]', "_", self.kr)
        self.test_dir_name = Path(f"{safe_db_name}_{safe_kr_name}")
        
        tmp_path = REPORTS_DIR / self.student / self.test_dir_name / "tmp.txt"
        if os.path.exists(tmp_path):
            self._read_tmp_file()
            self.start_time = datetime.datetime.fromtimestamp(self.data_for_tmp["start_exams"])
            self.answers = self.data_for_tmp.get("answers", {})
        else:
            self.start_time = datetime.datetime.now()
            self.data_for_tmp["start_exams"] = self.start_time.timestamp()

            os.makedirs(REPORTS_DIR / self.student / self.test_dir_name, exist_ok=True)

            self._update_tmp_file()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_timer)
        self.timer.start(1000)
        

        self.proc_thread = ProctorThread(student, self.test_dir_name)
        self.cam_thread = WebcamThread(student, self.test_dir_name)
        self.proc_thread.screenshot_taken.connect(lambda p: self.proc_lbl.setText(f"● {p.split('/')[-1]}"))
        self.proc_thread.start()
        self.cam_thread.start()
        
        self._load_q(0)

    def _update_tmp_file(self):
        with open(REPORTS_DIR  / self.student / self.test_dir_name / "tmp.txt", "w") as f:
            f.write(json.dumps(self.data_for_tmp))
            
            f.close()
    
    def _read_tmp_file(self):
        with open(REPORTS_DIR  / self.student / self.test_dir_name / "tmp.txt", "r") as f:
            self.data_for_tmp = json.loads(f.read())
            self.data_for_tmp["answers"] = { int(k):self.data_for_tmp["answers"][k] for k in self.data_for_tmp["answers"]}
            f.close()

    def _update_timer(self):
        delta =self.start_time + datetime.timedelta(seconds=TIME_FOR_EXAM) -  datetime.datetime.now() 
        seconds = delta.seconds

        if delta.total_seconds() < 0:
            self._finish_confirm(False)

        m, s = divmod(seconds, 60)
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")

    def _update_nav(self):
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_idx:
                btn.setObjectName("nav_btn_active")
            elif i in self.answers:
                btn.setObjectName("nav_btn_answered")
            elif i in self.skipped:
                btn.setObjectName("nav_btn_skipped")
            else:
                btn.setObjectName("nav_btn_empty")
            btn.setStyle(btn.style()) # Обновляем стиль

    def _load_q(self, idx):
        self._save_ans()
        if not (0 <= idx < len(self.questions)): return
        
        self.current_idx = idx
        q = self.questions[idx]
        
        self.prog_lbl.setText(f"Вопрос {idx+1} из {len(self.questions)}")
        self.q_lbl.setText(f"<b>{q['question']}</b>")
        
        # Очистка
        while self.opt_layout.count():
            item = self.opt_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        import textwrap
        self.widgets = []
        if q['type'] == 'multiple':
            for k, v in q['options'].items():
                wrapped_text = textwrap.fill(f"{k.upper()})  {v}", width=90)
                cb = QCheckBox(wrapped_text)
                cb.stateChanged.connect(self._save_ans)
                self.opt_layout.addWidget(cb)
                self.widgets.append((k, cb))
                if idx in self.answers and k in self.answers[idx].split(','):
                    cb.setChecked(True)
        else:
            self.bg = QButtonGroup(self) # Важно сохранить ссылку
            for k, v in q['options'].items():
                wrapped_text = textwrap.fill(f"{k.upper()})  {v}", width=90)
                rb = QRadioButton(wrapped_text)
                rb.toggled.connect(self._save_ans)

                self.bg.addButton(rb)
                self.opt_layout.addWidget(rb)
                self.widgets.append((k, rb))
                if idx in self.answers and self.answers[idx] == k:
                    rb.setChecked(True)
        
        self._update_nav()
        
        # Кнопки
        is_first = (idx == 0)
        self.btn_back.setEnabled(not is_first)
        is_last = (idx == len(self.questions) - 1)
        self.btn_next.setEnabled(not is_last)
        self.btn_finish.setVisible(True) # Всегда даем возможность завершить

    def _save_ans(self):
        # Проверка на существование self.widgets (для первого вызова)
        if not hasattr(self, 'widgets') or not self.widgets:
            return

        q = self.questions[self.current_idx]
        if q['type'] == 'multiple':
            selected = [k for k, w in self.widgets if w.isChecked()]
            if selected: 
                self.answers[self.current_idx] = ",".join(sorted(selected))
                self.skipped.discard(self.current_idx)
                self.data_for_tmp["answers"] = self.answers
                self._update_tmp_file()
        else:
            for k, w in self.widgets:
                if w.isChecked():
                    self.answers[self.current_idx] = k
                    self.skipped.discard(self.current_idx)
                    self.data_for_tmp["answers"] = self.answers
                    self._update_tmp_file()
                    break

    def _next(self): self._load_q(self.current_idx + 1)
    def _back(self): self._load_q(self.current_idx - 1)
    def _skip(self): 
        self.skipped.add(self.current_idx)
        self._next()

    def _finish_confirm(self, ask = True):
        self._save_ans()
        end = False
        if ask:
            reply = QMessageBox.question(self, "Завершение", 
                                        f"Отвечено: {len(self.answers)}/{len(self.questions)}\nЗавершить тест?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                end = True
        else:
            end = True
        
        if end:
            tmp_path = REPORTS_DIR / self.student / self.test_dir_name / "tmp.txt"
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            self._stop_threads()
            self.timer.stop()
            self.finished.emit({
                "student": self.student, "kr": self.kr,
                "questions": self.questions, "answers": self.answers,
                "elapsed": (datetime.datetime.now() - self.start_time).seconds if (datetime.datetime.now() - self.start_time).seconds < TIME_FOR_EXAM  else TIME_FOR_EXAM,
                "test_dir_name": self.test_dir_name,
                "db_path": self.db_path
            })

    def _stop_threads(self):
        if self.proc_thread.isRunning(): self.proc_thread.stop()
        if self.cam_thread.isRunning(): self.cam_thread.stop()
        
    def closeEvent(self, event):
        self._stop_threads()
        super().closeEvent(event)

# --- ЭКРАН 4: РЕЗУЛЬТАТЫ ---
class ResultScreen(QWidget):
    logout = pyqtSignal()
    
    def __init__(self, data):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        score = 0
        total = len(data['questions'])
        for i, q in enumerate(data['questions']):
            u_raw = data['answers'].get(i, "")
            c_raw = q['correct']
            if set(u_raw.split(',')) == set(c_raw.split(',')) and u_raw:
                score += 1
                
        percent = int(score/total*100) if total else 0
        save_result_to_excel(data['student'], score, len(data['answers']), total, data['kr'], data["elapsed"])
        
        db_name = os.path.basename(data.get('db_path', '')).replace('.xlsx', '')
        generate_pdf(data['student'], data["test_dir_name"], data['kr'], data['questions'], data['answers'], score, total, data["elapsed"], db_name)
                
        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(48, 32, 48, 32)
        c_layout.setSpacing(20)
        
        # Карточка итога
        top_card = QuestionCard()
        score_lbl = QLabel(f"{percent}%")
        score_lbl.setStyleSheet(f"font-size: 72px; font-weight: 800; color: {'#68D391' if percent >= 60 else '#FC8181'};")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_card.add_widget(score_lbl)
        
        info_lbl = QLabel(f"ФИО: {data['student']}  ·  Результат: {score}/{total}")
        info_lbl.setStyleSheet("color: #CBD5E0; font-size: 16px; max-height: 100px")
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_card.add_widget(info_lbl)
            
        c_layout.addWidget(top_card)
        
        btn = DangerButton("Выйти")
        btn.clicked.connect(self.logout.emit)
        c_layout.addWidget(btn)
        
        container.setLayout(c_layout)
        layout.addWidget(container)


# ==========================================
# ЭКРАНЫ ВАЛИДАТОРА
# ==========================================
from src.config import VALIDATOR_CREDS

class ValidatorLoginScreen(QWidget):
    success = pyqtSignal(str)
    back = pyqtSignal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        layout.addWidget(IconLabel("🔐"))
        layout.addWidget(AppTitle("Вход для Валидатора"))

        card = QuestionCard()
        
        self.login_inp = QLineEdit()
        self.login_inp.setPlaceholderText("Логин")
        card.add_widget(self.login_inp)
        
        self.pwd_inp = QLineEdit()
        self.pwd_inp.setPlaceholderText("Пароль")
        self.pwd_inp.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_inp.returnPressed.connect(self._check)
        card.add_widget(self.pwd_inp)
        
        layout.addWidget(card)

        btn_row = QHBoxLayout()
        b_btn = ActionButton("← Назад")
        b_btn.clicked.connect(self.back.emit)
        btn_row.addWidget(b_btn)
        
        v_btn = SuccessButton("Войти")
        v_btn.clicked.connect(self._check)
        btn_row.addWidget(v_btn)
        
        layout.addLayout(btn_row)
        layout.addStretch()

    def _check(self):
        login = self.login_inp.text().strip()
        pwd = self.pwd_inp.text().strip()
        if VALIDATOR_CREDS.get(login) == pwd:
            self.success.emit(login)
        else:
            self.login_inp.setStyleSheet("border: 2px solid #FC8181;")
            self.pwd_inp.setStyleSheet("border: 2px solid #FC8181;")


class ValidatorDatabaseScreen(DatabaseScreen):
    def __init__(self):
        super().__init__()
        # Наследуем UI из обычного выбора БД
        
class ValidatorKRScreen(KRScreen):
    def __init__(self, db_path):
        super().__init__(db_path)


class ValidatorTestScreen(QWidget):
    finished = pyqtSignal(dict)

    def __init__(self, validator_login, db_path, kr_name):
        super().__init__()
        self.validator_login = validator_login
        self.db_path = db_path
        self.kr_name = kr_name
        self.kr = kr_name if kr_name else (os.path.basename(db_path) if db_path else "Unknown DB")
        self.questions = load_questions(db_path, kr_name=kr_name)
        self.answers = {}
        self.validity = {} # Сохранение статуса "Валидный вопрос"
        self.skipped = set()
        self.current_idx = 0
        self.widgets = [] 
        self.nav_buttons = []
        
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        
        # ЛЕВАЯ ПАНЕЛЬ
        nav_panel = QWidget()
        nav_panel.setObjectName("nav_panel")
        nav_panel.setFixedWidth(260)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(14, 16, 14, 16)
        
        nav_layout.addWidget(SectionTitle("НАВИГАЦИЯ"))
        nav_layout.addSpacing(5)
        
        nav_container = QWidget()
        nav_container.setObjectName("nav_grid_container")  
        grid_layout = QGridLayout()
        grid_layout.setSpacing(6)
        grid_layout.setContentsMargins(12, 12, 12, 12)
        
        total = len(self.questions)
        for i in range(total):
            btn = QPushButton(str(i + 1))
            btn.setObjectName("nav_btn_empty")
            btn.setFixedSize(28, 28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, idx=i: self._load_q(idx))
            grid_layout.addWidget(btn, i // 7, i % 7)
            self.nav_buttons.append(btn)
            
        nav_container.setLayout(grid_layout)
        nav_layout.addWidget(nav_container)        
        nav_layout.addStretch()

        info_lbl = QLabel(f"👨‍⚕️ Валидатор: {validator_login}")
        info_lbl.setStyleSheet("color: #A0AEC0; font-size: 13px;")
        nav_layout.addWidget(info_lbl)

        root.addWidget(nav_panel)
        
        # ЦЕНТРАЛЬНАЯ ЧАСТЬ
        center = QWidget()
        c_layout = QVBoxLayout(center)
        c_layout.setContentsMargins(32, 28, 32, 28)
        
        self.prog_lbl = QLabel()
        self.prog_lbl.setStyleSheet("color: #A0AEC0; font-size: 13px;")
        c_layout.addWidget(self.prog_lbl)
        
        self.q_card = QuestionCard()
        self.q_lbl = QLabel()
        self.q_lbl.setObjectName("question_label")
        self.q_lbl.setWordWrap(True)
        self.q_card.add_widget(self.q_lbl)
        
        self.opt_container = QWidget()
        self.opt_layout = QVBoxLayout(self.opt_container)
        self.opt_layout.setContentsMargins(0,10,0,0)
        self.opt_container.setObjectName("question_layout")
        self.q_card.add_widget(self.opt_container)

        self.validity_cb = QCheckBox("Валидный вопрос")
        self.validity_cb.setStyleSheet("color: #68D391; font-weight: bold; margin-top: 15px;")
        self.validity_cb.stateChanged.connect(self._save_ans)
        self.q_card.add_widget(self.validity_cb)
        
        c_layout.addWidget(self.q_card)
        c_layout.addStretch()

        nav_btns = QHBoxLayout()
        nav_btns.setSpacing(15)
        
        self.btn_back = ActionButton("← Назад")
        self.btn_back.clicked.connect(self._back)
        nav_btns.addWidget(self.btn_back)
        
        self.btn_skip = SkipButton("Пропустить")
        self.btn_skip.clicked.connect(self._skip)
        nav_btns.addWidget(self.btn_skip)
        
        nav_btns.addStretch()
        
        self.btn_next = ActionButton("Вперёд →")
        self.btn_next.clicked.connect(self._next)
        nav_btns.addWidget(self.btn_next)
        
        self.btn_finish = SuccessButton("✓ Завершить")
        self.btn_finish.clicked.connect(self._finish_confirm)
        nav_btns.addWidget(self.btn_finish)
        
        c_layout.addLayout(nav_btns)
        root.addWidget(center)
        
        self._load_q(0)

    def _update_nav(self):
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_idx:
                btn.setObjectName("nav_btn_active")
            elif i in self.answers:
                btn.setObjectName("nav_btn_answered")
            elif i in self.skipped:
                btn.setObjectName("nav_btn_skipped")
            else:
                btn.setObjectName("nav_btn_empty")
            btn.setStyle(btn.style())

    def _load_q(self, idx):
        self._save_ans()
        if not (0 <= idx < len(self.questions)): return
        
        self.current_idx = idx
        q = self.questions[idx]
        
        self.prog_lbl.setText(f"Вопрос {idx+1} из {len(self.questions)}")
        self.q_lbl.setText(f"<b>{q['question']}</b>")
        
        while self.opt_layout.count():
            item = self.opt_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        import textwrap
        self.widgets = []
        if q['type'] == 'multiple':
            for k, v in q['options'].items():
                wrapped_text = textwrap.fill(f"{k.upper()})  {v}", width=90)
                cb = QCheckBox(wrapped_text)
                cb.stateChanged.connect(self._save_ans)
                self.opt_layout.addWidget(cb)
                self.widgets.append((k, cb))
                if idx in self.answers and k in self.answers[idx].split(','):
                    cb.setChecked(True)
        else:
            self.bg = QButtonGroup(self)
            for k, v in q['options'].items():
                wrapped_text = textwrap.fill(f"{k.upper()})  {v}", width=90)
                rb = QRadioButton(wrapped_text)
                rb.toggled.connect(self._save_ans)
                self.bg.addButton(rb)
                self.opt_layout.addWidget(rb)
                self.widgets.append((k, rb))
                if idx in self.answers and self.answers[idx] == k:
                    rb.setChecked(True)
        
        # Галочка валидности (по умолчанию считаем валидным, если еще не сохраняли)
        is_valid = self.validity.get(idx, True)
        self.validity_cb.setChecked(is_valid)

        self._update_nav()
        
        is_first = (idx == 0)
        self.btn_back.setEnabled(not is_first)
        is_last = (idx == len(self.questions) - 1)
        self.btn_next.setEnabled(not is_last)
        self.btn_finish.setVisible(True)

    def _save_ans(self):
        if not hasattr(self, 'widgets') or not self.widgets:
            return

        self.validity[self.current_idx] = self.validity_cb.isChecked()

        q = self.questions[self.current_idx]
        if q['type'] == 'multiple':
            selected = [k for k, w in self.widgets if w.isChecked()]
            if selected: 
                self.answers[self.current_idx] = ",".join(sorted(selected))
                self.skipped.discard(self.current_idx)
        else:
            for k, w in self.widgets:
                if w.isChecked():
                    self.answers[self.current_idx] = k
                    self.skipped.discard(self.current_idx)
                    break

    def _next(self): self._load_q(self.current_idx + 1)
    def _back(self): self._load_q(self.current_idx - 1)
    def _skip(self): 
        self.skipped.add(self.current_idx)
        self._next()

    def _finish_confirm(self):
        self._save_ans()
        reply = QMessageBox.question(self, "Завершение", 
                                    f"Отвечено: {len(self.answers)}/{len(self.questions)}\nЗавершить валидацию?",
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            db_name = os.path.basename(self.db_path).replace('.xlsx', '') if self.db_path else "Unknown_DB"
            self.finished.emit({
                "validator": self.validator_login, "kr": self.kr,
                "questions": self.questions, "answers": self.answers,
                "validity": self.validity, "db_path": self.db_path, "db_name": db_name
            })

from src.utils import generate_validator_pdf

class ValidatorResultScreen(QWidget):
    logout = pyqtSignal()
    
    def __init__(self, data):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        generate_validator_pdf(
            validator=data['validator'],
            kr=data['kr'],
            questions=data['questions'],
            answers=data['answers'],
            validity=data['validity'],
            db_name=data['db_name']
        )
                
        container = QWidget()
        c_layout = QVBoxLayout(container)
        c_layout.setContentsMargins(48, 32, 48, 32)
        c_layout.setSpacing(20)
        
        top_card = QuestionCard()
        score_lbl = QLabel("Валидация завершена")
        score_lbl.setStyleSheet(f"font-size: 40px; font-weight: 800; color: #68D391;")
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_card.add_widget(score_lbl)
        
        info_lbl = QLabel(f"Валидатор: {data['validator']}  ·  База: {data['db_name']}  ·  КР: {data['kr']}")
        info_lbl.setStyleSheet("color: #CBD5E0; font-size: 16px; max-height: 100px")
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_card.add_widget(info_lbl)
            
        c_layout.addWidget(top_card)
        
        btn = DangerButton("Выйти")
        btn.clicked.connect(self.logout.emit)
        c_layout.addWidget(btn)
        
        container.setLayout(c_layout)
        layout.addWidget(container)