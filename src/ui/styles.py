DARK_QSS = """
/* === ОБЩИЕ НАСТРОЙКИ === */
QMainWindow, QWidget {
    background-color: #0F1117;
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QWidget#nav_panel {
    background-color: #161B27;
    border-right: 2px solid #2D3748;
    border-radius: 6px;
}

/* === КНОПКИ === */
QPushButton#nav_btn_empty {
    background-color: #2D3748;
    color: #A0AEC0;
    border: 2px solid #3D4F6E;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#nav_btn_active {
    background-color: #2B6CB0;
    color: #FFFFFF;
    border: 2px solid #4299E1;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 700;
}
QPushButton#nav_btn_answered {
    background-color: #276749;
    color: #FFFFFF;
    border: 2px solid #38A169;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#nav_btn_skipped {
    background-color: #171D28;
    color: #FFFFFF;
    border: 2px solid #2D3748;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}

QPushButton#action_btn {
    background-color: #2B6CB0;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}
QPushButton#action_btn:hover { background-color: #3182CE; }

QPushButton#success_btn {
    background-color: #276749;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}
QPushButton#success_btn:hover { background-color: #38A169; }

QPushButton#danger_btn {
    background-color: #C53030;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}

QPushButton#skip_btn {
    background-color: #9C4221;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
    min-height: 40px;
}

QPushButton#skip_btn:hover { background-color: #B14B25; }

/* === КАРТОЧКИ И ТЕКСТ === */
QFrame#question_card {
    background-color: #1A202C;
    border: 2px solid #2D3748;
    border-radius: 12px;
}

QLabel#question_label {
    color: #F7FAFC;
    font-size: 16px;
    font-weight: 600;
    background-color: transparent;
}

QLabel#section_title {
    color: #A0AEC0;
    font-size: 11px;
    font-weight: 700;
    background-color: transparent;
}

QLabel#app_title {
    font-size: 32px;
    font-weight: 800;
    color: #90CDF4;
    background-color: transparent;
}

/* === ВВОД ДАННЫХ === */
QRadioButton, QCheckBox {
    color: #CBD5E0;
    font-size: 14px;
    spacing: 12px;
    padding: 10px 12px;
    background-color: transparent;
}
QRadioButton:hover, QCheckBox:hover {
    background-color: #1E2A3A;
    color: #EDF2F7;
}
QRadioButton:checked, QCheckBox:checked {
    background-color: #1A365D;
    color: #90CDF4;
    font-weight: 600;
}

QLineEdit {
    background-color: #1A202C;
    color: #E2E8F0;
    border: 2px solid #4A5568;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    min-height: 40px;
}
QLineEdit:focus { border-color: #3182CE; }

/* === COMBOBOX (БЕЗ СТРЕЛКИ) === */
QComboBox {
    background-color: #1A202C;
    color: #E2E8F0;
    border: 2px solid #4A5568;
    border-radius: 8px;
    padding: 8px 16px;
    font-size: 14px;
    min-height: 40px;
    selection-background-color: #2B6CB0;
}

QComboBox:hover {
    border: 2px solid #3182CE;
    background-color: #232936;
}

QComboBox:focus {
    border: 2px solid #3182CE;
    padding: 7px 15px;
}

/* Кнопка выпадающего списка */
QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 40px;
    border-left-width: 0px;
    border-top-right-radius: 8px;
    border-bottom-right-radius: 8px;
}

/* Сама стрелка - СКРЫТА */
QComboBox::down-arrow {
    image: none;
    border: none;
    width: 0px; 
    height: 0px;
}

/* Выпадающий список (Popup) */
QComboBox QAbstractItemView {
    background-color: #1A202C;
    border: 2px solid #2D3748;
    border-radius: 8px;
    color: #E2E8F0;
    selection-background-color: #2B6CB0;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}

QComboBox QAbstractItemView::item {
    padding: 8px 10px;
    min-height: 30px;
}

/* === ТАЙМЕР === */
QLabel#timer_label {
    color: #F6E05E;           /* Желтый текст (как было) */
    background-color: #1A202C; /* Темно-синий фон (как у карточек) */
    border: 2px solid #2D3748; /* Тонкая рамка */
    border-radius: 8px;        /* Скругленные углы */
    padding: 6px 12px;         /* Отступы внутри */
    font-size: 20px;
    font-weight: 700;
    font-family: 'Consolas', 'Courier New', monospace; /* Моноширинный шрифт для цифр */
}

/* === ВОПРОС === */
QLabel#question_label {
    color: #FFFFFF;
    font-size: 20px; /* Крупнее */
    font-weight: 700;
    margin-bottom: 20px; /* Отступ от вопроса до ответов */
    background-color: transparent;
    line-height: 1.4;
}

QWidget#question_layout {
    color: #FFFFFF;
    font-size: 20px; /* Крупнее */
    font-weight: 700;
    margin-bottom: 20px; /* Отступ от вопроса до ответов */
    background-color: transparent;
    line-height: 1.4;
}

/* === ВАРИАНТЫ ОТВЕТОВ === */
QRadioButton, QCheckBox {
    color: #CBD5E0;
    font-size: 16px;
    font-weight: 500;
    spacing: 12px;
    padding: 14px 20px;
    /* Обычное состояние: фон карточки, тонкая серая рамка (или без неё) */
    border-radius: 12px;
    border: 2px solid #2D3748; /* Едва заметная рамка для структуры */
}

/* === ЭФФЕКТ НАВЕДЕНИЯ (HOVER) === */
QRadioButton:hover, QCheckBox:hover {
    /* При наведении: яркая синяя рамка, как на скриншоте */
    border: 2px solid #63B3ED; 
    background-color: #232936; /* Чуть светлее фон */
    color: #FFFFFF;
}

/* === ВЫБРАННЫЙ ВАРИАНТ (CHECKED) === */
QRadioButton:checked, QCheckBox:checked {
    /* Когда выбран: синяя заливка (или просто жирная синяя рамка) */
    background-color: #2B6CB0; 
    border: 2px solid #4299E1;
    color: #FFFFFF;
    font-weight: 700;
}

/* === ИНДИКАТОРЫ (Кружки/Квадраты) === */
QRadioButton::indicator {
    width: 24px; height: 24px;
    border-radius: 13px;
    border: 2px solid #A0AEC0; /* Серый кружок */
    background: transparent;
    margin-right: 10px;
}
QCheckBox::indicator {
    width: 24px; height: 24px;
    border-radius: 6px;
    border: 2px solid #A0AEC0;
    background: transparent;
    margin-right: 10px;
}

/* Активный индикатор */
QRadioButton::indicator:checked, QCheckBox::indicator:checked {
    border-color: #FFFFFF;
    background-color: #FFFFFF;
}

QRadioButton::indicator:checked {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%232B6CB0'><circle cx='12' cy='12' r='6'/></svg>");
}
QCheckBox::indicator:checked {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%232B6CB0' stroke-width='4' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'/></svg>");
}

QWidget#nav_grid_container {
    background-color: transparent;     /* Темный фон (как основной фон окна) или #1A202C */
}

/* --- СКРОЛЛБАР (ТЕМНАЯ ТЕМА) --- */
QScrollBar:vertical {
    border: none;
    background-color: #2D3748; /* Фон канала такой же, как у списка */
    width: 12px;               /* Чуть шире для удобства */
    margin: 0px;
    border-radius: 0px;
}

/* Ползунок (ручка) */
QScrollBar::handle:vertical {
    background-color: #4A5568; /* Темно-серый ползунок */
    min-height: 20px;
    border-radius: 6px;        /* Закругленные края */
    margin: 2px;               /* Отступ от краев канала */
}

/* Ползунок при наведении */
QScrollBar::handle:vertical:hover {
    background-color: #718096; /* Светлее при наведении */
}

/* Ползунок при нажатии */
QScrollBar::handle:vertical:pressed {
    background-color: #A0AEC0; /* Еще светлее при клике */
}

/* Скрываем стрелки вверх/вниз */
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    border: none;
    background: none;
    height: 0px;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: none;
}
"""
