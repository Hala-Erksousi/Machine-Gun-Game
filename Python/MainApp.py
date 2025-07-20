import GestureCameraThread as G
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
import GeneralStyleSettings as GS
import sys
from FirstPage import FirstPage
from SecondPage import SecondPage
from ThirdPage import ThirdPage
from ResultsPage import ResultsPage
from AudioManager import audio_manager
class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        GS.set_black_background(self)

        self.player1_name = ""
        self.player2_name = ""
        self.player1_score = 0
        self.player2_score = 0
        self.current_player_index = 0
        self.PLAYER_GAME_TIME = 80


        self.first_page = FirstPage(self.go_to_second_page)
        self.second_page = SecondPage(self.go_to_player1_page)

        self.addWidget(self.first_page)
        self.addWidget(self.second_page)
        self.setCurrentWidget(self.first_page)
        
        audio_manager.play_welcome_sound()

        QShortcut(QKeySequence("Esc"), self).activated.connect(QApplication.quit)

    def go_to_second_page(self):
        audio_manager.stop_all_sounds() 
        self.setCurrentWidget(self.second_page)

    def go_to_player1_page(self, player1, player2):
        self.player1_name = player1
        self.player2_name = player2
        self.current_player_index = 0
        
        self.player1_page = ThirdPage(self.player1_name, self.PLAYER_GAME_TIME, self.handle_player_round_end)
        self.addWidget(self.player1_page)
        self.setCurrentWidget(self.player1_page)

    def handle_player_round_end(self, score):
        if self.current_player_index == 0:
            self.player1_score = score
            print(f"Player 1 ({self.player1_name}) finished with score: {self.player1_score}")
            self.current_player_index = 1
            audio_manager.stop_all_sounds()
            
            self.show_intermediate_screen("Next Player...", self.go_to_player2_page)
            
        elif self.current_player_index == 1:
            self.player2_score = score
            print(f"Player 2 ({self.player2_name}) finished with score: {self.player2_score}")
            self.current_player_index = -1
            audio_manager.stop_all_sounds()

            self.show_intermediate_screen("End Game!", self.show_final_results)

    def show_intermediate_screen(self, message, next_callback):
        intermediate_page = QWidget()
        GS.set_black_background(intermediate_page)

        layout = QVBoxLayout()
        label = GS.create_styled_label(message, 60, True, "#FF0000")

        layout.addStretch(1)
        layout.addWidget(label)
        layout.addStretch(1)

        intermediate_page.setLayout(layout)
        self.addWidget(intermediate_page)
        self.setCurrentWidget(intermediate_page)
        
        if message == "End Game!":
            audio_manager.play_game_over_sound()
        elif message == "Next Player...":
            audio_manager.play_next_player_sound()   
            G.arduino.write(f"{int(0)}\n".encode())
        else:
            pass 

        QTimer.singleShot(2000, next_callback)

    def go_to_player2_page(self):
        if hasattr(self, 'player1_page') and self.player1_page.isVisible():
            self.removeWidget(self.player1_page)
            self.player1_page.deleteLater()

        audio_manager.stop_all_sounds() 

        self.player2_page = ThirdPage(self.player2_name, self.PLAYER_GAME_TIME, self.handle_player_round_end)
        self.addWidget(self.player2_page)
        self.setCurrentWidget(self.player2_page)

    def show_final_results(self):
        if hasattr(self, 'player2_page') and self.player2_page.isVisible():
            self.removeWidget(self.player2_page)
            self.player2_page.deleteLater()

        audio_manager.stop_all_sounds() 

        results_page = ResultsPage(self.player1_name, self.player1_score, self.player2_name, self.player2_score)
        self.addWidget(results_page)
        self.setCurrentWidget(results_page)

if __name__== '__main__':
    def cleanup_threads():
        for widget in app.topLevelWidgets():
            if isinstance(widget, MainApp):
                for i in range(widget.count()):
                    page = widget.widget(i)
                    if isinstance(page, ThirdPage):
                        page.stop_cameras()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    main_app = MainApp()
    main_app.showFullScreen()

    app.aboutToQuit.connect(cleanup_threads)

    sys.exit(app.exec_())