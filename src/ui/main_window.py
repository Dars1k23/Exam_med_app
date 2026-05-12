from PyQt6.QtWidgets import QMainWindow, QStackedWidget
from src.ui.styles import DARK_QSS
from src.ui.screens import (DatabaseScreen, NameScreen, KRScreen, TestScreen, ResultScreen,
                            ValidatorLoginScreen, ValidatorDatabaseScreen, ValidatorKRScreen, ValidatorTestScreen, ValidatorResultScreen)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Exam System")
        self.resize(1000, 700)
        self.setStyleSheet(DARK_QSS)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self._show_name()

    # --- РЕЖИМ СТУДЕНТА ---
    def _show_name(self):
        self.name_scr = NameScreen()
        self.name_scr.next_step.connect(self._show_database)
        self.name_scr.go_validator.connect(self._show_validator_login)
        self._set_screen(self.name_scr)

    def _show_database(self, name):
        self.db_scr = DatabaseScreen()
        self.db_scr.back.connect(self._show_name)
        self.db_scr.start_test.connect(lambda db_path: self._show_kr(name, db_path))
        self._set_screen(self.db_scr)

    def _show_kr(self, name, db_path):
        self.kr_scr = KRScreen(db_path)
        self.kr_scr.back.connect(lambda: self._show_database(name))
        self.kr_scr.start_test.connect(lambda kr_name: self._start_test(name, db_path, kr_name))
        self._set_screen(self.kr_scr)

    def _start_test(self, student, db_path, kr_name):
        self.test_scr = TestScreen(student, db_path, kr_name)
        self.test_scr.finished.connect(self._show_result)
        self._set_screen(self.test_scr)

    def _show_result(self, data):
        self.res_scr = ResultScreen(data)
        self.res_scr.logout.connect(self._show_name)
        self._set_screen(self.res_scr)

    # --- РЕЖИМ ВАЛИДАТОРА ---
    def _show_validator_login(self):
        self.v_login_scr = ValidatorLoginScreen()
        self.v_login_scr.back.connect(self._show_name)
        self.v_login_scr.success.connect(self._show_validator_db)
        self._set_screen(self.v_login_scr)

    def _show_validator_db(self, validator_login):
        self.v_db_scr = ValidatorDatabaseScreen()
        self.v_db_scr.back.connect(self._show_validator_login)
        self.v_db_scr.start_test.connect(lambda db_path: self._show_validator_kr(validator_login, db_path))
        self._set_screen(self.v_db_scr)

    def _show_validator_kr(self, validator_login, db_path):
        self.v_kr_scr = ValidatorKRScreen(db_path)
        self.v_kr_scr.back.connect(lambda: self._show_validator_db(validator_login))
        self.v_kr_scr.start_test.connect(lambda kr_name: self._start_validator_test(validator_login, db_path, kr_name))
        self._set_screen(self.v_kr_scr)

    def _start_validator_test(self, validator_login, db_path, kr_name):
        self.v_test_scr = ValidatorTestScreen(validator_login, db_path, kr_name)
        self.v_test_scr.finished.connect(self._show_validator_result)
        self._set_screen(self.v_test_scr)

    def _show_validator_result(self, data):
        self.v_res_scr = ValidatorResultScreen(data)
        self.v_res_scr.logout.connect(self._show_name)
        self._set_screen(self.v_res_scr)

    def _set_screen(self, widget):
        # Удаляем старый виджет, чтобы остановить таймеры/потоки (через closeEvent)
        current = self.stack.currentWidget()
        if current:
            current.close() # Важно для остановки потоков
            self.stack.removeWidget(current)
            current.deleteLater()
        
        self.stack.addWidget(widget)
        self.stack.setCurrentWidget(widget)
