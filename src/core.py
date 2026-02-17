import pandas as pd
from src.config import QUESTIONS_FILE, RESULTS_FILE, EXAM_PASSWORDS
from datetime import datetime

def load_questions(category: str | None = None, n: int = 100):
    """
    Загружает вопросы, нормализует колонки и фильтрует по категории.
    """
    # Демо данные, если нет файла или pandas
    try:
        if not QUESTIONS_FILE.exists():
            return _get_demo_data(n)
        
        df = pd.read_excel(QUESTIONS_FILE)
        
        # Нормализация имен колонок (убираем пробелы, lower case)
        df.columns = [str(c).strip().lower() for c in df.columns]
        
        # Маппинг для надежности (если в Excel написано "Option A" или "Вариант А")
        col_map = {}
        for col in df.columns:
            if 'question' in col or 'вопрос' in col: col_map[col] = 'question'
            elif 'option' in col and 'a' in col: col_map[col] = 'option_a'
            elif 'option' in col and 'b' in col: col_map[col] = 'option_b'
            elif 'option' in col and 'c' in col: col_map[col] = 'option_c'
            elif 'option' in col and 'd' in col: col_map[col] = 'option_d'
            elif 'correct' in col or 'ответ' in col: col_map[col] = 'correct'
            elif 'cat' in col: col_map[col] = 'category'
            elif 'type' in col: col_map[col] = 'type'
            
        df = df.rename(columns=col_map)
        
        # Фильтрация
        if category and category != "Все категории" and "category" in df.columns:
            df = df[df["category"].astype(str).str.strip() == category]

        if df.empty:
            return _get_demo_data(n)

        # Выборка
        sample_size = min(n, len(df))
        df = df.sample(sample_size).reset_index(drop=True)

        questions = []
        for _, row in df.iterrows():
            # Очистка правильного ответа (удаляем пробелы: "a, b" -> "a,b")
            raw_correct = str(row.get("correct", "a")).strip().lower()
            correct = ",".join([x.strip() for x in raw_correct.split(",") if x.strip()])
            
            q_type = str(row.get("type", "single")).strip().lower()
            
            questions.append({
                "question": str(row.get("question", "?")),
                "options": {
                    "a": str(row.get("option_a", "-")),
                    "b": str(row.get("option_b", "-")),
                    "c": str(row.get("option_c", "-")),
                    "d": str(row.get("option_d", "-")),
                },
                "correct": correct,
                "category": str(row.get("category", "General")),
                "type": "multiple" if q_type == "multiple" else "single",
            })
        return questions

    except Exception as e:
        print(f"Error loading questions: {e}")
        return _get_demo_data(n)

def get_categories():
    try:
        if not QUESTIONS_FILE.exists():
            return list(EXAM_PASSWORDS.keys())
        df = pd.read_excel(QUESTIONS_FILE)
        # Ищем колонку категории
        cat_col = next((c for c in df.columns if 'cat' in str(c).lower()), None)
        if cat_col:
            cats = sorted(df[cat_col].dropna().unique().astype(str).tolist())
            return ["Все категории"] + cats
    except Exception:
        pass
    return ["Все категории"]

def save_result_to_excel(student, score, total, category):
    try:
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Student": student,
            "Category": category,
            "Score": score,
            "Total": total,
            "Percent": round(score/total*100, 1) if total else 0
        }
        if RESULTS_FILE.exists():
            df = pd.read_excel(RESULTS_FILE)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        df.to_excel(RESULTS_FILE, index=False)
    except Exception as e:
        print(f"Error saving result: {e}")

def _get_demo_data(n):
    return [{"question": "Демо вопрос 1 (ответ A)", "options": {"a": "Да", "b": "Нет", "c": "-", "d": "-"}, "correct": "a", "category": "Demo", "type": "single"}] * n
