from pathlib import Path

# Пароли
EXAM_PASSWORDS = {
    "Анатомия": "anat2025",
    "Физиология": "phys2025",
    "Фармакология": "pharm2025",
    "Клиника": "clin2025",
    "Все категории": "admin2025",
}

TIME_FOR_EXAM = 30*60

# Пути
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
QUESTIONS_FILE = DATA_DIR / "questions.xlsx"
RESULTS_FILE = DATA_DIR / "all_results.xlsx"

# Создаем папки при запуске
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)
