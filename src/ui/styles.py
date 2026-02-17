DARK_QSS = """
QMainWindow, QWidget {
    background-color: #0F1117;
    color: #E2E8F0;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
}

QWidget#nav_panel {
    background-color: #161B27;
    border-right: 1px solid #2D3748;
}

QPushButton#nav_btn_empty {
    background-color: #2D3748;
    color: #A0AEC0;
    border: 1px solid #3D4F6E;
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
    border: 1px solid #38A169;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
}
QPushButton#nav_btn_skipped {
    background-color: #9C4221;
    color: #FFFFFF;
    border: 1px solid #DD6B20;
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
QPushButton#action_btn:hover {
    background-color: #3182CE;
}

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
QPushButton#success_btn:hover {
    background-color: #38A169;
}

QPushButton#danger_btn {
    background-color: #C53030;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    font-size: 14px;
    font-weight: 600;
}

QFrame#question_card {
    background-color: #1A202C;
    border: 1px solid #2D3748;
    border-radius: 12px;
}

QLabel#question_label {
    color: #F7FAFC;
    font-size: 16px;
    font-weight: 600;
    background-color: transparent;
}

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

QLineEdit, QComboBox {
    background-color: #1A202C;
    color: #E2E8F0;
    border: 1px solid #4A5568;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 14px;
    min-height: 40px;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #3182CE;
}

QComboBox QAbstractItemView {
    background-color: #1A202C;
    color: #E2E8F0;
    selection-background-color: #2B6CB0;
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
"""
