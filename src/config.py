from pathlib import Path

BLACK_LIST = {
    # Браузеры
    "chrome", "firefox", "edge", "opera", "brave", "safari",
    # Соцсети/Мессенджеры
    "telegram", "discord", "whatsapp", "vk", "zoom", "teams",
    "skype", "slack", "signal", "viber"
}

TIME_FOR_EXAM = 30*60

# Пути
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = DATA_DIR / "reports"
QUESTIONS_FILE = DATA_DIR / "Вопросы.xlsx"
CATEGORY_FILE = DATA_DIR / "Разделы по номерам таблица.xlsx"
RESULTS_FILE = DATA_DIR / "Все результаты.xlsx"

# Создаем папки при запуске
REPORTS_DIR.mkdir(exist_ok=True, parents=True)
DATA_DIR.mkdir(exist_ok=True, parents=True)
