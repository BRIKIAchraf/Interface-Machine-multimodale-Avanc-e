from PyQt6.QtWidgets import QMainWindow, QLabel, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage
from src.utils.video_thread import VideoThread
from src.utils.voice_thread import VoiceThread

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interface Homme-Machine Multimodale Avancée")
        self.setGeometry(100, 100, 1280, 850)
        
        # Styles
        self.setStyleSheet("""
            QMainWindow { background-color: #1e1e1e; }
            QLabel { color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
            .info-box { background-color: #2d2d2d; border-radius: 8px; padding: 10px; margin: 5px; }
            .info-title { font-size: 14px; color: #888; font-weight: bold; }
            .info-value { font-size: 18px; color: #fff; font-weight: bold; }
        """)

        # Central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Header
        self.header_label = QLabel("IHM Multimodale : Gestes, Voix & Émotions")
        self.header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header_label.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px; color: #00d4ff;")
        self.main_layout.addWidget(self.header_label)
        
        # Video Feed
        self.image_label = QLabel(self)
        self.image_label.setMinimumSize(640, 360)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("background-color: #000; border: 2px solid #333;")
        self.main_layout.addWidget(self.image_label)
        
        # Dashboard Panel (Grid or HBox)
        self.dashboard_layout = QHBoxLayout()
        
        # Geste Box
        self.gesture_box = self.create_info_box("GESTE DÉTECTÉ", "---")
        self.dashboard_layout.addLayout(self.gesture_box)

        # Emotion Box
        self.emotion_box = self.create_info_box("ÉMOTION", "---")
        self.dashboard_layout.addLayout(self.emotion_box)

        # Voix Box
        self.voice_box = self.create_info_box("DERNIÈRE COMMANDE VOCALE", "---")
        self.dashboard_layout.addLayout(self.voice_box)

        self.main_layout.addLayout(self.dashboard_layout)

        # Initialize Fusion Engine
        from src.fusion.engine import FusionEngine
        self.fusion_engine = FusionEngine()

        # Initialize Video Thread
        self.video_thread = VideoThread()
        self.video_thread.change_pixmap_signal.connect(self.update_image)
        self.video_thread.update_info_signal.connect(self.update_visual_info)
        self.video_thread.start()

        # Action Box (Resultat de la fusion)
        self.action_box = self.create_info_box("ACTION SYSTÈME", "En attente...")
        self.dashboard_layout.addLayout(self.action_box)

        # Initialize Voice Thread
        try:
            self.voice_thread = VoiceThread()
            self.voice_thread.command_detected.connect(self.update_voice_info)
            self.voice_thread.start()
        except Exception as e:
            print(f"Erreur chargement voix: {e}")
            self.voice_label_val.setText("Erreur Init Voix")


    def create_info_box(self, title, value):
        layout = QVBoxLayout()
        container = QWidget()
        container.setStyleSheet("background-color: #2d2d2d; border-radius: 10px;")
        container_layout = QVBoxLayout()
        container.setLayout(container_layout)
        
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color: #aaa; font-size: 12px; text-transform: uppercase;")
        lbl_val = QLabel(value)
        lbl_val.setStyleSheet("color: #fff; font-size: 20px; font-weight: bold;")
        lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        container_layout.addWidget(lbl_title)
        container_layout.addWidget(lbl_val)
        layout.addWidget(container)
        
        # Store ref to update later
        if "GESTE" in title: self.gesture_label_val = lbl_val
        if "ÉMOTION" in title: self.emotion_label_val = lbl_val
        if "VOCALE" in title: self.voice_label_val = lbl_val
        if "ACTION" in title: self.action_label_val = lbl_val
        
        return layout

    @pyqtSlot(QImage)
    def update_image(self, cv_img):
        self.image_label.setPixmap(QPixmap.fromImage(cv_img))

    @pyqtSlot(str, str, dict)
    def update_visual_info(self, gesture, emotion, data):
        self.gesture_label_val.setText(gesture)
        
        # Fusion Update (Gesture & Emotion)
        # On passe data (contient curseur) pour la gestion souris
        action = self.fusion_engine.update("gesture", gesture, data)
        if action: self.update_action_display(action)
        
        action = self.fusion_engine.update("emotion", emotion)
        if action: self.update_action_display(action)

        # Traductions simples pour l'affichage
        map_emotions = {'happy': 'JOIE', 'angry': 'COLÈRE', 'sad': 'TRISTESSE', 'neutral': 'NEUTRE', 'surprise': 'SURPRISE', 'fear': 'PEUR'}
        fr_emotion = map_emotions.get(emotion, emotion)
        if fr_emotion:
            self.emotion_label_val.setText(fr_emotion.upper())

    @pyqtSlot(str)
    def update_voice_info(self, text):
        self.voice_label_val.setText(f'"{text}"')
        # Fusion Update (Voice)
        action = self.fusion_engine.update("voice", text)
        if action: self.update_action_display(action)

    def update_action_display(self, action):
        if not action: return
        self.action_label_val.setText(action)
        self.action_label_val.setStyleSheet("color: #00ff00; font-size: 22px; font-weight: bold;")

    def closeEvent(self, event):
        self.video_thread.stop()
        if hasattr(self, 'voice_thread'):
            self.voice_thread.stop()
        event.accept()
