from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QMessageBox
from src.ui.styles import DARK_QSS
from src.ui.screens import (DatabaseScreen, NameScreen, VariantScreen, TestScreen, ResultScreen,
                            ValidatorLoginScreen, ValidatorDatabaseScreen, ValidatorVariantScreen, ValidatorTestScreen, ValidatorResultScreen)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medical Exam System")
        self.resize(1000, 700)
        self.setStyleSheet(DARK_QSS)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self._show_name()

    def closeEvent(self, event):
        # Если текущий экран - тест (студента или валидатора), спрашиваем подтверждение
        current = self.stack.currentWidget()
        if isinstance(current, (TestScreen, ValidatorTestScreen)):
            box = QMessageBox(self)
            box.setWindowTitle("Выход")
            box.setText("Тестирование еще не завершено. Вы уверены, что хотите закрыть приложение?")
            box.setIcon(QMessageBox.Icon.Question)
            yes_btn = box.addButton("Да", QMessageBox.ButtonRole.YesRole)
            no_btn = box.addButton("Нет", QMessageBox.ButtonRole.NoRole)
            box.exec()
            
            if box.clickedButton() == yes_btn:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    # --- РЕЖИМ СТУДЕНТА ---
    def _show_name(self):
        self.name_scr = NameScreen()
        self.name_scr.next_step.connect(self._show_database)
        self.name_scr.go_validator.connect(self._show_validator_login)
        self._set_screen(self.name_scr)

    def _show_database(self, name):
        self.db_scr = DatabaseScreen()
        self.db_scr.back.connect(self._show_name)
        self.db_scr.start_test.connect(lambda db_path: self._show_variant(name, db_path))
        self._set_screen(self.db_scr)

    def _show_variant(self, name, db_path):
        self.variant_scr = VariantScreen(db_path, is_validator=False)
        self.variant_scr.back.connect(lambda: self._show_database(name))
        self.variant_scr.start_test.connect(lambda variant_name: self._start_test(name, db_path, variant_name))
        self._set_screen(self.variant_scr)

    def _start_test(self, student, db_path, variant_name):
        self.test_scr = TestScreen(student, db_path, variant_name)
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
        self.v_db_scr.start_test.connect(lambda db_path: self._show_validator_variant(validator_login, db_path))
        self._set_screen(self.v_db_scr)

    def _show_validator_variant(self, validator_login, db_path):
        self.v_variant_scr = ValidatorVariantScreen(db_path, is_validator=True)
        self.v_variant_scr.back.connect(lambda: self._show_validator_db(validator_login))
        self.v_variant_scr.start_test.connect(lambda variant_name: self._start_validator_test(validator_login, db_path, variant_name))
        self._set_screen(self.v_variant_scr)

    def _start_validator_test(self, validator_login, db_path, variant_name):
        self.v_test_scr = ValidatorTestScreen(validator_login, db_path, variant_name)
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
