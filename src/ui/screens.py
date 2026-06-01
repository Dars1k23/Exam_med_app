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
        
        self.s_btn = SuccessButton("Далее →")
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

from src.variant_mapper import map_variant_to_rows

# --- ЭКРАН 3: ВЫБОР ВАРИАНТА ---
class VariantScreen(QWidget):
    start_test = pyqtSignal(str)
    back = pyqtSignal()

    def __init__(self, db_path, is_validator=False):
        super().__init__()
        self.db_path = db_path
        self.is_validator = is_validator
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        layout.addWidget(IconLabel("⚕", "#3182CE"))
        layout.addWidget(AppTitle("Medical Test System"))
        
        sub = QLabel("Шаг 3: Выберите вариант для экзамена" if is_validator else "Шаг 3: Нажмите для начала теста (Вариант будет выбран случайно)")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QuestionCard()
        card.add_widget(SectionTitle("ВАРИАНТ ЭКЗАМЕНА"))
        
        self.combo = QComboBox()
        self.combo.addItem("Выберите вариант...", "")
        
        variant_mapping = map_variant_to_rows(db_path)
        self.variants = list(variant_mapping.keys())
        for variant_name, rows in variant_mapping.items():
            self.combo.addItem(f"{variant_name} ({len(rows)} вопросов)", variant_name)
            
        card.add_widget(self.combo)
        
        if not is_validator:
            self.combo.hide() # Студент не выбирает сам
            card.add_widget(QLabel("Вариант будет выбран автоматически."))

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        b_btn = ActionButton("← Назад")
        b_btn.clicked.connect(self.back.emit)
        btn_row.addWidget(b_btn)
        
        self.s_btn = SuccessButton("▶ Начать тест")
        if is_validator:
            self.s_btn.setEnabled(False)
            self.s_btn.clicked.connect(lambda: self.start_test.emit(self.combo.currentData() or ""))
        else:
            self.s_btn.setEnabled(True)
            self.s_btn.clicked.connect(self._start_random)
        
        self.combo.currentIndexChanged.connect(self._on_combo_changed)
        
        btn_row.addWidget(self.s_btn)
        layout.addLayout(btn_row)

        layout.addStretch()

    def _start_random(self):
        import random
        if self.variants:
            v = random.choice(self.variants)
            self.start_test.emit(v)
        else:
            self.start_test.emit("")

    def _on_combo_changed(self):
        if self.combo.currentData():
            self.s_btn.setEnabled(True)
        else:
            self.s_btn.setEnabled(False)

# --- ЭКРАН 4: ТЕСТ (Сложная верстка с панелью) ---
class TestScreen(QWidget):
    finished = pyqtSignal(dict)

    def __init__(self, student, db_path, variant_name):
        super().__init__()
        self.student = student
        self.db_path = db_path
        self.variant_name = variant_name # Это начальный вариант (может быть переопределен из tmp)
        
        # Логика восстановления или инициализации
        import re
        db_name = os.path.basename(self.db_path).replace('.xlsx', '') if self.db_path else "Unknown_DB"
        safe_db_name = re.sub(r'[\\/*?:"<>|]', "_", db_name)
        # Директория теста ТЕПЕРЬ НЕ СОДЕРЖИТ названия варианта
        self.test_dir_name = Path(f"{safe_db_name}")
        
        tmp_path = REPORTS_DIR / self.student / self.test_dir_name / "tmp.txt"
        self.data_for_tmp = { "start_exams": 0, "answers": {}, "variant": self.variant_name, "question_times": {}}
        
        if os.path.exists(tmp_path):
            self._read_tmp_file()
            self.variant = self.data_for_tmp.get("variant", self.variant_name)
            self.start_time = datetime.datetime.fromtimestamp(self.data_for_tmp["start_exams"])
            self.answers = self.data_for_tmp.get("answers", {})
            self.question_times = self.data_for_tmp.get("question_times", {})
            self.question_times = {int(k): v for k, v in self.question_times.items()}
        else:
            self.variant = self.variant_name if self.variant_name else (os.path.basename(db_path) if db_path else "Unknown DB")
            self.start_time = datetime.datetime.now()
            self.data_for_tmp["start_exams"] = self.start_time.timestamp()
            self.data_for_tmp["variant"] = self.variant
            self.answers = {}
            self.question_times = {}
            self.data_for_tmp["question_times"] = self.question_times

            os.makedirs(REPORTS_DIR / self.student / self.test_dir_name, exist_ok=True)
            self._update_tmp_file()

        self.questions = load_questions(db_path, variant_name=self.variant)
        self.skipped = set()
        self.current_idx = 0
        self.last_timer_update = datetime.datetime.now()
        self.widgets = [] # Инициализируем сразу! (Fix AttributeError)
        self.nav_buttons = []
        
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
        
        # Область прокрутки
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 10, 0)
        
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
        
        self.scroll_layout.addWidget(self.q_card)
        self.scroll_layout.addStretch()
        
        self.scroll.setWidget(scroll_content)
        c_layout.addWidget(self.scroll)

         # Кнопки внизу (не прокручиваются)
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
        now = datetime.datetime.now()
        elapsed_on_q = (now - self.last_timer_update).total_seconds()
        self.question_times[self.current_idx] = self.question_times.get(self.current_idx, 0) + elapsed_on_q
        self.last_timer_update = now
        self.data_for_tmp["question_times"] = self.question_times
        self._update_tmp_file()

        delta = self.start_time + datetime.timedelta(seconds=TIME_FOR_EXAM) - now 
        seconds = int(delta.total_seconds())

        if delta.total_seconds() < 0:
            self._finish_confirm(False)

        m, s = divmod(max(0, seconds), 60)
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
        self.last_timer_update = datetime.datetime.now()
        q = self.questions[idx]
        
        self.prog_lbl.setText(f"Вопрос {idx+1} из {len(self.questions)}")
        self.q_lbl.setText(f"<b>{q['question'].replace('\n', '<br>')}</b>")
        
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

    def _finish_confirm(self, checked=None, ask=True):
        # Если вызвало нажатием кнопки (checked будет False или True от сигнала clicked)
        # или если явно передано ask=True
        is_user_triggered = (checked is not None and not isinstance(checked, datetime.datetime)) or ask is True
        
        self._save_ans()
        end = False
        
        if is_user_triggered and ask is not False:
            answered = len(self.answers)
            total = len(self.questions)
            unanswered = total - answered
            
            msg = f"Вы ответили на {answered} из {total} вопросов."
            if unanswered > 0:
                msg += f"\n\n⚠️ Внимание: {unanswered} вопросов остались без ответа!"
            
            msg += "\n\nВы действительно хотите завершить тест?"
            
            box = QMessageBox(self)
            box.setWindowTitle("Завершение теста")
            box.setText(msg)
            box.setIcon(QMessageBox.Icon.Question)
            yes_btn = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
            no_btn = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            box.exec()
            
            if box.clickedButton() == yes_btn:
                end = True
        else:
            # Сюда попадаем только при автоматическом завершении (например, по таймеру)
            end = True
        
        if end:
            tmp_path = REPORTS_DIR / self.student / self.test_dir_name / "tmp.txt"
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            self._stop_threads()
            self.timer.stop()
            self.finished.emit({
                "student": self.student, "variant": self.variant,
                "questions": self.questions, "answers": self.answers,
                "elapsed": (datetime.datetime.now() - self.start_time).seconds if (datetime.datetime.now() - self.start_time).seconds < TIME_FOR_EXAM  else TIME_FOR_EXAM,
                "test_dir_name": self.test_dir_name,
                "question_times": self.question_times,
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
        save_result_to_excel(data['student'], score, len(data['answers']), total, data['variant'], data["elapsed"])
        
        db_name = os.path.basename(data.get('db_path', '')).replace('.xlsx', '')
        generate_pdf(data['student'], data["test_dir_name"], data['variant'], data['questions'], data['answers'], score, total, data["elapsed"], db_name, data.get('question_times', {}))
                
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
        
class ValidatorVariantScreen(VariantScreen):
    def __init__(self, db_path, is_validator=True):
        super().__init__(db_path, is_validator=is_validator)


class ValidatorTestScreen(QWidget):
    finished = pyqtSignal(dict)

    def __init__(self, validator_login, db_path, variant_name):
        super().__init__()
        self.validator_login = validator_login
        self.db_path = db_path
        self.variant_name = variant_name
        self.variant = variant_name if variant_name else (os.path.basename(db_path) if db_path else "Unknown DB")
        self.questions = load_questions(db_path, variant_name=variant_name)
        self.answers = {}
        self.validity = {} # Сохранение статуса валидности (is_valid)
        self.question_times = {} # Время на каждый вопрос
        self.last_timer_update = datetime.datetime.now()
        self.skipped = set()
        self.current_idx = 0
        self.widgets = [] 
        self.nav_buttons = []
        self._loading = False
        
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
        
        # Область прокрутки
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll.setStyleSheet("background: transparent;")
        
        scroll_content = QWidget()
        scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 10, 0)

        self.q_card = QuestionCard()
        self.q_lbl = QLabel()
        self.q_lbl.setObjectName("question_label")
        self.q_lbl.setWordWrap(True)
        self.q_card.add_widget(self.q_lbl)
        
        # Надпись "Не валиден" (между вопросом и вариантами)
        self.status_lbl = QLabel("⚠️ НЕ ВАЛИДЕН")
        self.status_lbl.setStyleSheet("color: #FC8181; font-weight: bold; font-size: 18px; margin: 10px 0;")
        self.status_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_lbl.hide()
        self.q_card.add_widget(self.status_lbl)
        
        self.opt_container = QWidget()
        self.opt_layout = QVBoxLayout(self.opt_container)
        self.opt_layout.setContentsMargins(0,10,0,0)
        self.opt_container.setObjectName("question_layout")
        self.q_card.add_widget(self.opt_container)

        self.validity_cb = QCheckBox("не валидный")
        self.validity_cb.setStyleSheet("color: #FC8181; font-weight: bold; margin-top: 15px;")
        self.validity_cb.stateChanged.connect(self._save_ans)
        self.q_card.add_widget(self.validity_cb)
        
        self.scroll_layout.addWidget(self.q_card)
        
        # Ответ и обоснование (скрыты по умолчанию)
        self.ans_card = QuestionCard()
        self.ans_card.setObjectName("answer_card")
        self.ans_card.setStyleSheet("background-color: #1A365D; border: 1px solid #3182CE; margin-top: 20px;")
        self.ans_lbl = QLabel()
        self.ans_lbl.setWordWrap(True)
        self.ans_lbl.setStyleSheet("color: #90CDF4; font-weight: bold; font-size: 15px;")
        self.ans_card.add_widget(self.ans_lbl)
        
        self.expl_lbl = QLabel()
        self.expl_lbl.setWordWrap(True)
        self.expl_lbl.setStyleSheet("color: #E2E8F0; font-size: 14px; margin-top: 8px;")
        self.ans_card.add_widget(self.expl_lbl)
        
        self.ans_card.hide()
        self.scroll_layout.addWidget(self.ans_card)
        self.scroll_layout.addStretch()
        
        self.scroll.setWidget(scroll_content)
        c_layout.addWidget(self.scroll)

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

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_question_timer)
        self.timer.start(1000)

    def _update_question_timer(self):
        now = datetime.datetime.now()
        elapsed_on_q = (now - self.last_timer_update).total_seconds()
        self.question_times[self.current_idx] = self.question_times.get(self.current_idx, 0) + elapsed_on_q
        self.last_timer_update = now

    def _update_nav(self):
        for i, btn in enumerate(self.nav_buttons):
            if i == self.current_idx:
                btn.setObjectName("nav_btn_active")
            elif not self.validity.get(i, True):
                # Если помечен как "не валиден" - всегда красный
                btn.setObjectName("nav_btn_incorrect")
            elif i in self.answers:
                # Если дан любой ответ - зеленый
                btn.setObjectName("nav_btn_answered")
            elif i in self.skipped:
                btn.setObjectName("nav_btn_skipped")
            else:
                btn.setObjectName("nav_btn_empty")
            btn.setStyle(btn.style())

    def _load_q(self, idx):
        self._save_ans()
        if not (0 <= idx < len(self.questions)): return
        
        self._loading = True
        self.current_idx = idx
        self.last_timer_update = datetime.datetime.now()
        q = self.questions[idx]
        
        self.prog_lbl.setText(f"Вопрос {idx+1} из {len(self.questions)}")
        self.q_lbl.setText(f"<b>{q['question'].replace('\n', '<br>')}</b>")
        
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
        self.validity_cb.setChecked(not is_valid)
        self.status_lbl.setVisible(not is_valid)

        # Обновляем инфо об ответе
        if idx in self.answers:
            self._show_explanation(q)
        else:
            self.ans_card.hide()

        self._update_nav()
        self._loading = False
        
        is_first = (idx == 0)
        self.btn_back.setEnabled(not is_first)
        is_last = (idx == len(self.questions) - 1)
        self.btn_next.setEnabled(not is_last)
        self.btn_finish.setVisible(True)

    def _show_explanation(self, q):
        correct_key = q['correct'].upper()
        # Получаем текст правильного ответа
        correct_text = ""
        if ',' in q['correct']:
            keys = q['correct'].split(',')
            parts = [f"{k.upper()}: {q['options'].get(k, '')}" for k in keys]
            correct_text = "Правильные ответы:\n" + "\n".join(parts)
        else:
            correct_text = f"Правильный ответ: {correct_key} ({q['options'].get(q['correct'], '')})"
            
        self.ans_lbl.setText(correct_text)
        
        expl = q.get('explanation', '')
        if expl and expl.lower() != 'nan':
            self.expl_lbl.setText(f"<b>Обоснование:</b><br>{expl}")
            self.expl_lbl.show()
        else:
            self.expl_lbl.hide()
            
        self.ans_card.show()

    def _save_ans(self):
        if self._loading or not hasattr(self, 'widgets') or not self.widgets:
            return

        is_valid = not self.validity_cb.isChecked()
        self.validity[self.current_idx] = is_valid
        self.status_lbl.setVisible(not is_valid)

        q = self.questions[self.current_idx]
        has_answer = False
        if q['type'] == 'multiple':
            selected = [k for k, w in self.widgets if w.isChecked()]
            if selected: 
                self.answers[self.current_idx] = ",".join(sorted(selected))
                self.skipped.discard(self.current_idx)
                has_answer = True
        else:
            for k, w in self.widgets:
                if w.isChecked():
                    self.answers[self.current_idx] = k
                    self.skipped.discard(self.current_idx)
                    has_answer = True
                    break
        
        if has_answer:
            self._show_explanation(q)

    def _next(self): self._load_q(self.current_idx + 1)
    def _back(self): self._load_q(self.current_idx - 1)
    def _skip(self): 
        self.skipped.add(self.current_idx)
        self._next()

    def _finish_confirm(self):
        self._save_ans()
        answered = len(self.answers)
        total = len(self.questions)
        unanswered = total - answered
        
        msg = f"Отвечено на {answered} из {total} вопросов."
        if unanswered > 0:
            msg += f"\n\n⚠️ Внимание: {unanswered} вопросов остались без ответа!"
        
        msg += "\n\nВы действительно хотите завершить валидацию?"
        
        box = QMessageBox(self)
        box.setWindowTitle("Завершение валидации")
        box.setText(msg)
        box.setIcon(QMessageBox.Icon.Question)
        yes_btn = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
        no_btn = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        box.exec()
        
        if box.clickedButton() == yes_btn:
            self.timer.stop()
            db_name = os.path.basename(self.db_path).replace('.xlsx', '') if self.db_path else "Unknown_DB"
            self.finished.emit({
                "validator": self.validator_login, "variant": self.variant,
                "questions": self.questions, "answers": self.answers,
                "validity": self.validity, "db_path": self.db_path, "db_name": db_name,
                "question_times": self.question_times
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
            variant=data['variant'],
            questions=data['questions'],
            answers=data['answers'],
            validity=data['validity'],
            db_name=data['db_name'],
            question_times=data.get('question_times', {})
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
        
        info_lbl = QLabel(f"Валидатор: {data['validator']}  ·  База: {data['db_name']}  ·  Вариант: {data['variant']}")
        info_lbl.setStyleSheet("color: #CBD5E0; font-size: 16px; max-height: 100px")
        info_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_card.add_widget(info_lbl)
            
        c_layout.addWidget(top_card)
        
        btn = DangerButton("Выйти")
        btn.clicked.connect(self.logout.emit)
        c_layout.addWidget(btn)
        
        container.setLayout(c_layout)
        layout.addWidget(container)
