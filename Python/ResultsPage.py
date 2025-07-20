from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
import GeneralStyleSettings as GS
# import AudioManager as audio_manager
from AudioManager import audio_manager
class ResultsPage(QWidget):
    def __init__(self, player1, player1_score, player2, player2_score):
        super().__init__()
        GS.set_black_background(self)
        self.player1 = player1
        self.player2 = player2
        self.player1_score = player1_score 
        self.player2_score = player2_score 
        self.setup_ui()
        
        audio_manager.play_result_sound() 

    def setup_ui(self):
        layout = QVBoxLayout()

        title = GS.create_styled_label("Final Results", 48, True, "#00ffff", letter_spacing="2px")

        p1_name_label = GS.create_styled_label(self.player1, 36, True, "#00eaff", alignment=Qt.AlignRight) 
        p1_score_label = GS.create_styled_label(f"Score: {self.player1_score}", 32, False, alignment=Qt.AlignRight) 

        p2_name_label = GS.create_styled_label(self.player2, 36, True, "#00eaff", alignment=Qt.AlignLeft) 
        p2_score_label = GS.create_styled_label(f"Score: {self.player2_score}", 32, False, alignment=Qt.AlignLeft) 

        players_layout = QHBoxLayout()
        players_layout.addStretch(1)
        
        vbox_p1 = QVBoxLayout()
        vbox_p1.addWidget(p1_name_label)
        vbox_p1.addSpacing(15)
        vbox_p1.addWidget(p1_score_label)
        vbox_p1.addStretch(1)
        players_layout.addLayout(vbox_p1)
        
        players_layout.addItem(QSpacerItem(500, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)) 
        
        vbox_p2 = QVBoxLayout()
        vbox_p2.addWidget(p2_name_label)
        vbox_p2.addSpacing(15)
        vbox_p2.addWidget(p2_score_label)
        vbox_p2.addStretch(1)
        players_layout.addLayout(vbox_p2)
        
        players_layout.addStretch(1)

        winner = QLabel()
        if self.player1_score > self.player2_score:
            winner.setText(f"\U0001F3C6 Winner: {self.player1} \U0001F3C6")
            winner.setStyleSheet("color: #ffd700; font-weight: extra-bold;")
        elif self.player2_score > self.player1_score:
            winner.setText(f"\U0001F3C6 Winner: {self.player2} \U0001F3C6")
            winner.setStyleSheet("color: #ffd700; font-weight: extra-bold;")
        else:
            winner.setText("\U0001F91D It's a Tie! \U0001F91D")
            winner.setStyleSheet("color: #32CD32; font-weight: extra-bold;")

        winner.setFont(QFont("Arial", 42, QFont.Bold)) 
        winner.setAlignment(Qt.AlignCenter)

        thanks = GS.create_styled_label("Thank you for playing!", 34, True) 

        self.exit_btn = GS.create_styled_button(
            "Exit", 12,
            "#6c757d",
            "#808a91",
            "#5a6268",
            QApplication.quit
        )
        self.exit_btn.setFixedSize(70, 28)

        bottom_right_layout = QHBoxLayout()
        bottom_right_layout.addStretch(1) 
        bottom_right_layout.addWidget(self.exit_btn)
        bottom_right_layout.addSpacing(30) 

        layout.addSpacing(40) 
        layout.addWidget(title)
        layout.addSpacing(60) 
        layout.addLayout(players_layout)
        layout.addSpacing(60) 
        layout.addWidget(winner)
        layout.addSpacing(40)
        layout.addWidget(thanks)
        layout.addStretch(1) 
        layout.addLayout(bottom_right_layout) 
        layout.addSpacing(30) 

        self.setLayout(layout)