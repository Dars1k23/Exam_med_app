import pandas as pd
from src.config import QUESTIONS_FILE, RESULTS_FILE, CATEGORY_FILE
from datetime import datetime

def load_questions(category: str | None = None, n: int = 100):
    """
    Загружает вопросы, нормализует колонки и фильтрует по категории.
    """
    
    if not QUESTIONS_FILE.exists():
        raise "Нет файла с вопросами"
    
    if not CATEGORY_FILE.exists():
        raise "Нет файла с категориями"
    
    questions_df = pd.read_excel(QUESTIONS_FILE)
    questions_df = questions_df.astype(str)

    categories = get_categories()
    code = -1
    for key in categories:
        if categories[key]["Описание"] == category:
            code = categories[key]["Код"]

    questions_df = (questions_df[questions_df["Раздел"] == code])

    if (len(questions_df) == 0):
        raise "Нет вопросов в категории"
    
    n = min(n, len(questions_df))

    questions_df = questions_df.sample(n=n)
    
    questions = []
    for _, row in questions_df.iterrows():
        question = str(row.get("Вопрос"))

        options = {}
        for i in range(5):
            if str(row.get(f"Ответ{i+1}")) != "nan":
                options[str(i+1)] = str(row.get(f"Ответ{i+1}"))

        correct = str(row.get("Верный_ответ"))


        questions.append({"question": question, "options": options, "correct": correct, "category": "Demo", "type": "single"})


    return questions


def get_categories():
    try:
        if not CATEGORY_FILE.exists():
            return {"-1": {"Описание":"Все категории", "Пароль": ""}}
        
        df = pd.read_excel(CATEGORY_FILE)
        df = df.astype(str)

        if 'Состояние' in df.columns:
            df = df.drop(columns=['Состояние'])        

        result_dict = df.set_index('Код', drop=False).to_dict(orient='index')
        result_dict["-1"] = {"Описание":"Все категории", "Пароль": ""}
        return result_dict
    except Exception:
        pass
    return {"-1": {"Описание":"Все категории", "Пароль": ""}}

def save_result_to_excel(student, score, answered, total, category, time, warning):
    try:
        new_row = {
            "Время написания": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ФИО": student,
            "Категория": category,
            "Баллы": score,
            "Количество отвечанный вопросов": answered,
            "Количество всех вопросов": total,
            "Процент выполнения": round(score/total*100, 1) if total else 0,
            "Время написания, сек": time,
            "Замечанно списывание (1 - да, 0 - нет)": warning
        }
        if RESULTS_FILE.exists():
            df = pd.read_excel(RESULTS_FILE)
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df = pd.DataFrame([new_row])
        df.to_excel(RESULTS_FILE, index=False)
    except Exception as e:
        print(f"Error saving result: {e}")