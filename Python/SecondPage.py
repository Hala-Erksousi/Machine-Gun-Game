from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
import GeneralStyleSettings as GS
class SecondPage(QWidget):
    def __init__(self, go_to_game_callback):
        super().__init__()
        GS.set_black_background(self)
        self.go_to_game_callback = go_to_game_callback
        self.setup_ui()

        # Keyboard shortcuts
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.validate_and_go_next)
        QShortcut(QKeySequence(Qt.Key_Escape), self).activated.connect(self.close) # Exit the app

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = GS.create_styled_label("Enter Players Names", 40, True, "#ffdd00")

        self.player1_input = GS.create_styled_line_edit("Player 1 Name", 400, 50, 20)
        self.player2_input = GS.create_styled_line_edit("Player 2 Name", 400, 50, 20)
        
        # Add labels above input fields for clarity
        player1_label = GS.create_styled_label("Player 1:", 20, False, alignment=Qt.AlignLeft)
        player2_label = GS.create_styled_label("Player 2:", 20, False, alignment=Qt.AlignLeft)

        next_btn = GS.create_styled_button(
            "Next", 28, "#28a745", "#218838", "#1e7e34", self.validate_and_go_next
        )

        # Use QHBoxLayout for labels and inputs to align them nicely
        p1_h_layout = QHBoxLayout()
        p1_h_layout.addStretch(1)
        p1_v_layout = QVBoxLayout() # Vertical layout for label and input
        p1_v_layout.addWidget(player1_label)
        p1_v_layout.addWidget(self.player1_input)
        p1_h_layout.addLayout(p1_v_layout)
        p1_h_layout.addStretch(1)

        p2_h_layout = QHBoxLayout()
        p2_h_layout.addStretch(1)
        p2_v_layout = QVBoxLayout()
        p2_v_layout.addWidget(player2_label)
        p2_v_layout.addWidget(self.player2_input)
        p2_h_layout.addLayout(p2_v_layout)
        p2_h_layout.addStretch(1)


        layout.addStretch(1)
        layout.addWidget(title)
        layout.addSpacing(40)
        layout.addLayout(p1_h_layout) # Add the horizontal layout for player 1
        layout.addSpacing(30)
        layout.addLayout(p2_h_layout) # Add the horizontal layout for player 2
        layout.addSpacing(60)
        layout.addWidget(next_btn, alignment=Qt.AlignCenter)
        layout.addStretch(1)

        self.setLayout(layout)

    def validate_and_go_next(self):
        player1_name = self.player1_input.text().strip()
        player2_name = self.player2_input.text().strip()

        if not player1_name or not player2_name:
            QMessageBox.warning(self, "Input Error", "Please enter names for both players.")
            return

        self.go_to_game_callback(player1_name, player2_name)
