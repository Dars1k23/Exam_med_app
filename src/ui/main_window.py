from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.styles import DARK_QSS
from src.ui.screens import CategoryScreen, LoginScreen, NameScreen, TestScreen, ResultScreen

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Exam System")
        self.resize(1000, 700)
        self.setStyleSheet(DARK_QSS)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self._show_category()

    def _show_category(self):
        self.cat_scr = CategoryScreen()
        self.cat_scr.next_step.connect(self._show_login)
        self._set_screen(self.cat_scr)

    def _show_login(self, category):
        self.login_scr = LoginScreen(category)
        self.login_scr.back.connect(self._show_category)
        self.login_scr.success.connect(lambda: self._show_name(category))
        self._set_screen(self.login_scr)

    def _show_name(self, category):
        self.name_scr = NameScreen()
        self.name_scr.back.connect(lambda: self._show_login(category))
        self.name_scr.start_test.connect(lambda name: self._start_test(name, category))
        self._set_screen(self.name_scr)

    def _start_test(self, student, category):
        self.test_scr = TestScreen(student, category)
        self.test_scr.finished.connect(self._show_result)
        self._set_screen(self.test_scr)

    def _show_result(self, data):
        self.res_scr = ResultScreen(data)
        self.res_scr.logout.connect(self._show_category)
        self._set_screen(self.res_scr)

    def _set_screen(self, widget):
        # Удаляем старый виджет, чтобы остановить таймеры/потоки (через closeEvent)
        current = self.stack.currentWidget()
        if current:
            current.close() # Важно для остановки потоков
            self.stack.removeWidget(current)
            current.deleteLater()
        
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
