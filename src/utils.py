import cv2
import pyautogui
import datetime
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from fpdf import FPDF
from src.config import REPORTS_DIR

# --- ПРОКТОРИНГ ---

class ProctorThread(QThread):
    screenshot_taken = pyqtSignal(str)
    
    def __init__(self, student_name, interval=30):
        super().__init__()
        self.student_dir = REPORTS_DIR / student_name
        self.student_dir.mkdir(exist_ok=True, parents=True)
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            self.sleep(self.interval)
            if not self._running: break
            try:
                ts = datetime.datetime.now().strftime("%H%M%S")
                path = self.student_dir / f"scr_{ts}.png"
                pyautogui.screenshot().save(path)
                self.screenshot_taken.emit(str(path))
            except Exception:
                pass

    def stop(self):
        self._running = False
        self.quit()
        self.wait(2000) # Ждем не более 2 сек

class WebcamThread(QThread):
    def __init__(self, student_name, interval=60):
        super().__init__()
        self.student_dir = REPORTS_DIR / student_name
        self.interval = interval
        self._running = True

    def run(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened(): return
            
            while self._running:
                self.sleep(self.interval)
                if not self._running: break
                
                ret, frame = cap.read()
                if ret:
                    ts = datetime.datetime.now().strftime("%H%M%S")
                    path = self.student_dir / f"cam_{ts}.jpg"
                    cv2.imwrite(str(path), frame)
            cap.release()
        except Exception:
            pass

    def stop(self):
        self._running = False
        self.quit()
        self.wait(2000)

# --- PDF ---

def generate_pdf(student, category, questions, answers, score, total):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=12) # Внимание: для кириллицы нужен шрифт DejaVu/Arial!
        
        pdf.cell(0, 10, f"Report: {student}", ln=True)
        pdf.cell(0, 10, f"Score: {score}/{total} ({round(score/total*100)}%)", ln=True)
        pdf.ln(5)
        
        for i, q in enumerate(questions):
            user_ans = answers.get(i, "-")
            correct = q['correct']
            
            # Логика Fix 4: Сравнение множеств
            c_set = set(correct.split(','))
            u_set = set(user_ans.split(','))
            is_right = (c_set == u_set)
            
            status = "[OK]" if is_right else "[WRONG]"
            # Очищаем текст от кириллицы если шрифт стандартный, иначе крашнет
            # В реальном проекте подключите .ttf шрифт
            pdf.cell(0, 8, f"Q{i+1}: {status} Your: {user_ans} | Correct: {correct}", ln=True)
            
        filename = REPORTS_DIR / student / f"report_{datetime.datetime.now().strftime('%H%M%S')}.pdf"
        pdf.output(str(filename))
        return str(filename)
    except Exception as e:
        print(f"PDF Error: {e}")
        return None
