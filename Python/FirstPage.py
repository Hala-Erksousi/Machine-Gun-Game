from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
import GeneralStyleSettings as GS
class FirstPage(QWidget):
    def __init__(self, start_game_callback):
        super().__init__()
        GS.set_black_background(self)
        self.start_game_callback = start_game_callback
        self.setup_ui()
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.start_game_callback)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        welcome_label = GS.create_styled_label(
            "Machine Gun Game", 48, True, "#00eaff", letter_spacing="2px"
        )
        
        title_image_layout = QHBoxLayout()
        title_image_layout.addStretch(1) 
      
        title_image_layout.addWidget(welcome_label)
        title_image_layout.addStretch(1) 
        
        instructions_label = GS.create_styled_label(
            "Press 'Start Game' to begin", 24, False, "#aaaaaa"
        )

        
        start_btn = GS.create_styled_button(
            "Start Game", 28, "#007bff", "#0056b3", "#004085", self.start_game_callback
        )
        
        layout.addStretch(1) 
        layout.addWidget(welcome_label)
        layout.addSpacing(30)
        layout.addWidget(instructions_label)
        layout.addSpacing(60) 
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1) # Another spacer

        self.setLayout(layout)