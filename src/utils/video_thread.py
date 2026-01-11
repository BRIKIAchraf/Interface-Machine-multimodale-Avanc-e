import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QImage
from src.gestures.hand_tracking import HandTracker
from src.gestures.analyzer import GestureAnalyzer
from src.emotions.detector import EmotionDetector
from src.executive.face_auth import FaceAuthenticator

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    update_info_signal = pyqtSignal(str, str, dict) 

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.hand_tracker = HandTracker(max_hands=1) 
        self.gesture_analyzer = GestureAnalyzer()
        self.emotion_detector = EmotionDetector() # Garde détection émotion de base
        self.face_auth = FaceAuthenticator() # Ajout module Auth/Gaze
        self.frame_count = 0

    def run(self):
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            print("ERREUR: Impossible d'ouvrir la webcam")
            return
        
        current_emotion = "---"
        current_gesture = "---"
        
        while self._run_flag:
            ret, cv_img = cap.read()
            if ret:
                # Miroir horizontal
                cv_img = cv2.flip(cv_img, 1)
                
                h, w, tr = cv_img.shape
                self.frame_count += 1
                data = {}
                
                # 0. AUTHENTIFICATION & ATTENTION (Visage)
                # On le fait à chaque frame ou 1/2 pour fluidité curseur
                is_auth, user, attention = self.face_auth.update(cv_img)
                data['auth'] = is_auth
                data['user'] = user
                data['attention'] = attention
                
                # Si pas d'attention, on pourrait bloquer le curseur ?
                # if not attention: ... (Logique décisionnelle dans FusionEngine)
                
                # 1. GESTE
                cv_img = self.hand_tracker.find_hands(cv_img, draw=True)
                lm_list = self.hand_tracker.find_position(cv_img, draw=False)
                
                if len(lm_list) != 0:
                    finger_count = self.hand_tracker.get_finger_count(0)
                    gesture = self.gesture_analyzer.analyze_gesture_with_fingers(lm_list, finger_count)
                    
                    if gesture:
                        current_gesture = gesture
                        
                    # Données curseur
                    if len(lm_list) > 8:
                        ix, iy = lm_list[8][1], lm_list[8][2]
                        data['cursor'] = (ix / w, iy / h) 
                        data['landmarks'] = lm_list
                else:
                    current_gesture = "Aucune main"
                    data['cursor'] = None

                # 2. EMOTION (moins fréquent)
                if self.frame_count % 10 == 0:
                    emotion = self.emotion_detector.detect(cv_img) 
                    if emotion:
                        current_emotion = emotion

                # Affichage debug
                overlay = cv_img.copy()
                cv2.rectangle(overlay, (5, 5), (400, 160), (0, 0, 0), -1)
                cv2.addWeighted(overlay, 0.3, cv_img, 0.7, 0, cv_img)
                
                color_att = (0, 255, 0) if attention else (0, 0, 255)
                cv2.putText(cv_img, f"Geste: {current_gesture}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(cv_img, f"Emotion: {current_emotion.upper()}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                cv2.putText(cv_img, f"Regard: {'ECRAN' if attention else 'AILLEURS'}", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_att, 2)
                cv2.putText(cv_img, f"User: {user if is_auth else 'Invité'}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

                # Emission
                self.update_info_signal.emit(current_gesture, current_emotion, data)

                # Conversion QT
                rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                convert_to_qt_format = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
                p = convert_to_qt_format.scaled(1280, 720, Qt.AspectRatioMode.KeepAspectRatio)
                self.change_pixmap_signal.emit(p)
        
        cap.release()

    def stop(self):
        self._run_flag = False
        self.wait()
