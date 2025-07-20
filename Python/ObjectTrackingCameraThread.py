# import GestureCameraThread as G
from GestureCameraThread import GestureCameraThread
from Target import Target
import cv2
import numpy as np
import serial as ser
import time
from datetime import datetime
from Target import Target

from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal

class ObjectTrackingCameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    score_update_signal = pyqtSignal(int)
    time_remaining_signal = pyqtSignal(int)
    round_ended_signal = pyqtSignal(int)

    def __init__(self, player_name, PLAYER_TIME_LIMIT_SECONDS=70, PAUSE_DURATION_SECONDS=7, parent=None, is_dummy=False, display_width=1175, display_height=900):
        super().__init__(parent)
        self.player_name = player_name
        self._run_flag = False
        self.cap = None
        self.display_width = display_width   
        self.display_height = display_height

       # Goal Tracking Variables
        self.lower_yellow = np.array([9, 106, 88])
        self.upper_yellow = np.array([32, 255, 255])
        self.known_targets = []
        self.target_id_counter = 0
        self.FALLEN_CONFIRMATION_FRAMES = 5 
        self.setup_frame_processed = False
        self.current_player_fallen_score = 0 
        self.start_time = 0
        self.PLAYER_TIME_LIMIT_SECONDS = PLAYER_TIME_LIMIT_SECONDS
        self.PAUSE_DURATION_SECONDS = PAUSE_DURATION_SECONDS
        self.is_dummy = is_dummy

        self.record_video = False
        self.out = None
        self.output_filename = ""

    def run(self):
        if self.is_dummy:
            print("Running Object Tracking Camera in DUMMY mode.")
            frame = np.zeros((500, 1000, 3), dtype=np.uint8)
            cv2.putText(frame, "DUMMY CAMERA ACTIVE", (200,250), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
            ret = True
            if np.random.rand() < 0.01 and self.setup_frame_processed:
                if len(self.known_targets) > 0:
                    standing_targets = [t for t in self.known_targets if t.is_standing]
                    if standing_targets:
                        target_to_fall = np.random.choice(standing_targets)
                        target_to_fall.is_standing = False
                        target_to_fall.was_counted_as_fallen = True
                        self.current_player_fallen_score = sum(1 for t in self.known_targets if t.was_counted_as_fallen)
                        self.score_update_signal.emit(self.current_player_fallen_score)
                        print(f"Dummy: Object {target_to_fall.id} fell! Score: {self.current_player_fallen_score}")
        else:
            camera_opened = False
            for i in range(3):
                print(f"DEBUG: Trying to open object tracking camera with index {i}...")
                self.cap = cv2.VideoCapture(0)
                if self.cap.isOpened():
                    self.camera_index = i 
                    print(f"DEBUG: Object tracking camera opened successfully at index {self.camera_index}")
                    camera_opened = True
                    break
                else:
                    print(f"DEBUG: Could not open object tracking camera with index {i}")

            if not camera_opened:
                print("Error: Could not open any object tracking camera. Please check connections or if camera is in use.")
                self._run_flag = False
                return
            
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            frame_width_cap = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height_cap = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps_cap = self.cap.get(cv2.CAP_PROP_FPS)
            if fps_cap == 0:
                fps_cap = 30 

            # fourcc = cv2.VideoWriter_fourcc(*'XVID')
            # self.output_filename = f"Bowling_Recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
            # self.out = cv2.VideoWriter(self.output_filename, fourcc, fps_cap, (1000, 500))
            # if not self.out.isOpened():
            #     print("Wrong video is not open, recording disabled.")
            #     self.record_video = False
            # else:
            #     self.record_video = True
            #     print(f"Start recording {self.output_filename}")


        self._run_flag = True
        self.start_time = time.time()
        self.current_player_fallen_score = 0
        self.score_update_signal.emit(0)
        
        self.known_targets = []
        self.target_id_counter = 0
        self.setup_frame_processed = False

        while self._run_flag:
            if not self.is_dummy:
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Could not read frame from object tracking camera.")
                    break
            
            
            if self.is_dummy:
                pass 
            else:
                frame = cv2.resize(frame, (1000, 500)) 

            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            yellow_mask = cv2.inRange(hsv_frame, self.lower_yellow, self.upper_yellow)
            kernel = np.ones((5, 5), np.uint8)
            yellow_mask = cv2.erode(yellow_mask, kernel, iterations=1) 
            yellow_mask = cv2.dilate(yellow_mask, kernel, iterations=1) 
            contours, _ = cv2.findContours(yellow_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            current_frame_detections = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100: 
                    x, y, w, h = cv2.boundingRect(contour)
                    center_x = x + w // 2
                    center_y = y + h // 2
                    current_frame_detections.append({'bbox': (x, y, w, h), 'center': (center_x, center_y)})

            if not self.setup_frame_processed and len(current_frame_detections) > 0:
                self.known_targets = []
                for detection in current_frame_detections:
                    self.target_id_counter += 1
                    self.known_targets.append(Target(self.target_id_counter, detection['bbox']))
                self.setup_frame_processed = True
                print(f"DEBUG: Detected {len(self.known_targets)} initial targets for {self.player_name}.")


           #Update the fallen score based on dropped targets
            self.current_player_fallen_score = sum(1 for t in self.known_targets if t.was_counted_as_fallen)
            self.score_update_signal.emit(self.current_player_fallen_score) #Update the score in the GUI

            for target in self.known_targets:
                if not target.is_standing and target.was_counted_as_fallen:
                    continue

                min_dist = float('inf')
                best_match_detection = None

                target_center_point = (target.current_x + target.current_w // 2,
                                       target.current_y + target.current_h // 2)

                for detection in current_frame_detections:
                    detection_center_point = detection['center']
                    dist =GestureCameraThread.calculate_distance(target_center_point, detection_center_point)
                    distance_threshold = target.initial_w * 1.5

                    if dist < min_dist and dist < distance_threshold:
                        min_dist = dist
                        best_match_detection = detection

                if best_match_detection:
                    target.current_x, target.current_y, target.current_w, target.current_h = best_match_detection['bbox']
                    current_center_y = target.current_y + target.current_h // 2

                    if current_center_y - target.standing_center_y > target.fall_threshold_y:
                        target.fallen_frame_count += 1
                        if target.fallen_frame_count >= self.FALLEN_CONFIRMATION_FRAMES:
                            if target.is_standing:
                                target.is_standing = False
                                if not target.was_counted_as_fallen: #Ensure no double Counting
                                    target.was_counted_as_fallen = True
                                    self.current_player_fallen_score += 1 #Live Score Update
                                    self.score_update_signal.emit(self.current_player_fallen_score)
                                    print(f"{self.player_name}: Target {target.id} fell! Current Score: {self.current_player_fallen_score}")
                    else:
                        target.fallen_frame_count = 0
                else: 
                    # No match found, target might have disappeared or moved significantly
                    target.fallen_frame_count += 1
                    if target.fallen_frame_count >= self.FALLEN_CONFIRMATION_FRAMES:
                        if target.is_standing: 
                            target.is_standing = False
                            if not target.was_counted_as_fallen: #Ensure no double Counting
                                target.was_counted_as_fallen = True
                                self.current_player_fallen_score += 1 
                                self.score_update_signal.emit(self.current_player_fallen_score)
                                print(f"{self.player_name}: Target {target.id} fell (lost)! Current Score: {self.current_player_fallen_score}")

            # Drawing on the frame
            for target in self.known_targets:
                x, y, w, h = target.current_x, target.current_y, target.current_w, target.current_h
                color = (0, 255, 0) if target.is_standing else (0, 0, 255)
                status_text = "Standing" if target.is_standing else "Fallen"
                cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
                cv2.putText(frame, f"Goal {target.id} ({status_text})", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                cv2.circle(frame, (target.initial_x + target.initial_w // 2, target.standing_center_y), 5, (255, 0, 0), -1) #Blue reference point

            elapsed = time.time() - self.start_time
            remaining = max(0, self.PLAYER_TIME_LIMIT_SECONDS - int(elapsed))
            self.time_remaining_signal.emit(remaining) #Update time in GUI

            score_text = f"Player {self.player_name} | Fallen: {self.current_player_fallen_score} | Time Left: {remaining}s"
            cv2.putText(frame, score_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        
          
            # Final condition for ending the round
            if remaining <= 0 or (self.setup_frame_processed and self.current_player_fallen_score >= len(self.known_targets) and len(self.known_targets) > 0):
                print(f"Round ended for {self.player_name}. Score: {self.current_player_fallen_score}")
                self.round_ended_signal.emit(self.current_player_fallen_score)
                self.stop() #Stop the camera thread
            
            #convert frame for display in PyQt
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(self.display_width, self.display_height, Qt.IgnoreAspectRatio)
            self.change_pixmap_signal.emit(p)
            
            self.msleep(10) 

        if self.cap:
            self.cap.release()
        if self.out and self.record_video: 
            self.out.release()
        print(f"Object Tracking Camera {self.camera_index} stopped.")

    def stop(self):
        self._run_flag = False
        self.wait()

    def reset_for_new_round(self):
        self.known_targets = []
        self.target_id_counter = 0
        self.setup_frame_processed = False
        self.current_player_fallen_score = 0
        self.score_update_signal.emit(0)
