import cv2
import sys
import pyautogui
import datetime
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from fpdf import FPDF
import os
from src.config import REPORTS_DIR, FONTS_DIR, DATA_DIR


# --- ПРОКТОРИНГ ---

class ProctorThread(QThread):
    screenshot_taken = pyqtSignal(str)

    def __init__(self, student_name, test_dir_name: Path, interval=30):
        super().__init__()
        self.screens_dir = REPORTS_DIR / student_name / test_dir_name / "screens"
        self.screens_dir.mkdir(exist_ok=True, parents=True)
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            try:
                ts = datetime.datetime.now().strftime("%H%M%S")
                path = self.screens_dir / f"scr_{ts}.png"
                pyautogui.screenshot().save(path)
                self.screenshot_taken.emit(str(path))
            except Exception as e:
                print(f"[Proctor Error]: {e}")

            # Дробим сон по 100 мс, чтобы поток завершался мгновенно
            for _ in range(int(self.interval * 10)):
                if not self._running:
                    break
                self.msleep(100)

    def stop(self):
        self._running = False
        self.wait()  # Железно ждем завершения потока


class WebcamThread(QThread):
    def __init__(self, student_name, test_number: Path, interval=30):
        super().__init__()
        self.photos_dir = REPORTS_DIR / student_name / test_number / "photos"
        self.photos_dir.mkdir(exist_ok=True, parents=True)
        self.interval = interval
        self._running = True

    def run(self):
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("[Webcam Error]: Не удалось открыть камеру. Проверь индекс или разрешения.")
            return

        print("[Webcam]: Камера успешно запущена.")

        try:
            while self._running:
                ret, frame = cap.read()
                if ret:
                    ts = datetime.datetime.now().strftime("%H%M%S")
                    path = self.photos_dir / f"cam_{ts}.jpg"

                    try:
                        # --- ОБХОД КИРИЛЛИЦЫ В ПУТИ ---
                        # 1. Кодируем изображение во временный буфер в памяти (в формат .jpg)
                        success, encoded_img = cv2.imencode('.jpg', frame)

                        if success:
                            # 2. Сохраняем буфер встроенными средствами Python, которые отлично дружат с UTF-8
                            with open(path, "wb") as f:
                                f.write(encoded_img)
                        else:
                            print("[Webcam Error]: Не удалось закодировать кадр в JPG.")

                    except Exception as file_err:
                        print(f"[Webcam Save Error]: Ошибка при записи файла на диск: {file_err}")

                else:
                    print("[Webcam Error]: Не удалось прочитать кадр с камеры.")

                # Чуткий сон
                for _ in range(int(self.interval * 10)):
                    if not self._running:
                        break
                    self.msleep(100)
        except Exception as e:
            print(f"[Webcam Crash]: {e}")
        finally:
            cap.release()
            print("[Webcam]: Камера успешно освобождена.")

    def stop(self):
        self._running = False
        self.wait()  # Обязательно ждем закрытия cv2.VideoCapture перед выходом

# --- PDF ---
def _add_header(pdf, student, variant, percentage, score, total, elapsed_time, db_name):
    image_path = Path(DATA_DIR / "image.png")
    if image_path.exists():
        pdf.image(str(image_path), x=65, y=10, w=80)
        pdf.ln(95)
    else:
        pdf.ln(10)
    
    pdf.set_font("TNR", '', size=16)
    pdf.multi_cell(0, 8, "КЛИНИКА ДОКТОРА РОШАЛЯ", ln=True, align='C')
    pdf.ln(2)
    
    pdf.set_font("TNR", '', size=24)
    pdf.multi_cell(0, 12, "ОТЧЁТ", ln=True, align='C')
    pdf.ln(8)
    
    pdf.set_font("TNR", '', size=12)
    pdf.multi_cell(0, 7, f"Версия БД: {db_name}", ln=True, align='C')
    pdf.multi_cell(0, 7, f"Вариант: {variant}", ln=True, align='C')
    pdf.multi_cell(0, 7, f"ФИО: {student}", ln=True, align='C')
    m, s = divmod(elapsed_time, 60)
    pdf.multi_cell(0, 7, f"Затраченное время: {m:02d}:{s:02d}", ln=True, align='C')
    
    if percentage >= 60:
        pdf.set_text_color(0, 128, 0)
    else:
        pdf.set_text_color(255, 0, 0)
    pdf.multi_cell(0, 8, f"Результат: {percentage}% ({score} из {total})", ln=True, align='C')
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)
    
    pdf.set_draw_color(180, 180, 180)
    pdf.set_line_width(0.5)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(10)


def generate_pdf(student, test_dir_name: Path, variant, questions, answers, score, total, elapsed_time, db_name, question_times=None):
    try:        
        if question_times is None: question_times = {}
        percentage = round(score / total * 100) if total > 0 else 0
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        out_dir = REPORTS_DIR / student / test_dir_name
        out_dir.mkdir(parents=True, exist_ok=True)

        # ==========================================
        # 1. ДЕТАЛЬНЫЙ ОТЧЕТ
        # ==========================================
        pdf_det = FPDF()
        pdf_det.add_page()
        pdf_det.set_left_margin(15)
        pdf_det.set_right_margin(15)
        pdf_det.set_auto_page_break(auto=True, margin=20)

        pdf_det.add_font("TNR", "", FONTS_DIR / "timesnrcyrmt.ttf", uni=True)
        pdf_det.set_font("TNR", "", 12)

        _add_header(pdf_det, student, variant, percentage, score, total, elapsed_time, db_name)

        pdf_det.set_font("TNR", '', size=13)
        pdf_det.cell(0, 8, "Детальные результаты:", ln=True)
        pdf_det.ln(5)

        for i, q in enumerate(questions):
            user_ans_keys = answers.get(i, "")
            correct_keys = q['correct']
            q_time = int(question_times.get(i, 0))
            m_q, s_q = divmod(q_time, 60)
            time_str = f" [Время: {m_q:02d}:{s_q:02d}]"

            c_set = set(correct_keys.split(','))
            u_set = set(user_ans_keys.split(',')) if user_ans_keys else set()
            is_right = (c_set == u_set) and bool(user_ans_keys)

            if not user_ans_keys:
                status_text = "[НЕ ОТВЕЧЕНО]"
                pdf_det.set_text_color(120, 120, 120)  # Серый
            elif is_right:
                status_text = "[ВЕРНО]"
                pdf_det.set_text_color(0, 128, 0)      # Зеленый
            else:
                status_text = "[НЕВЕРНО]"
                pdf_det.set_text_color(255, 0, 0)    # Красный

            pdf_det.set_font("TNR", '', size=12)
            pdf_det.cell(0, 7, f"Вопрос {i+1}. {status_text}{time_str}", ln=True)

            pdf_det.set_font("TNR", '', size=10)
            pdf_det.set_x(20)
            pdf_det.multi_cell(0, 5, f"{q['question']}")
            pdf_det.set_text_color(0, 0, 0) # Возвращаем черный для остального текста
            
            u_texts = []
            if user_ans_keys:
                for k in user_ans_keys.split(','):
                    ans_text = q['options'].get(k, '')
                    u_texts.append(f"{k.upper()}) {ans_text}")
            u_ans_full = "; ".join(u_texts) if u_texts else "Не отвечено"
            
            pdf_det.set_x(20)
            pdf_det.multi_cell(0, 5, f"Ответ студента: {u_ans_full}")
            
            c_texts = []
            for k in correct_keys.split(','):
                ans_text = q['options'].get(k, '')
                c_texts.append(f"{k.upper()}) {ans_text}")
            c_ans_full = "; ".join(c_texts)
            
            pdf_det.set_text_color(0, 100, 0)
            pdf_det.set_x(20)
            pdf_det.multi_cell(0, 5, f"Правильный ответ: {c_ans_full}")
            pdf_det.set_text_color(0, 0, 0)
            
            exp = q.get('explanation', '')
            if exp:
                pdf_det.set_x(20)
                pdf_det.multi_cell(0, 5, f"Обоснование: {exp}")
            
            pdf_det.ln(4)
            
        filename_det = out_dir / f"report_detailed_{ts}.pdf"
        pdf_det.output(str(filename_det))
        
        # ==========================================
        # 2. КРАТКИЙ ОТЧЕТ
        # ==========================================
        pdf_br = FPDF()
        pdf_br.add_page()
        pdf_br.set_left_margin(15)
        pdf_br.set_right_margin(15)
        pdf_br.set_auto_page_break(auto=True, margin=20)
        pdf_br.add_font("TNR", "", FONTS_DIR / "timesnrcyrmt.ttf", uni=True)
        pdf_br.set_font("TNR", "", 12)
        
        _add_header(pdf_br, student, variant, percentage, score, total, elapsed_time, db_name)
        
        pdf_br.set_font("TNR", '', size=13)
        pdf_br.cell(0, 8, "Краткие результаты:", ln=True)
        pdf_br.ln(5)
        
        for i, q in enumerate(questions):
            user_ans_keys = answers.get(i, "")
            correct_keys = q['correct']
            
            c_set = set(correct_keys.split(','))
            u_set = set(user_ans_keys.split(',')) if user_ans_keys else set()
            is_right = (c_set == u_set) and bool(user_ans_keys)
            
            pdf_br.set_font("TNR", '', size=11)
            if not user_ans_keys:
                status_text = "НЕ ОТВЕЧЕНО"
                pdf_br.set_text_color(120, 120, 120)  # Серый
                pdf_br.cell(0, 6, f"Вопрос {i+1}: {status_text}", ln=True)
            elif is_right:
                status_text = "ВЕРНО"
                pdf_br.set_text_color(0, 128, 0)      # Зеленый
                u_ans_display = user_ans_keys.upper()
                pdf_br.cell(0, 6, f"Вопрос {i+1}: {status_text} (Ответ: {u_ans_display})", ln=True)
            else:
                status_text = "НЕВЕРНО"
                pdf_br.set_text_color(255, 0, 0)      # Красный
                u_ans_display = user_ans_keys.upper()
                pdf_br.cell(0, 6, f"Вопрос {i+1}: {status_text} (Ответ: {u_ans_display})", ln=True)
            
            pdf_br.set_text_color(0, 0, 0)
            
        filename_br = out_dir / f"report_brief_{ts}.pdf"
        pdf_br.output(str(filename_br))
        
        return str(filename_det)
        
    except Exception as e:
        print(f"PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return None

def get_number_of_test(student_dir):
    i = 1
    while os.path.exists(student_dir /Path(str(i))):
        i+=1
    return Path(str(i))

def generate_validator_pdf(validator, variant, questions, answers, validity, db_name, question_times=None):
    try:        
        if question_times is None: question_times = {}
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Создаем папку reports/validators/<login>/<variant_name>
        import re
        safe_db_name = re.sub(r'[\\/*?:"<>|]', "_", db_name)
        safe_variant_name = re.sub(r'[\\/*?:"<>|]', "_", variant)
        out_dir = REPORTS_DIR / "validators" / validator / f"{safe_db_name}_{safe_variant_name}"
        out_dir.mkdir(parents=True, exist_ok=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_auto_page_break(auto=True, margin=20)

        pdf.add_font("TNR", "", FONTS_DIR / "timesnrcyrmt.ttf", uni=True)
        pdf.set_font("TNR", "", 12)
        
        # Заголовок
        image_path = Path(DATA_DIR / "image.png")
        if image_path.exists():
            pdf.image(str(image_path), x=65, y=10, w=80)
            pdf.ln(95)
        else:
            pdf.ln(10)
        
        pdf.set_font("TNR", '', size=16)
        pdf.cell(0, 8, "КЛИНИКА ДОКТОРА РОШАЛЯ", ln=True, align='C')
        pdf.ln(2)
        
        pdf.set_font("TNR", '', size=24)
        pdf.cell(0, 12, "ОТЧЁТ ВАЛИДАТОРА", ln=True, align='C')
        pdf.ln(8)
        
        pdf.set_font("TNR", '', size=12)
        pdf.cell(0, 7, f"Версия БД: {db_name}", ln=True, align='C')
        pdf.cell(0, 7, f"Вариант: {variant}", ln=True, align='C')
        pdf.cell(0, 7, f"Валидатор: {validator}", ln=True, align='C')

        # Расчет статистики для заголовка
        total_q = len(questions)
        correct_q = 0
        for i, q in enumerate(questions):
            user_ans_keys = answers.get(i, "")
            if user_ans_keys:
                c_set = set(q.get('correct', '').split(','))
                u_set = set(user_ans_keys.split(','))
                if c_set == u_set:
                    correct_q += 1
        percentage = (correct_q / total_q * 100) if total_q > 0 else 0
        
        pdf.set_text_color(100, 100, 100) # Серый цвет для процента
        pdf.cell(0, 7, f"Результат: {percentage:.1f}% ({correct_q} из {total_q})", ln=True, align='C')
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(10)
        
        pdf.set_font("TNR", '', size=13)
        pdf.cell(0, 8, "Результаты валидации вопросов:", ln=True)
        pdf.ln(5)
        
        for i, q in enumerate(questions):
            user_ans_keys = answers.get(i, "")
            is_valid = validity.get(i, True)
            correct_keys = q.get('correct', '')
            q_time = int(question_times.get(i, 0))
            m_q, s_q = divmod(q_time, 60)
            time_str = f" [Время: {m_q:02d}:{s_q:02d}]"
            
            # Определяем статус ответа (три состояния)
            if not user_ans_keys:
                status_text = "не ответил"
                color = (120, 120, 120)  # Серый
            else:
                c_set = set(correct_keys.split(','))
                u_set = set(user_ans_keys.split(','))
                if c_set == u_set:
                    status_text = "ответил - верно"
                    color = (0, 128, 0)  # Зеленый
                else:
                    status_text = "ответил - не верно"
                    color = (255, 0, 0)  # Красный
            
            # Статус валидности
            status_valid = "ВАЛИДЕН" if is_valid else "НЕ ВАЛИДЕН"
            if not is_valid:
                color = (255, 0, 0)  # Если не валиден, всегда красный
            
            pdf.set_font("TNR", '', size=12)
            pdf.set_text_color(*color)
            pdf.cell(0, 7, f"Вопрос {i+1}. {status_text} | {status_valid}{time_str}", ln=True)
            pdf.set_text_color(0, 0, 0)
            
            pdf.set_font("TNR", '', size=10)
            pdf.set_x(20)
            pdf.multi_cell(0, 5, f"{q['question']}")
            
            # Ответ валидатора
            u_texts = []
            if user_ans_keys:
                for k in user_ans_keys.split(','):
                    ans_text = q['options'].get(k, '')
                    u_texts.append(f"{k.upper()}) {ans_text}")
            u_ans_full = "; ".join(u_texts) if u_texts else "Не отвечено"
            
            pdf.set_x(20)
            pdf.multi_cell(0, 5, f"Ответ валидатора: {u_ans_full}")

            # Правильный ответ
            c_texts = []
            if correct_keys:
                for k in correct_keys.split(','):
                    ans_text = q['options'].get(k, '')
                    c_texts.append(f"{k.upper()}) {ans_text}")
            c_ans_full = "; ".join(c_texts) if c_texts else "Не указан"
            
            pdf.set_text_color(0, 100, 0) # Темно-зеленый для правильного ответа
            pdf.set_x(20)
            pdf.multi_cell(0, 5, f"Правильный ответ: {c_ans_full}")
            pdf.set_text_color(0, 0, 0)

            # Обоснование
            exp = q.get('explanation', '')
            if exp and str(exp).lower() != 'nan':
                pdf.set_x(20)
                pdf.multi_cell(0, 5, f"Обоснование: {exp}")
            
            pdf.ln(4)
            
        filename = out_dir / f"validator_report_{ts}.pdf"
        pdf.output(str(filename))
        return str(filename)
        
    except Exception as e:
        print(f"Validator PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return None
