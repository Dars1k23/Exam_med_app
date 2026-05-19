import sys
from pathlib import Path
from src.vault import DATA_DIR_OPEN

TIME_FOR_EXAM = 30*60

VALIDATOR_CREDS = {
    "admin": "admin",
    "validator": "12345"
}

def get_base_path():
    """Возвращает корень приложения (учитывает PyInstaller _internal)"""
    if getattr(sys, 'frozen', False):
        # PyInstaller: используем sys._MEIPASS (указывает на _internal)
        return Path(sys._MEIPASS)
    # Разработка: корень проекта
    return Path(__file__).resolve().parent.parent

def get_bundle_dir() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return Path(__file__).resolve().parent.parent


# Пути
BASE_DIR = get_base_path()
DATA_DIR = DATA_DIR_OPEN
REPORTS_DIR = DATA_DIR / "reports"
QUESTIONS_FILE = DATA_DIR / "Вопросы.xlsx"
SECTIONS_FILE = DATA_DIR / "Разделы.xlsx"
RESULTS_FILE = DATA_DIR / "all_results.xlsx"
BUNDLE_DIR = get_bundle_dir()
FONTS_DIR = BUNDLE_DIR / "fonts"

# Создаем папки при запуске
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)
