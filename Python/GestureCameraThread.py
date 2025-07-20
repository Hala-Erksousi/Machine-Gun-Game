import mediapipe as mp
import cv2
import math
import serial as ser
import time
arduino = ser.Serial(port='COM9', baudrate=9600, timeout=1)
time.sleep(2)

from PyQt5.QtGui import QFont, QKeySequence, QColor, QImage, QPixmap
from PyQt5.QtCore import Qt, QTimer, QUrl, QThread, pyqtSignal

class GestureCameraThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)

    def __init__(self, camera_index=1, parent=None,display_width=1175, display_height=900):
        super().__init__(parent)
        self.camera_index = camera_index
        self._run_flag = False
        self.cap = None
        self.display_width = display_width   
        self.display_height = display_height 

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)
        self.mp_draw = mp.solutions.drawing_utils
        #variables for Fire and Load Cases
        self.ready_confirmed = False
        self.fire_triggered = False
        self.fire_command_sent = False
        self.Load_commend_sent=False
        self.last_stepper_send_time = 0
        self.STEPPER_SEND_INTERVAL = 0.3
    # Function for calculate angle (-30,+30)
    def  calculate_signed_angle(self, x1, y1, x2, y2):
        dx = x2 - x1
        dy = y1 - y2
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        if angle_deg > 180:
            angle_deg -= 360
        elif angle_deg < -180:
            angle_deg += 360
        signed_angle = angle_deg - 90
        return max(-30, min(30, signed_angle))
    # Function for cartridge Loading Movement
    def calculate_distance(point1, point2):
        return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)
    def is_ready_gesture(self, handLms):
        return (
            handLms.landmark[12].y > handLms.landmark[10].y and
            handLms.landmark[16].y > handLms.landmark[14].y and
            handLms.landmark[20].y > handLms.landmark[18].y and
            handLms.landmark[8].y < handLms.landmark[6].y
        )
    #Function For Firing Movement
    def is_fire_gesture(self, handLms):
        return handLms.landmark[12].y < handLms.landmark[10].y
    #Function to ensure all fingers are open
    def is_open_hand(self, handLms):
        return (
            handLms.landmark[8].y < handLms.landmark[6].y and
            handLms.landmark[12].y < handLms.landmark[10].y and
            handLms.landmark[16].y < handLms.landmark[14].y and
            handLms.landmark[20].y < handLms.landmark[18].y
        )
    
    def run(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        # time.sleep(1)
        if not self.cap.isOpened():
            print(f"Error: Could not open gesture camera {self.camera_index}")
            self._run_flag = False
            return
    
        self._run_flag = True
        while self._run_flag:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Could not read frame from gesture camera.")
                break
            
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = self.hands.process(img_rgb)

            if results.multi_hand_landmarks:
                for idx, handLms in enumerate(results.multi_hand_landmarks):
                    self.mp_draw.draw_landmarks(frame, handLms, self.mp_hands.HAND_CONNECTIONS)
                    
                    x0 = int(handLms.landmark[0].x * w)
                    y0 = int(handLms.landmark[0].y * h)
                    x8 = int(handLms.landmark[8].x * w)
                    y8 = int(handLms.landmark[8].y * h)
                    
                    angle = self.calculate_signed_angle(x0, y0, x8, y8)
                    angle_mapped = angle * 3
                    
                    direction = "Center"
                    if angle_mapped < -10:
                        direction = "Right"
                    elif angle_mapped > 10:
                        direction = "Left"
                    
                    cv2.putText(frame, direction, (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)
                    cv2.putText(frame, f"Angle: {int(angle_mapped)}", (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
                    cv2.line(frame, (x0, y0), (x8, y8), (0, 255, 255), 3)
                    cv2.circle(frame, (x8, y8), 10, (0, 0, 255), -1)
                    # if the movement is currently load then ready_confirmed = True and all others are false 
                    if self.is_ready_gesture(handLms):
                        self.ready_confirmed = True
                        self.fire_triggered = False
                        self.fire_command_sent = False
                        self.Load_command_send=None
                        Load_String="Load"
                        cv2.putText(frame, "Load", (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 140, 0), 3)
                        # if the load hasn't been sent yet and the arduino is open , send a message and set Load_command_send to True
                        if not self.Load_command_send and arduino and arduino.is_open:
                            arduino.write(f"{Load_String}\n".encode())
                            print("Sent 'Load' to Arduino.")
                            self.Load_command_send = True
                            # Add a small delay  after sending the servo command
                            time.sleep(0.05) # 50 millisecond
                        elif self.Load_command_send:
                            self.Load_command_send=False
                    #If ready_confirmed is True and  the user has performed the fire movement,  and if fire_command_sent hasn't been sent yet, 
                    # and the Arduino is open, then send the word 'fire' to the Arduino and set fire_command_sent to True."
                    elif self.ready_confirmed and self.is_fire_gesture(handLms):
                        self.fire_triggered = True
                        self.ready_confirmed = False
                        fire_string="FIRE"
                        cv2.putText(frame, "FIRE", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                        if not self.fire_command_sent and arduino and arduino.is_open:
                            arduino.write(f"{fire_string}\n".encode())
                            print("Sent 'FIRE' to Arduino.")
                            self.fire_command_sent = True
                            # Add a small delay  after sending the servo command
                            time.sleep(0.05) # 50 millisecond
                    elif not self.is_ready_gesture(handLms) and not self.is_fire_gesture(handLms):
                       self.ready_confirmed = False
                       self.fire_triggered = False
                       self. fire_command_sent = False        
                    elif self.fire_triggered and self.is_open_hand(handLms):
                        self.ready_confirmed=False
                        self.fire_triggered = False
                        self.fire_command_sent = False
                    # send the angle to the arduino only if there's no 'load' or 'fire' movement occurring
                    current_time = time.time()
                    if current_time - self.last_stepper_send_time >= self.STEPPER_SEND_INTERVAL:
                        if arduino and arduino.is_open and self.ready_confirmed==False and self.fire_triggered==False:
                            arduino.write(f"{int(angle_mapped)}\n".encode())
                        self.last_stepper_send_time = current_time

            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            p = convert_to_qt_format.scaled(self.display_width, self.display_height, Qt.IgnoreAspectRatio)
            self.change_pixmap_signal.emit(p)
            
        self.cap.release()
        print(f"Gesture Camera {self.camera_index} stopped.")

    def stop(self):
        self._run_flag = False
        self.wait()