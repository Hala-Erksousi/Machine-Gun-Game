from GestureCameraThread import GestureCameraThread
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QLineEdit, QStackedWidget, QHBoxLayout, QShortcut, QMessageBox,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal
import GeneralStyleSettings as GS
from ObjectTrackingCameraThread import ObjectTrackingCameraThread
from AudioManager import audio_manager
class ThirdPage(QWidget):
    def __init__(self, player_name, player_time_limit, finish_round_callback):
        super().__init__()
        self.player_name = player_name
        self.player_time_limit = player_time_limit
        self.finish_round_callback = finish_round_callback
        GS.set_black_background(self)
        
        self.pre_game_timer = QTimer(self)
        self.pre_game_timer.timeout.connect(self.update_pre_game_timer)
        
        self.pre_game_seconds = 2
        self.current_pre_game_timer_duration = 0 
        self.is_pre_game_timer_active = False
        self.is_go_displayed = False
        self.countdown_sound_played = False 

        self.score_label = GS.create_styled_label(f"Score: 0", 28, True, "#00ff00", alignment=Qt.AlignLeft)
        self.game_timer_label = GS.create_styled_label(f"Time Left: {self.player_time_limit}s", 28, True, "#FF0000", alignment=Qt.AlignRight)

        self.setup_ui()
        self.gesture_camera_thread = GestureCameraThread(camera_index=1, display_width=self.camera_display_width, display_height=self.camera_display_height)
        self.gesture_camera_thread.change_pixmap_signal.connect(self.update_gesture_camera_feed)
        
        
        self.object_tracking_camera_thread = ObjectTrackingCameraThread(
            player_name=self.player_name,
            PLAYER_TIME_LIMIT_SECONDS=self.player_time_limit,
            display_width=self.camera_display_width,
            display_height=self.camera_display_height
        )
        self.object_tracking_camera_thread.change_pixmap_signal.connect(self.update_object_tracking_camera_feed)
        self.object_tracking_camera_thread.score_update_signal.connect(self.update_score_display)
        self.object_tracking_camera_thread.time_remaining_signal.connect(self.update_game_timer_display)
        self.object_tracking_camera_thread.round_ended_signal.connect(self.handle_round_ended)

       

    def setup_ui(self):
        layout = QVBoxLayout()

        self.name_label = GS.create_styled_label(self.player_name, 36, True, "#00eaff")
        self.ready_label = GS.create_styled_label("Are You Ready?", 30, True, "#ffdd00")

        self.ready_btn = GS.create_styled_button(
            "Yes", 28, "#28a745", "#218838", "#1e7e34", self.start_pre_game_timer
        )

        self.pre_game_countdown_label = GS.create_styled_label("", 60, True, "#FF0000")
        self.pre_game_countdown_label.hide() 

        top_info_layout = QHBoxLayout()
        top_info_layout.addWidget(self.score_label)
        top_info_layout.addStretch(1)
        top_info_layout.addWidget(self.game_timer_label)

        self.cam_area1 = QLabel("Gesture Camera Feed")
        self.cam_area2 = QLabel("Target Camera Feed")
        for cam in [self.cam_area1, self.cam_area2]:
            cam.setStyleSheet("""
                color: #bbbbbb;
                border: 3px solid #007bff;
                background-color: #0d0d0d;
                font-size: 22px;
                border-radius: 10px;
                padding: 20px;
            """)
            cam.setAlignment(Qt.AlignCenter)
            cam.setFixedSize(1175,900)
            self.camera_display_width = 1175
            self.camera_display_height = 900

        cam_layout = QHBoxLayout()
        cam_layout.addStretch(1)
        cam_layout.addWidget(self.cam_area1)
        cam_layout.addSpacing(80)
        cam_layout.addWidget(self.cam_area2)
        cam_layout.addStretch(1)

        layout.addSpacing(20)
        layout.addWidget(self.name_label)
        layout.addSpacing(20)
        layout.addWidget(self.ready_label)
        layout.addSpacing(30)
        layout.addWidget(self.ready_btn, alignment=Qt.AlignCenter)
        layout.addWidget(self.pre_game_countdown_label, alignment=Qt.AlignCenter)
        
        layout.addLayout(top_info_layout)
        layout.addSpacing(10)
        layout.addLayout(cam_layout)
        layout.addStretch(1)

        self.setLayout(layout)
        QShortcut(QKeySequence(Qt.Key_Return), self).activated.connect(self.ready_btn.click)

    def start_pre_game_timer(self):
        self.ready_label.hide()
        self.ready_btn.hide()
        self.pre_game_countdown_label.show()
        self.score_label.show()
        self.game_timer_label.show()
        
        if not self.countdown_sound_played:
            audio_manager.play_countdown_sound() 
            self.countdown_sound_played = True 

        self.current_pre_game_timer_duration = self.pre_game_seconds + 1
        self.is_pre_game_timer_active = True 
        self.is_go_displayed = False
        self.pre_game_timer.start(1000) 
        self.update_pre_game_timer_display()

    def update_pre_game_timer_display(self):
        if self.is_pre_game_timer_active:
            self.pre_game_countdown_label.setText(str(self.current_pre_game_timer_duration))
            self.pre_game_countdown_label.setStyleSheet("color: #FF0000; font-size: 80px; font-weight: extra-bold;")
        elif self.is_go_displayed:
            self.pre_game_countdown_label.setText("Go!")
            self.pre_game_countdown_label.setStyleSheet("color: #00FF00; font-size: 90px; font-weight: extra-bold;")

    def update_pre_game_timer(self):
        self.current_pre_game_timer_duration -= 1
        
        if self.current_pre_game_timer_duration > 0:
            self.update_pre_game_timer_display()
        else:
            self.pre_game_timer.stop()
            
            if self.is_pre_game_timer_active:
                self.is_pre_game_timer_active = False 
                self.is_go_displayed = True
                QTimer.singleShot(1000, self.start_actual_game)

    def start_actual_game(self):
        self.pre_game_countdown_label.hide()
        self.is_go_displayed = False 
        
        self.gesture_camera_thread.start()
        self.object_tracking_camera_thread.reset_for_new_round()
        self.object_tracking_camera_thread.start()

    def update_gesture_camera_feed(self, image):
        self.cam_area1.setPixmap(QPixmap.fromImage(image))

    def update_object_tracking_camera_feed(self, image):
        self.cam_area2.setPixmap(QPixmap.fromImage(image))
    
    def update_score_display(self, score):
        self.score_label.setText(f"Score: {score}")

    def update_game_timer_display(self, time_left):
        self.game_timer_label.setText(f"Time Left: {time_left}s")
        if time_left >= 0 and time_left <= 3:
            audio_manager.play_final_countdown_beep()
    
    def handle_round_ended(self, final_score):
        print(f"ThirdPage received round_ended signal for {self.player_name} with score: {final_score}")
        self.stop_cameras()
        self.finish_round_callback(final_score)

    def stop_cameras(self):
        if self.gesture_camera_thread.isRunning():
            self.gesture_camera_thread.stop()
        if self.object_tracking_camera_thread.isRunning():
            self.object_tracking_camera_thread.stop()
        self.cam_area1.clear()
        self.cam_area2.clear()
        self.cam_area1.setText("Gesture Camera Feed")
        self.cam_area2.setText("Target Camera Feed")