import pandas as pd
import os
from src.config import RESULTS_FILE
from datetime import datetime

def load_questions(db_path: str, kr_name: str = None, n: int = 100):
    try:
        if not os.path.exists(db_path):
            print(f"File not found: {db_path}")
            return _get_demo_data(n)

        df = pd.read_excel(db_path)
        df.columns = [str(c).strip().lower() for c in df.columns]

        question_col = next((c for c in df.columns if "вопрос" in c or "question" in c), None)
        correct_col = next((c for c in df.columns if "правильный ответ" in c or "верный" in c or "correct" in c), None)
        explanation_col = next((c for c in df.columns if "обоснование" in c), None)

        if not question_col or not correct_col:
            print("Required columns not found")
            return _get_demo_data(n)

        kr_col = next((c for c in df.columns if "кр (название)" in c or ("кр" in c and "название" in c)), None)

        if kr_name and kr_col:
            df = df[df[kr_col].astype(str).str.strip() == kr_name]

        def normalize_correct(value):
            answer_map = {
                "1": "a", "2": "b", "3": "c", "4": "d", "5": "e",
                "a": "a", "b": "b", "c": "c", "d": "d", "e": "e",
                "а": "a", "б": "b", "с": "c", "д": "d", "е": "e" # русские буквы на всякий случай
            }
            raw = str(value).strip().lower()
            if not raw or raw == "nan":
                return "a"

            # Разделяем по запятым или точкам с запятой для множественного выбора
            parts = [x.strip() for x in raw.replace(';', ',').split(",") if x.strip()]
            converted = [answer_map.get(p, p) for p in parts if p in answer_map or p in ['a','b','c','d','e']]
            return ",".join(converted) if converted else "a"

        # Убираем пустые вопросы
        df = df[df[question_col].notna()]

        if df.empty:
            return _get_demo_data(n)

        # Выборка
        sample_size = min(n, len(df))
        df = df.sample(sample_size).reset_index(drop=True)

        questions = []
        db_name = os.path.basename(db_path)

        for _, row in df.iterrows():
            correct = normalize_correct(row.get(correct_col, "1"))
            explanation = str(row.get(explanation_col, "")).strip() if explanation_col else ""

            options = {
                "a": str(row.get("вариант a", row.get("ответ1", ""))).strip(),
                "b": str(row.get("вариант b", row.get("ответ2", ""))).strip(),
                "c": str(row.get("вариант c", row.get("ответ3", ""))).strip(),
                "d": str(row.get("вариант d", row.get("ответ4", ""))).strip(),
            }

            # Пятый вариант добавляем только если он есть
            option_e = str(row.get("вариант e", row.get("ответ5", ""))).strip()
            if option_e and option_e.lower() != "nan":
                options["e"] = option_e

            q_type = "multiple" if "," in correct else "single"

            questions.append({
                "question": str(row.get(question_col, "?")).strip(),
                "options": options,
                "correct": correct,
                "explanation": explanation,
                "kr": db_name,
                "type": q_type,
            })

        return questions

    except Exception as e:
        print(f"Error loading questions: {e}")
        return _get_demo_data(n)


def save_result_to_excel(student, score, answered, total, kr, time):
    try:
        new_row = {
            "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Student": student,
            "КР": kr,
            "Score": score,
            "Answered": answered,
            "Total": total,
            "Percent": round(score/total*100, 1) if total else 0,
            "Lead Time": time
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
    return [{"question": f"Демо вопрос {i} (ответ a)", "options": {"a": "Да", "b": "Нет", "c": str(i), "d": "-"}, "correct": "a", "kr": "Demo DB", "type": "single"} for i in range(n)]