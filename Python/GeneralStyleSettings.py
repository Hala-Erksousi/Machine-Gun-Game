from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
BLACK_STYLE = """
    QWidget {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0a0a0a, stop:1 #1a1a1a);
        color: white;
        font-family: "Segoe UI", "Arial", sans-serif;
    }
    QLabel {
        color: white;
    }
    QPushButton {
        padding: 12px 25px;
        border-radius: 10px;
        border: none;
        font-weight: bold;
        transition: all 0.2s ease-in-out; 
    }
    QPushButton:hover {
        background-color: #555555;
        transform: scale(1.05); 
    }
    QPushButton:pressed {
        background-color: #333333;
        transform: scale(0.95); 
        border: 2px solid #00ffff;
    }
    QLineEdit {
        border-radius: 8px;
        padding: 8px;
        background-color: #f0f0f0;
        color: #333333;
        border: 1px solid #555555;
    }
    QLineEdit:focus {
        border: 2px solid #00aaff;
    }
"""

def set_black_background(widget):
    widget.setStyleSheet(BLACK_STYLE)

# --- Helper functions for consistent styling ---
def create_styled_label(text, font_size, bold=True, color="white", alignment=Qt.AlignCenter, letter_spacing="0px"):
    label = QLabel(text)
    font = QFont("Arial", font_size)
    if bold:
        font.setWeight(QFont.Bold)
    label.setFont(font)
    label.setStyleSheet(f"color: {color}; letter-spacing: {letter_spacing};")
    label.setAlignment(alignment)
    return label

def create_styled_button(text, font_size, bg_color, hover_color, pressed_color, callback):
    button = QPushButton(text)
    button.setFont(QFont("Arial", font_size, QFont.Bold))
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: {bg_color};
            color: white;
            min-width: 250px;
            min-height: 70px;
            border-radius: 12px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
        QPushButton:pressed {{
            background-color: {pressed_color};
            border: 2px solid #00ffff;
        }}
    """)
    button.clicked.connect(callback)
    
    shadow = QGraphicsDropShadowEffect(button)
    shadow.setBlurRadius(20)
    shadow.setOffset(5, 5)
    shadow.setColor(QColor(0, 0, 0, 150))
    button.setGraphicsEffect(shadow)
    return button

def create_styled_line_edit(placeholder, fixed_width, fixed_height, font_size, alignment=Qt.AlignCenter):
    line_edit = QLineEdit()
    line_edit.setFixedSize(fixed_width, fixed_height)
    line_edit.setFont(QFont("Arial", font_size))
    line_edit.setPlaceholderText(placeholder)
    line_edit.setAlignment(alignment)
    return line_edit