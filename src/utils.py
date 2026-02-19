import pyautogui
import datetime
from pathlib import Path
from PyQt6.QtCore import QThread, pyqtSignal
from fpdf import FPDF
import os
from pathlib import Path
from src.config import REPORTS_DIR, BLACK_LIST
from PIL import ImageGrab
import psutil

# --- ПРОКТОРИНГ ---

class ProctorThread(QThread):    
    def __init__(self, student_name,test_number: Path, interval=5):
        super().__init__()
        self.screens_dir = REPORTS_DIR  / student_name/ test_number / "screens"
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
                # self._take_screenshot(path)
            except Exception:
                pass

            self.sleep(self.interval)
    
    def _take_screenshot(filepath: Path): # ---------------- если на windows не рабоатет создание скриншота ----------------
        """Делает скриншот экрана и сохраняет в файл."""
        try:
            # Делаем скриншот
            screenshot = ImageGrab.grab()
            
            # Сохраняем
            screenshot.save(filepath, "PNG")
            
        except Exception as e:
            pass        

    def stop(self):
        self._running = False
        self.quit()
        # self.wait(2000) # Ждем не более 2 сек

class ScanningThread(QThread):
    violation_detected = pyqtSignal(set)

    def __init__(self, interval = 1):
        super().__init__()
        self.interval = interval
        self._running = True

    def run(self):
        while self._running:
            if not self._running: break
            try:
                violation = self._check_blacklisted_apps()
                if violation:
                    self.violation_detected.emit(violation)
            except Exception:
                pass

            self.sleep(self.interval)

    def _check_blacklisted_apps(self):
        """Проверяет процессы и окна. Возвращает название нарушения или пустую строку"""
        try:
            s = set()
            # 1. Проверка процессов (psutil)
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(bl in proc_name for bl in BLACK_LIST):
                        s.add(proc.info['name'])
                        # return f"Запрещённый процесс: {proc.info['name']}"
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # 2. Проверка окон (Windows: powershell WMI)
            if os.name == "nt":  # Windows
                try:
                    result = subprocess.run([
                        "powershell",
                        "-Command",
                        "Get-Process | Where-Object {$_.MainWindowTitle} | Select-Object -ExpandProperty MainWindowTitle"
                    ], capture_output=True, text=True, timeout=3)
                    
                    window_titles = [title.strip().lower() for title in result.stdout.split('\n') if title.strip()]
                    
                    for title in window_titles:
                        if any(bl in title for bl in BLACK_LIST):
                            s.add(title)
                            
                except subprocess.TimeoutExpired:
                    pass
            
        except Exception:
            pass
        return s

    def stop(self):
        self._running = False
        self.quit()


# --- PDF ---
def generate_pdf(student, test_number: Path, category, questions, answers, score, total):
    try:        
        pdf = FPDF()
        pdf.add_page()
        
         # Устанавливаем отступы от краев страницы
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_auto_page_break(auto=True, margin=20)

        # === ПОДКЛЮЧЕНИЕ UNICODE ШРИФТА ===
        pdf.add_font("TNR", "", "fonts/timesnrcyrmt.ttf", uni=True)

        pdf.set_font("TNR", "", 12)  # Установка шрифта по умолчанию

         # === ЛОГОТИП (БОЛЬШОЙ И ПО ЦЕНТРУ) === 
        image_path = Path("image.png")
        if image_path.exists():
            # Центрируем: (210мм ширина - 80мм картинка) / 2 = 65мм от левого края
            pdf.image(str(image_path), x=65, y=10, w=80)
            pdf.ln(95)  # Отступ после логотипа
        else:
            pdf.ln(10)
        
        # === ЗАГОЛОВОК "КЛИНИКА ДОКТОРА РОШАЛЯ" ===
        pdf.set_font("TNR", '', size=16)
        pdf.cell(0, 8, "КЛИНИКА ДОКТОРА РОШАЛЯ", ln=True, align='C')
        pdf.ln(2)
        
        # === ЗАГОЛОВОК "ОТЧЁТ" ===
        pdf.set_font("TNR", '', size=24)
        pdf.cell(0, 12, "ОТЧЁТ", ln=True, align='C')
        pdf.ln(8)
        
        # === ФИО СТУДЕНТА ===
        pdf.set_font("TNR", '', size=14)
        pdf.cell(0, 8, f"Студент: {student}", ln=True, align='C')
        pdf.ln(2)
        
        # === КАТЕГОРИЯ ===
        pdf.set_font("TNR", '', size=12)
        pdf.cell(0, 7, f"Категория: {category}", ln=True, align='C')
        pdf.ln(6)
        
        # === ПРОЦЕНТ И СООТНОШЕНИЕ ===
        percentage = round(score / total * 100) if total > 0 else 0
        pdf.set_font("TNR", '', size=14)

        if percentage >= 60:
            pdf.set_text_color(0, 128, 0)  # Зеленый
        else:
            pdf.set_text_color(255, 0, 0)  # Красный
        
        pdf.cell(0, 8, f"Результат: {percentage}%", ln=True, align='C')
        
        pdf.set_font("TNR", '', size=11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 7, f"Правильных ответов: {score} из {total}", ln=True, align='C')
        pdf.ln(10)
        
        # === РАЗДЕЛИТЕЛЬ ===
        pdf.set_draw_color(180, 180, 180)
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(10)
        
        # === ДЕТАЛЬНЫЕ РЕЗУЛЬТАТЫ ===
        pdf.set_font("TNR", '', size=13)
        pdf.cell(0, 8, "Детальные результаты:", ln=True)
        pdf.ln(5)
        
        for i, q in enumerate(questions):
            user_ans = answers.get(i, "Не отвечено")
            correct = q['correct']
            
            # Сравнение множеств
            c_set = set(correct.split(','))
            u_set = set(user_ans.split(','))
            is_right = (c_set == u_set)
            
            # === НОМЕР И СТАТУС ===
            if is_right:
                status_text = "[ВЕРНО]"
                pdf.set_text_color(0, 128, 0)  # Зеленый
            else:
                status_text = "[НЕВЕРНО]"
                pdf.set_text_color(255, 0, 0)  # Красный
            
            pdf.set_font("TNR", '', size=12)
            pdf.cell(0, 7, f"{i+1}. {status_text}", ln=True)
            pdf.set_text_color(0, 0, 0)
            
            # === ТЕКСТ ВОПРОСА (с переносом строк) ===
            pdf.set_font("TNR", '', size=10)
            question_text = q['question']
            # Добавляем отступ слева для текста вопроса
            pdf.set_x(20)
            pdf.multi_cell(0, 5, f"Вопрос: {question_text}")
            
            # === ОТВЕТ СТУДЕНТА ===
            pdf.set_font("TNR", '', size=10)
            pdf.set_x(20)
            # Используем multi_cell чтобы длинный текст не обрезался
            pdf.multi_cell(0, 5, f"Ваш ответ: {user_ans}")
            
            # === ПРАВИЛЬНЫЙ ОТВЕТ ===
            pdf.set_font("TNR", '', size=10)
            pdf.set_text_color(0, 100, 0)
            pdf.set_x(20)
            pdf.multi_cell(0, 5, f"Правильный ответ: {correct}")
            pdf.set_text_color(0, 0, 0)
            
            pdf.ln(4)  # Отступ между вопросами
        
        # === СОХРАНЕНИЕ ===
        filename = REPORTS_DIR / student / test_number /f"report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filename.parent.mkdir(parents=True, exist_ok=True)
        pdf.output(str(filename))
        return str(filename)
        
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