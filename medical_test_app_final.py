"""
Medical Test Application — PyQt6 (ПОЛНАЯ ВЕРСИЯ ПО ТЗ)
Медицинская тестовая система с валидацией, прокторингом и множественным выбором.

Зависимости:
    pip install PyQt6 pandas openpyxl fpdf2 pyautogui opencv-python

Структура файлов:
    questions.xlsx      — вопросы (столбцы: question, option_a..d, correct, category, type)
    all_results.xlsx    — создаётся автоматически
    reports/            — скриншоты прокторинга

Формат correct:
    - Один ответ: "a", "b", "c", "d"
    - Множественный: "a,c", "b,d", "a,b,c"

Формат type:
    - "single" — один ответ (RadioButton)
    - "multiple" — множественный выбор (CheckBox)
"""

import sys
import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QButtonGroup,
    QRadioButton,
    QScrollArea,
    QFrame,
    QStackedWidget,
    QMessageBox,
    QLineEdit,
    QComboBox,
    QGridLayout,
    QCheckBox,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPalette, QColor

# ══════════════════════════════════════════════════════════════════════════════
#  КОНФИГУРАЦИЯ ПАРОЛЕЙ
# ══════════════════════════════════════════════════════════════════════════════
EXAM_PASSWORDS = {
    "Анатомия": "anat2025",
    "Физиология": "phys2025",
    "Фармакология": "pharm2025",
    "Клиника": "clin2025",
    "Все категории": "admin2025",
}

# ── Импорты опциональных зависимостей ─────────────────────────────────────────
try:
    import pandas as pd

    PANDAS_OK = True
except ImportError:
    PANDAS_OK = False
    print("⚠ pandas не установлен: pip install pandas openpyxl")

try:
    import pyautogui

    PYAUTOGUI_OK = True
except ImportError:
    PYAUTOGUI_OK = False
    print("⚠ pyautogui не установлен: pip install pyautogui")

try:
    from fpdf import FPDF

    FPDF_OK = True
except ImportError:
    FPDF_OK = False
    print("⚠ fpdf2 не установлен: pip install fpdf2")

try:
    import cv2

    CV2_OK = True
except ImportError:
    CV2_OK = False
    print("⚠ opencv-python не установлен (веб-камера отключена)")


# ══════════════════════════════════════════════════════════════════════════════
#  QSS СТИЛИ
# ══════════════════════════════════════════════════════════════════════════════
DARK_QSS = """
QMainWindow, QWidget {
    background-color: #0F1117;
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QWidget#nav_panel {
    background-color: #161B27;
    border-right: 1px solid #2D3748;
}

QPushButton#nav_btn_empty {
    background-color: #2D3748;
    color: #A0AEC0;
    border: 1px solid #3D4F6E;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#nav_btn_active {
    background-color: #2B6CB0;
    color: #FFFFFF;
    border: 2px solid #4299E1;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#nav_btn_answered {
    background-color: #276749;
    color: #FFFFFF;
    border: 1px solid #38A169;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#nav_btn_skipped {
    background-color: #9C4221;
    color: #FFFFFF;
    border: 1px solid #DD6B20;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#action_btn {
    background-color: #2B6CB0;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}
QPushButton#action_btn:hover {
    background-color: #3182CE;
}

QPushButton#success_btn {
    background-color: #276749;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}
QPushButton#success_btn:hover {
    background-color: #38A169;
}

QPushButton#danger_btn {
    background-color: #C53030;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
}

QFrame#question_card {
    background-color: #1A202C;
    border: 1px solid #2D3748;
    border-radius: 12px;
}

QLabel#question_label {
    color: #F7FAFC;
    font-size: 16px;
    font-weight: 600;
    background-color: transparent;
}

QRadioButton, QCheckBox {
    color: #CBD5E0;
    font-size: 14px;
    spacing: 12px;
    padding: 10px 12px;
    background-color: transparent;
}
QRadioButton:hover, QCheckBox:hover {
    background-color: #1E2A3A;
    color: #EDF2F7;
}
QRadioButton:checked, QCheckBox:checked {
    background-color: #1A365D;
    color: #90CDF4;
    font-weight: 600;
}

QLineEdit, QComboBox {
    background-color: #1A202C;
    color: #E2E8F0;
    border: 1px solid #4A5568;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    min-height: 20px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #3182CE;
}

QComboBox QAbstractItemView {
    background-color: #1A202C;
    color: #E2E8F0;
    selection-background-color: #2B6CB0;
}

QLabel#section_title {
    color: #A0AEC0;
    font-size: 11px;
    font-weight: 700;
    background-color: transparent;
}

QLabel#app_title {
    font-size: 32px;
    font-weight: 800;
    color: #90CDF4;
    background-color: transparent;
}
"""


# ══════════════════════════════════════════════════════════════════════════════
#  ПОТОКИ ПРОКТОРИНГА
# ══════════════════════════════════════════════════════════════════════════════
class ProctorThread(QThread):
    screenshot_taken = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, student_name: str, interval: int = 30):
        super().__init__()
        self.student_name = student_name
        self.interval = interval
        self._running = False
        self.report_dir = Path("reports") / student_name
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        self._running = True
        while self._running:
            self.msleep(self.interval * 1000)
            if not self._running:
                break
            self._take_screenshot()

    def _take_screenshot(self):
        if not PYAUTOGUI_OK:
            return
        try:
            ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            path = str(self.report_dir / f"screen_{ts}.png")
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            self.screenshot_taken.emit(path)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._running = False
        self.quit()
        self.wait(3000)


class WebcamThread(QThread):
    photo_taken = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, student_name: str, interval: int = 60):
        super().__init__()
        self.student_name = student_name
        self.interval = interval
        self._running = False
        self.report_dir = Path("reports") / student_name
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.camera = None

    def run(self):
        if not CV2_OK:
            return
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                self.error_occurred.emit("Камера недоступна")
                return
            self._running = True
            while self._running:
                self.msleep(self.interval * 1000)
                if not self._running:
                    break
                self._capture_frame()
        except Exception as e:
            self.error_occurred.emit(str(e))
        finally:
            if self.camera:
                self.camera.release()

    def _capture_frame(self):
        try:
            if self.camera is not None:
                ret, frame = self.camera.read()
                if ret:
                    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    path = str(self.report_dir / f"webcam_{ts}.jpg")
                    cv2.imwrite(path, frame)
                    self.photo_taken.emit(path)
        except Exception as e:
            self.error_occurred.emit(str(e))

    def stop(self):
        self._running = False
        if self.camera:
            self.camera.release()
        self.quit()
        self.wait(3000)


# ══════════════════════════════════════════════════════════════════════════════
#  ЗАГРУЗКА ВОПРОСОВ
# ══════════════════════════════════════════════════════════════════════════════
def load_questions(
    filepath: str = "question_med.xlsx", category: str | None = None, n: int = 100
):
    """
    Загружает вопросы из Excel.
    Столбцы: question, option_a, option_b, option_c, option_d, correct, category, type
    correct: "a" | "b" | "c" | "d" | "a,c" | "b,d" и т.д.
    type: "single" | "multiple"
    """
    if not PANDAS_OK:
        return _demo_questions(n)

    path = Path(filepath)
    if not path.exists():
        print(f"⚠ Файл {filepath} не найден")
        return _demo_questions(n)

    try:
        df = pd.read_excel(path)
    except (PermissionError, Exception) as e:
        print(f"⚠ Ошибка чтения {filepath}: {e}")
        return _demo_questions(n)

    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    if category and category != "Все категории" and "category" in df.columns:
        df = df[df["category"].str.strip() == category]

    if len(df) == 0:
        return _demo_questions(n)

    sample_size = min(n, len(df))
    df = df.sample(sample_size).reset_index(drop=True)

    questions = []
    for _, row in df.iterrows():
        q_type = str(row.get("type", "single")).strip().lower()
        if q_type not in ("single", "multiple"):
            q_type = "single"

        correct = str(row.get("correct", "a")).strip().lower()

        q = {
            "question": str(row.get("question", "?")),
            "options": {
                "a": str(row.get("option_a", "Вариант A")),
                "b": str(row.get("option_b", "Вариант B")),
                "c": str(row.get("option_c", "Вариант C")),
                "d": str(row.get("option_d", "Вариант D")),
            },
            "correct": correct,
            "category": str(row.get("category", "Общее")),
            "type": q_type,
        }
        questions.append(q)
    return questions


def get_categories(filepath: str = "questions.xlsx"):
    if not PANDAS_OK:
        return ["Все категории", "Анатомия", "Физиология", "Фармакология", "Клиника"]
    path = Path(filepath)
    if not path.exists():
        return ["Все категории", "Анатомия", "Физиология", "Фармакология", "Клиника"]
    try:
        df = pd.read_excel(path)
        df.columns = [c.strip().lower() for c in df.columns]
        if "category" in df.columns:
            cats = ["Все категории"] + sorted(df["category"].dropna().unique().tolist())
            return cats
    except Exception:
        pass
    return ["Все категории"]


def _demo_questions(n: int = 20):
    """Демо-вопросы для тестирования."""
    topics = [
        (
            "Какой орган вырабатывает инсулин?",
            "Печень",
            "Поджелудочная",
            "Почки",
            "Надпочечники",
            "b",
            "single",
        ),
        (
            "ЧСС в норме (уд/мин):",
            "40–60",
            "60–100",
            "100–120",
            "120–150",
            "b",
            "single",
        ),
        (
            "Витамин D синтезируется:",
            "В печени",
            "В коже (УФ)",
            "В почках",
            "В кишечнике",
            "b",
            "single",
        ),
        (
            "Выберите признаки воспаления:",
            "Боль",
            "Температура",
            "Отёк",
            "Все верно",
            "d",
            "single",
        ),
        (
            "Множественный: признаки гипертонии:",
            "Головная боль",
            "Тахикардия",
            "Головокружение",
            "Тошнота",
            "a,c",
            "multiple",
        ),
    ]
    result = []
    pool = topics * (n // len(topics) + 1)
    for t in pool[:n]:
        result.append(
            {
                "question": t[0],
                "options": {"a": t[1], "b": t[2], "c": t[3], "d": t[4]},
                "correct": t[5],
                "category": "Демо",
                "type": t[6],
            }
        )
    return result


# ══════════════════════════════════════════════════════════════════════════════
#  PDF-ОТЧЁТ
# ══════════════════════════════════════════════════════════════════════════════
def generate_pdf_report(
    student_name: str,
    questions: list,
    answers: dict,
    score: int,
    total: int,
    category: str,
):
    if not FPDF_OK:
        return None
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, "Medical Test Report", ln=True, align="C")
    pdf.set_font("Helvetica", "", 13)
    pdf.cell(
        0,
        8,
        f"Date: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}",
        ln=True,
        align="C",
    )
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"  Student: {student_name}    Category: {category}", ln=True)
    pdf.ln(3)

    percent = round(score / total * 100, 1) if total > 0 else 0
    pdf.set_font("Helvetica", "B", 16)
    verdict = f"Score: {score}/{total} ({percent}%)"
    pdf.cell(0, 10, verdict, ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Answer Details:", ln=True)
    pdf.ln(2)

    for i, q in enumerate(questions):
        user_ans = answers.get(i)
        correct = q["correct"]

        # Для множественного выбора
        if q["type"] == "multiple":
            correct_set = set(correct.split(","))
            user_set = set(user_ans.split(",")) if user_ans else set()
            is_correct = correct_set == user_set
        else:
            is_correct = user_ans == correct

        pdf.set_font("Helvetica", "B", 10)
        pdf.multi_cell(0, 7, f"Q{i + 1}. {q['question'][:90]}")

        pdf.set_font("Helvetica", "", 10)
        pdf.cell(10)
        pdf.cell(0, 6, f"Correct: {correct}", ln=True)

        if user_ans:
            pdf.cell(10)
            status = "OK" if is_correct else f"Wrong: {user_ans}"
            pdf.cell(0, 6, status, ln=True)
        pdf.ln(2)

    report_dir = Path("reports") / student_name
    report_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_path = str(report_dir / f"report_{ts}.pdf")
    pdf.output(pdf_path)
    return pdf_path


def save_to_all_results(student_name: str, score: int, total: int, category: str):
    if not PANDAS_OK:
        return
    filepath = "all_results.xlsx"
    now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    percent = round(score / total * 100, 1) if total > 0 else 0

    new_row = {
        "Дата": now,
        "Студент": student_name,
        "Категория": category,
        "Баллы": score,
        "Всего": total,
        "Процент": percent,
    }

    if Path(filepath).exists():
        df = pd.read_excel(filepath)
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    else:
        df = pd.DataFrame([new_row])

    df.to_excel(filepath, index=False)


# ══════════════════════════════════════════════════════════════════════════════
#  ЭКРАН 1: ВЫБОР КАТЕГОРИИ
# ══════════════════════════════════════════════════════════════════════════════
class CategoryScreen(QWidget):
    category_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        icon = QLabel("⚕")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 72px; color: #3182CE;")
        layout.addWidget(icon)

        title = QLabel("Medical Test System")
        title.setObjectName("app_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Шаг 1: Выберите направление экзамена")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QFrame()
        card.setObjectName("question_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(32, 28, 32, 28)

        lbl = QLabel("НАПРАВЛЕНИЕ ЭКЗАМЕНА")
        lbl.setObjectName("section_title")
        card_layout.addWidget(lbl)

        self.cat_combo = QComboBox()
        cats = get_categories()
        self.cat_combo.addItems(cats)
        card_layout.addWidget(self.cat_combo)

        layout.addWidget(card)

        next_btn = QPushButton("Далее →")
        next_btn.setObjectName("action_btn")
        next_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        next_btn.clicked.connect(self._on_next)
        layout.addWidget(next_btn)

        layout.addStretch()

    def _on_next(self):
        category = self.cat_combo.currentText()
        self.category_selected.emit(category)


# ══════════════════════════════════════════════════════════════════════════════
#  ЭКРАН 2: ВАЛИДАЦИЯ ПАРОЛЯ
# ══════════════════════════════════════════════════════════════════════════════
class PasswordScreen(QWidget):
    password_validated = pyqtSignal()
    go_back = pyqtSignal()

    def __init__(self, category: str | None, parent=None):
        super().__init__(parent)
        self.category = category or "Unknown"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        icon = QLabel("🔒")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 72px;")
        layout.addWidget(icon)

        title = QLabel(f"Валидация: {self.category}")
        title.setObjectName("app_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Шаг 2: Введите пароль для доступа к экзамену")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QFrame()
        card.setObjectName("question_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(32, 28, 32, 28)

        lbl = QLabel("ПАРОЛЬ")
        lbl.setObjectName("section_title")
        card_layout.addWidget(lbl)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setPlaceholderText("Введите пароль...")
        self.pass_input.returnPressed.connect(self._validate)
        card_layout.addWidget(self.pass_input)

        self.error_label = QLabel()
        self.error_label.setStyleSheet("color: #FC8181; font-size: 12px;")
        self.error_label.setWordWrap(True)
        card_layout.addWidget(self.error_label)

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← Назад")
        back_btn.setObjectName("action_btn")
        back_btn.clicked.connect(self.go_back.emit)
        btn_row.addWidget(back_btn)

        validate_btn = QPushButton("Проверить пароль")
        validate_btn.setObjectName("success_btn")
        validate_btn.clicked.connect(self._validate)
        btn_row.addWidget(validate_btn)

        layout.addLayout(btn_row)
        layout.addStretch()

    def _validate(self):
        entered = self.pass_input.text().strip()
        correct = EXAM_PASSWORDS.get(self.category, "")

        if entered == correct:
            self.password_validated.emit()
        else:
            self.error_label.setText("❌ Неверный пароль. Попробуйте ещё раз.")
            self.pass_input.clear()
            self.pass_input.setFocus()


# ══════════════════════════════════════════════════════════════════════════════
#  ЭКРАН 3: ВВОД ФИО
# ══════════════════════════════════════════════════════════════════════════════
class StudentNameScreen(QWidget):
    name_entered = pyqtSignal(str)
    go_back = pyqtSignal()

    def __init__(self, category: str | None, parent=None):
        super().__init__(parent)
        self.category = category or "Unknown"
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(80, 60, 80, 60)

        icon = QLabel("👤")
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setStyleSheet("font-size: 72px;")
        layout.addWidget(icon)

        title = QLabel(f"Экзамен: {self.category}")
        title.setObjectName("app_title")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        sub = QLabel("Шаг 3: Введите ваше ФИО")
        sub.setStyleSheet("color: #718096; font-size: 16px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        layout.addSpacing(20)

        card = QFrame()
        card.setObjectName("question_card")
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(14)
        card_layout.setContentsMargins(32, 28, 32, 28)

        lbl = QLabel("ФИО СТУДЕНТА")
        lbl.setObjectName("section_title")
        card_layout.addWidget(lbl)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Иванов Иван Иванович")
        self.name_input.returnPressed.connect(self._on_start)
        card_layout.addWidget(self.name_input)

        layout.addWidget(card)

        btn_row = QHBoxLayout()
        back_btn = QPushButton("← Назад")
        back_btn.setObjectName("action_btn")
        back_btn.clicked.connect(self.go_back.emit)
        btn_row.addWidget(back_btn)

        start_btn = QPushButton("▶ Начать тест")
        start_btn.setObjectName("success_btn")
        start_btn.clicked.connect(self._on_start)
        btn_row.addWidget(start_btn)

        layout.addLayout(btn_row)

        warn = QLabel(
            "🎥 Прокторинг: скриншоты каждые 30 сек, веб-камера каждую минуту"
        )
        warn.setStyleSheet("color: #718096; font-size: 12px;")
        warn.setWordWrap(True)
        warn.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(warn)

        layout.addStretch()

    def _on_start(self):
        name = self.name_input.text().strip()
        if not name:
            self.name_input.setStyleSheet("border: 2px solid #E53E3E;")
            return
        self.name_input.setStyleSheet("")
        self.name_entered.emit(name)


# ══════════════════════════════════════════════════════════════════════════════
#  ЭКРАН 4: ТЕСТ
# ══════════════════════════════════════════════════════════════════════════════
class TestScreen(QWidget):
    test_finished = pyqtSignal(dict)

    def __init__(self, student_name: str, category: str | None, parent=None):
        super().__init__(parent)
        self.student_name = student_name
        self.category = category or "Unknown"
        self.questions = load_questions(category=self.category, n=100)
        self.total = len(self.questions)
        self.current_idx = 0
        self.answers = {}
        self.skipped = set()
        self.nav_buttons = []
        self.focus_log = []
        self._build_ui()
        self._start_proctor()
        self._show_question(0)

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        # Левая панель
        nav_panel = QWidget()
        nav_panel.setObjectName("nav_panel")
        nav_panel.setFixedWidth(260)
        nav_layout = QVBoxLayout(nav_panel)
        nav_layout.setContentsMargins(14, 16, 14, 16)

        nav_title = QLabel("НАВИГАЦИЯ")
        nav_title.setObjectName("section_title")
        nav_layout.addWidget(nav_title)

        self.proctor_lbl = QLabel("● Прокторинг активен")
        self.proctor_lbl.setStyleSheet("color: #68D391; font-size: 11px;")
        nav_layout.addWidget(self.proctor_lbl)
        nav_layout.addSpacing(4)

        # Сетка
        grid = QGridLayout()
        grid.setSpacing(4)
        for i in range(self.total):
            btn = QPushButton(str(i + 1))
            btn.setObjectName("nav_btn_empty")
            btn.setFixedSize(22, 22)
            btn.clicked.connect(lambda _, idx=i: self._show_question(idx))
            grid.addWidget(btn, i // 10, i % 10)
            self.nav_buttons.append(btn)
        nav_layout.addLayout(grid)
        nav_layout.addSpacing(8)

        # Легенда
        for color, text in [
            ("#2D3748", "Не посещён"),
            ("#2B6CB0", "Текущий"),
            ("#276749", "Отвечен"),
            ("#9C4221", "Пропущен"),
        ]:
            row = QHBoxLayout()
            dot = QLabel()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"background-color: {color}; border-radius: 6px;")
            lbl = QLabel(text)
            lbl.setStyleSheet("color: #718096; font-size: 11px;")
            row.addWidget(dot)
            row.addWidget(lbl)
            row.addStretch()
            nav_layout.addLayout(row)

        nav_layout.addStretch()

        self.timer_lbl = QLabel("00:00")
        self.timer_lbl.setStyleSheet(
            "color: #F6E05E; font-size: 20px; font-weight: 700;"
        )
        self.timer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        nav_layout.addWidget(self.timer_lbl)

        self._elapsed = 0
        self._qtimer = QTimer(self)
        self._qtimer.timeout.connect(self._tick)
        self._qtimer.start(1000)

        root.addWidget(nav_panel)

        # Центр
        center = QWidget()
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(32, 28, 32, 28)

        top_bar = QHBoxLayout()
        self.progress_lbl = QLabel()
        self.progress_lbl.setStyleSheet("color: #A0AEC0; font-size: 13px;")
        top_bar.addWidget(self.progress_lbl)
        top_bar.addStretch()
        center_layout.addLayout(top_bar)

        self.question_card = QFrame()
        self.question_card.setObjectName("question_card")
        q_layout = QVBoxLayout(self.question_card)
        q_layout.setContentsMargins(24, 20, 24, 20)

        self.question_label = QLabel()
        self.question_label.setObjectName("question_label")
        self.question_label.setWordWrap(True)
        q_layout.addWidget(self.question_label)

        # Контейнер для radio/checkbox
        self.options_container = QWidget()
        self.options_layout = QVBoxLayout(self.options_container)
        self.options_layout.setContentsMargins(0, 0, 0, 0)
        q_layout.addWidget(self.options_container)

        center_layout.addWidget(self.question_card)
        center_layout.addStretch()

        nav_btns = QHBoxLayout()
        self.back_btn = QPushButton("← Назад")
        self.back_btn.setObjectName("action_btn")
        self.back_btn.clicked.connect(self._go_back)

        self.skip_btn = QPushButton("Пропустить →")
        self.skip_btn.setObjectName("action_btn")
        self.skip_btn.setStyleSheet("background-color: #9C4221;")
        self.skip_btn.clicked.connect(self._go_skip)

        self.next_btn = QPushButton("Вперёд →")
        self.next_btn.setObjectName("action_btn")
        self.next_btn.clicked.connect(self._go_next)

        self.finish_btn = QPushButton("✓ Завершить тест")
        self.finish_btn.setObjectName("success_btn")
        self.finish_btn.clicked.connect(self._confirm_finish)

        nav_btns.addWidget(self.back_btn)
        nav_btns.addWidget(self.skip_btn)
        nav_btns.addStretch()
        nav_btns.addWidget(self.next_btn)
        nav_btns.addWidget(self.finish_btn)
        center_layout.addLayout(nav_btns)

        root.addWidget(center)

    def _start_proctor(self):
        self.proctor = ProctorThread(self.student_name)
        self.proctor.screenshot_taken.connect(
            lambda p: self.proctor_lbl.setText(f"● {Path(p).name}")
        )
        self.proctor.start()

        self.webcam = WebcamThread(self.student_name)
        self.webcam.start()

    def _tick(self):
        self._elapsed += 1
        m, s = divmod(self._elapsed, 60)
        self.timer_lbl.setText(f"{m:02d}:{s:02d}")

    def _show_question(self, idx: int):
        self._save_current_answer()
        self._update_nav_button(self.current_idx)

        self.current_idx = idx
        q = self.questions[idx]

        self.progress_lbl.setText(f"Вопрос {idx + 1} из {self.total}")
        self.question_label.setText(f"<b>Вопрос {idx + 1}.</b> {q['question']}")

        # Очищаем старые виджеты
        while self.options_layout.count():
            child = self.options_layout.takeAt(0)
            if child is not None:
                widget = child.widget()
                if widget is not None:
                    widget.deleteLater()

        # Множественный или одиночный
        if q["type"] == "multiple":
            self.checkboxes = {}
            for key in ("a", "b", "c", "d"):
                cb = QCheckBox(f"{key.upper()}.  {q['options'][key]}")
                self.checkboxes[key] = cb
                self.options_layout.addWidget(cb)

            # Восстанавливаем
            if idx in self.answers:
                selected = set(self.answers[idx].split(","))
                for key, cb in self.checkboxes.items():
                    cb.setChecked(key in selected)
        else:
            self.btn_group = QButtonGroup(self)
            self.radio_buttons = {}
            for key in ("a", "b", "c", "d"):
                rb = QRadioButton(f"{key.upper()}.  {q['options'][key]}")
                self.btn_group.addButton(rb)
                self.radio_buttons[key] = rb
                self.options_layout.addWidget(rb)

            if idx in self.answers:
                self.radio_buttons[self.answers[idx]].setChecked(True)

        self._update_all_nav_buttons()
        self.back_btn.setEnabled(idx > 0)
        self.next_btn.setVisible(idx < self.total - 1)

    def _save_current_answer(self):
        q = self.questions[self.current_idx]
        if q["type"] == "multiple" and hasattr(self, "checkboxes"):
            checked = [k for k, cb in self.checkboxes.items() if cb.isChecked()]
            if checked:
                self.answers[self.current_idx] = ",".join(sorted(checked))
        elif q["type"] == "single" and hasattr(self, "radio_buttons"):
            for k, rb in self.radio_buttons.items():
                if rb.isChecked():
                    self.answers[self.current_idx] = k
                    break

    def _update_nav_button(self, idx: int):
        if idx >= len(self.nav_buttons):
            return
        btn = self.nav_buttons[idx]
        if idx == self.current_idx:
            name = "nav_btn_active"
        elif idx in self.skipped:
            name = "nav_btn_skipped"
        elif idx in self.answers:
            name = "nav_btn_answered"
        else:
            name = "nav_btn_empty"
        btn.setObjectName(name)
        btn.setStyle(btn.style())

    def _update_all_nav_buttons(self):
        for i in range(self.total):
            self._update_nav_button(i)

    def _go_back(self):
        self._save_current_answer()
        if self.current_idx > 0:
            self._show_question(self.current_idx - 1)

    def _go_next(self):
        self._save_current_answer()
        if self.current_idx < self.total - 1:
            self._show_question(self.current_idx + 1)

    def _go_skip(self):
        self._save_current_answer()
        self.skipped.add(self.current_idx)
        if self.current_idx < self.total - 1:
            self._show_question(self.current_idx + 1)

    def _confirm_finish(self):
        self._save_current_answer()
        answered = len(self.answers)
        msg = QMessageBox(self)
        msg.setWindowTitle("Завершить тест?")
        msg.setText(f"Отвечено: {answered}/{self.total}\n\nЗавершить?")
        msg.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        msg.setStyleSheet(DARK_QSS)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            self._finish()

    def _finish(self):
        self._qtimer.stop()
        if hasattr(self, "proctor"):
            self.proctor.stop()
        if hasattr(self, "webcam"):
            self.webcam.stop()

        # Сохраняем лог фокуса
        if self.focus_log:
            log_path = Path("reports") / self.student_name / "focus_log.txt"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(log_path, "w", encoding="utf-8") as f:
                for ts, evt in self.focus_log:
                    f.write(f"{ts} — {evt}\n")

        self.test_finished.emit(
            {
                "student": self.student_name,
                "category": self.category,
                "questions": self.questions,
                "answers": self.answers,
                "elapsed": self._elapsed,
            }
        )

    def changeEvent(self, event):
        if event.type() == event.Type.ActivationChange:
            if not self.isActiveWindow():
                ts = datetime.datetime.now().strftime("%H:%M:%S")
                self.focus_log.append((ts, "Потеря фокуса"))
        super().changeEvent(event)

    def closeEvent(self, event):
        if hasattr(self, "proctor"):
            self.proctor.stop()
        if hasattr(self, "webcam"):
            self.webcam.stop()
        super().closeEvent(event)


# ══════════════════════════════════════════════════════════════════════════════
#  ЭКРАН 5: РЕЗУЛЬТАТЫ
# ══════════════════════════════════════════════════════════════════════════════
class ResultScreen(QWidget):
    logout = pyqtSignal()

    def __init__(self, data: dict, parent=None):
        super().__init__(parent)
        self.data = data
        self._build_ui()

    def _build_ui(self):
        questions = self.data["questions"]
        answers = self.data["answers"]
        student = self.data["student"]
        category = self.data["category"]
        elapsed = self.data["elapsed"]

        # Подсчёт
        score = 0
        for i, q in enumerate(questions):
            user_ans = answers.get(i)
            if q["type"] == "multiple":
                correct_set = set(q["correct"].split(","))
                user_set = set(user_ans.split(",")) if user_ans else set()
                if correct_set == user_set:
                    score += 1
            else:
                if user_ans == q["correct"]:
                    score += 1

        total = len(questions)
        percent = round(score / total * 100, 1) if total > 0 else 0

        pdf_path = generate_pdf_report(
            student, questions, answers, score, total, category
        )
        save_to_all_results(student, score, total, category)

        # UI
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(48, 32, 48, 32)

        # Карточка результата
        top_card = QFrame()
        top_card.setObjectName("question_card")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(32, 24, 32, 24)

        score_lbl = QLabel(f"{percent}%")
        score_lbl.setStyleSheet(
            f"font-size: 72px; font-weight: 800; color: {'#68D391' if percent >= 60 else '#FC8181'};"
        )
        score_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(score_lbl)

        fio_lbl = QLabel(f"ФИО: {student}")
        fio_lbl.setStyleSheet("font-size: 18px; color: #CBD5E0;")
        fio_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(fio_lbl)

        m, s = divmod(elapsed, 60)
        stats = QLabel(
            f"Категория: {category}  ·  Правильно: {score}/{total}  ·  Время: {m:02d}:{s:02d}"
        )
        stats.setStyleSheet("color: #718096; font-size: 13px;")
        stats.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(stats)

        if pdf_path:
            pdf_lbl = QLabel(f"📄 PDF: {pdf_path}")
            pdf_lbl.setStyleSheet("color: #90CDF4; font-size: 12px;")
            pdf_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            top_layout.addWidget(pdf_lbl)

        layout.addWidget(top_card)

        # Разбор
        err_title = QLabel("РАЗБОР ОТВЕТОВ")
        err_title.setObjectName("section_title")
        layout.addWidget(err_title)

        for i, q in enumerate(questions):
            user_ans = answers.get(i)
            correct = q["correct"]

            if q["type"] == "multiple":
                correct_set = set(correct.split(","))
                user_set = set(user_ans.split(",")) if user_ans else set()
                is_correct = correct_set == user_set
            else:
                is_correct = user_ans == correct

            card = QFrame()
            card.setStyleSheet(
                f"background-color: {'#1A2E22' if is_correct else '#2D1515'}; border-left: 4px solid {'#38A169' if is_correct else '#E53E3E'}; border-radius: 8px;"
            )
            c_layout = QVBoxLayout(card)
            c_layout.setContentsMargins(16, 12, 16, 12)

            q_lbl = QLabel(f"<b>Q{i + 1}.</b> {q['question']}")
            q_lbl.setWordWrap(True)
            q_lbl.setStyleSheet(
                f"color: {'#C6F6D5' if is_correct else '#FED7D7'}; font-size: 13px;"
            )
            c_layout.addWidget(q_lbl)

            correct_lbl = QLabel(f"✓ Правильно: {correct}")
            correct_lbl.setStyleSheet("color: #68D391; font-size: 13px;")
            c_layout.addWidget(correct_lbl)

            if user_ans:
                ua_lbl = QLabel(f"{'✓' if is_correct else '✗'} Ваш ответ: {user_ans}")
                ua_lbl.setStyleSheet(
                    f"color: {'#68D391' if is_correct else '#FC8181'}; font-size: 13px;"
                )
            else:
                ua_lbl = QLabel("— Нет ответа")
                ua_lbl.setStyleSheet("color: #F6E05E; font-size: 13px;")
            c_layout.addWidget(ua_lbl)

            layout.addWidget(card)

        # Кнопка выхода
        btn_row = QHBoxLayout()
        logout_btn = QPushButton("🚪 Выйти из учетной записи")
        logout_btn.setObjectName("danger_btn")
        logout_btn.clicked.connect(self.logout.emit)
        btn_row.addStretch()
        btn_row.addWidget(logout_btn)
        layout.addLayout(btn_row)

        scroll.setWidget(container)
        root.addWidget(scroll)


# ══════════════════════════════════════════════════════════════════════════════
#  ГЛАВНОЕ ОКНО
# ══════════════════════════════════════════════════════════════════════════════
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Test System")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)

        # Анти-чит: окно всегда поверх
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.category = None
        self._show_category()

    def _show_category(self):
        self.cat_screen = CategoryScreen()
        self.cat_screen.category_selected.connect(self._show_password)
        self.stack.addWidget(self.cat_screen)
        self.stack.setCurrentWidget(self.cat_screen)

    def _show_password(self, category: str):
        self.category = category
        self.pass_screen = PasswordScreen(category)
        self.pass_screen.password_validated.connect(self._show_name)
        self.pass_screen.go_back.connect(
            lambda: self.stack.setCurrentWidget(self.cat_screen)
        )
        self.stack.addWidget(self.pass_screen)
        self.stack.setCurrentWidget(self.pass_screen)

    def _show_name(self):
        self.name_screen = StudentNameScreen(self.category)
        self.name_screen.name_entered.connect(self._show_test)
        self.name_screen.go_back.connect(
            lambda: self.stack.setCurrentWidget(self.pass_screen)
        )
        self.stack.addWidget(self.name_screen)
        self.stack.setCurrentWidget(self.name_screen)

    def _show_test(self, student_name: str):
        self.test_screen = TestScreen(student_name, self.category)
        self.test_screen.test_finished.connect(self._show_results)
        self.stack.addWidget(self.test_screen)
        self.stack.setCurrentWidget(self.test_screen)

    def _show_results(self, data: dict):
        self.result_screen = ResultScreen(data)
        self.result_screen.logout.connect(self._on_logout)
        self.stack.addWidget(self.result_screen)
        self.stack.setCurrentWidget(self.result_screen)

    def _on_logout(self):
        # Очищаем все экраны
        for i in range(self.stack.count() - 1, -1, -1):
            w = self.stack.widget(i)
            if w is not None:
                self.stack.removeWidget(w)
                w.deleteLater()
        self.category = None
        self._show_category()


# ══════════════════════════════════════════════════════════════════════════════
#  ТОЧКА ВХОДА
# ══════════════════════════════════════════════════════════════════════════════
def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_QSS)
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor.fromString("#0F1117"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor.fromString("#E2E8F0"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()