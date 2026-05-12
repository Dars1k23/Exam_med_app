import cv2
import sys
import pyautogui
import datetime
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from fpdf import FPDF
import os
from pathlib import Path
from src.config import REPORTS_DIR, FONTS_DIR, DATA_DIR

# --- ПРОКТОРИНГ ---

class ProctorThread(QThread):
    screenshot_taken = pyqtSignal(str)
    
    def __init__(self, student_name, test_dir_name: Path, interval=30):
        super().__init__()
        self.screens_dir = REPORTS_DIR  / student_name/ test_dir_name / "screens"
        self.screens_dir.mkdir(exist_ok=True, parents=True)
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            if not self._running: break
            try:
                ts = datetime.datetime.now().strftime("%H%M%S")
                path = self.screens_dir / f"scr_{ts}.png"
                pyautogui.screenshot().save(path)
                self.screenshot_taken.emit(str(path))
            except Exception:
                pass

            self.sleep(self.interval)

    def stop(self):
        self._running = False
        self.quit()
        # self.wait(2000) # Ждем не более 2 сек

class WebcamThread(QThread):
    def __init__(self, student_name, test_number: Path, interval=30):
        super().__init__()
        self.photos_dir = REPORTS_DIR / student_name / test_number / "photos"
        self.photos_dir.mkdir(exist_ok=True, parents=True)
        self.interval = interval
        self._running = True

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): return
            
            while self._running:
                if not self._running: break
                
                ret, frame = cap.read()
                if ret:
                    ts = datetime.datetime.now().strftime("%H%M%S")
                    path = self.photos_dir /f"cam_{ts}.jpg"
                    cv2.imwrite(str(path), frame)

                self.sleep(self.interval)
            cap.release()
        except Exception:
            pass

    def stop(self):
        self._running = False
        self.quit()
        # self.wait(2000)

# --- PDF ---
def _add_header(pdf, student, kr, percentage, score, total, elapsed_time, db_name):
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
    pdf.multi_cell(0, 7, f"Номер КР: {kr}", ln=True, align='C')
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


def generate_pdf(student, test_dir_name: Path, kr, questions, answers, score, total, elapsed_time, db_name):
    try:        
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
        
        _add_header(pdf_det, student, kr, percentage, score, total, elapsed_time, db_name)
        
        pdf_det.set_font("TNR", '', size=13)
        pdf_det.cell(0, 8, "Детальные результаты:", ln=True)
        pdf_det.ln(5)
        
        for i, q in enumerate(questions):
            user_ans_keys = answers.get(i, "")
            correct_keys = q['correct']
            
            c_set = set(correct_keys.split(','))
            u_set = set(user_ans_keys.split(',')) if user_ans_keys else set()
            is_right = (c_set == u_set) and bool(user_ans_keys)
            
            if is_right:
                status_text = "[ВЕРНО]"
                pdf_det.set_text_color(0, 128, 0)
            else:
                status_text = "[НЕВЕРНО]"
                pdf_det.set_text_color(255, 0, 0)
                
            pdf_det.set_font("TNR", '', size=12)
            pdf_det.cell(0, 7, f"Вопрос {i+1}. {status_text}", ln=True)
            pdf_det.set_text_color(0, 0, 0)
            
            pdf_det.set_font("TNR", '', size=10)
            pdf_det.set_x(20)
            pdf_det.multi_cell(0, 5, f"{q['question']}")
            
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
        
        _add_header(pdf_br, student, kr, percentage, score, total, elapsed_time, db_name)
        
        pdf_br.set_font("TNR", '', size=13)
        pdf_br.cell(0, 8, "Краткие результаты:", ln=True)
        pdf_br.ln(5)
        
        for i, q in enumerate(questions):
            user_ans_keys = answers.get(i, "")
            correct_keys = q['correct']
            
            c_set = set(correct_keys.split(','))
            u_set = set(user_ans_keys.split(',')) if user_ans_keys else set()
            is_right = (c_set == u_set) and bool(user_ans_keys)
            
            if is_right:
                status_text = "ВЕРНО"
            else:
                status_text = "НЕВЕРНО"
                
            u_ans_display = user_ans_keys.upper() if user_ans_keys else "Не отвечено"
            
            pdf_br.set_font("TNR", '', size=11)
            if is_right:
                pdf_br.set_text_color(0, 128, 0)
            else:
                pdf_br.set_text_color(255, 0, 0)
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

def generate_validator_pdf(validator, kr, questions, answers, validity, db_name):
    try:        
        ts = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Создаем папку reports/validators/<login>/<kr_name>
        import re
        safe_db_name = re.sub(r'[\\/*?:"<>|]', "_", db_name)
        safe_kr_name = re.sub(r'[\\/*?:"<>|]', "_", kr)
        out_dir = REPORTS_DIR / "validators" / validator / f"{safe_db_name}_{safe_kr_name}"
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
        pdf.cell(0, 7, f"Номер КР: {kr}", ln=True, align='C')
        pdf.cell(0, 7, f"Валидатор: {validator}", ln=True, align='C')
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
            
            # Статус решения
            status_solved = "РЕШИЛ" if user_ans_keys else "НЕ РЕШИЛ"
            
            # Статус валидности
            status_valid = "ВАЛИДЕН" if is_valid else "НЕ ВАЛИДЕН"
            
            pdf.set_font("TNR", '', size=12)
            
            if is_valid:
                pdf.set_text_color(0, 128, 0)
            else:
                pdf.set_text_color(255, 0, 0)
                
            pdf.cell(0, 7, f"Вопрос {i+1}. {status_solved} | {status_valid}", ln=True)
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
            
            pdf.ln(4)
            
        filename = out_dir / f"validator_report_{ts}.pdf"
        pdf.output(str(filename))
        return str(filename)
        
    except Exception as e:
        print(f"Validator PDF Generation Error: {e}")
        import traceback
        traceback.print_exc()
        return None