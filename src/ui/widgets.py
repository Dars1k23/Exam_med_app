from PyQt6.QtWidgets import QPushButton, QLabel, QFrame, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt

class ActionButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("action_btn")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class SuccessButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("success_btn")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class DangerButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("danger_btn")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

class QuestionCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("question_card")
        self.layout = QVBoxLayout(self)
        self.layout.setSpacing(14)
        self.layout.setContentsMargins(32, 28, 32, 28)

    def add_widget(self, widget):
        self.layout.addWidget(widget)

class AppTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("app_title")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

class SectionTitle(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("section_title")

class IconLabel(QLabel):
    """Для больших иконок (⚕, 🔒, 👤)"""
    def __init__(self, icon, color=None, parent=None):
        super().__init__(icon, parent)
        style = "font-size: 72px;"
        if color:
            style += f" color: {color};"
        self.setStyleSheet(style)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
