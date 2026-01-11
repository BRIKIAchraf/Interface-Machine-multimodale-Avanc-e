import cv2
import numpy as np

class EmotionDetector:
    """
    Détecteur d'émotions utilisant OpenCV et l'analyse des expressions faciales.
    Utilise Haar Cascades pour la détection de visage et analyse les caractéristiques.
    """
    def __init__(self):
        # Chargement des classificateurs Haar Cascade
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        self.smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_smile.xml')
        
        self.current_emotion = "neutral"
        self.face_detected = False
        
        print("EmotionDetector initialisé (OpenCV Haar Cascades)")
        
    def detect(self, img_bgr):
        """
        Détecte l'émotion dans l'image en analysant les caractéristiques faciales.
        Retourne: str (ex: "happy", "neutral", "sad") ou None
        """
        try:
            # Conversion en niveaux de gris pour la détection
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Détection des visages
            faces = self.face_cascade.detectMultiScale(
                gray, 
                scaleFactor=1.1, 
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            if len(faces) == 0:
                self.face_detected = False
                return None
            
            self.face_detected = True
            
            # Analyser le premier visage détecté
            (x, y, w, h) = faces[0]
            
            # Dessiner le rectangle du visage
            cv2.rectangle(img_bgr, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Région d'intérêt pour le visage
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = img_bgr[y:y+h, x:x+w]
            
            # Détection des yeux
            eyes = self.eye_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.1,
                minNeighbors=10,
                minSize=(15, 15)
            )
            
            # Détection du sourire
            smiles = self.smile_cascade.detectMultiScale(
                roi_gray,
                scaleFactor=1.8,
                minNeighbors=20,
                minSize=(25, 25)
            )
            
            # Dessiner les yeux détectés
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Dessiner les sourires détectés
            for (sx, sy, sw, sh) in smiles:
                cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 0, 255), 2)
            
            # Analyse de l'émotion basée sur les caractéristiques détectées
            emotion = self._analyze_emotion(len(eyes), len(smiles), roi_gray)
            
            # Afficher l'émotion sur l'image
            cv2.putText(img_bgr, f"Emotion: {emotion.upper()}", 
                       (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
            
            self.current_emotion = emotion
            return emotion
            
        except Exception as e:
            print(f"Erreur détection émotion: {e}")
            return None
    
    def _analyze_emotion(self, num_eyes, num_smiles, face_roi):
        """
        Analyse l'émotion basée sur les caractéristiques détectées.
        """
        # Détection de sourire
        if num_smiles > 0:
            return "happy"
        
        # Si les yeux sont détectés mais pas de sourire
        if num_eyes >= 2:
            # Analyser l'intensité moyenne de la région du visage
            # pour détecter des expressions plus sombres
            avg_intensity = np.mean(face_roi)
            
            # Analyse de la région de la bouche (tiers inférieur du visage)
            mouth_region = face_roi[int(2*face_roi.shape[0]/3):, :]
            mouth_avg = np.mean(mouth_region)
            
            # Si la région de la bouche est plus sombre (bouche fermée/triste)
            if mouth_avg < avg_intensity * 0.85:
                return "sad"
            
            # Analyse de la région des sourcils (tiers supérieur)
            eyebrow_region = face_roi[:int(face_roi.shape[0]/3), :]
            eyebrow_variance = np.var(eyebrow_region)
            
            # Variance élevée peut indiquer des sourcils froncés (colère)
            if eyebrow_variance > 1000:
                return "angry"
        
        # Par défaut, neutre
        return "neutral"
    
    def get_face_detected(self):
        """Retourne True si un visage a été détecté lors de la dernière analyse"""
        return self.face_detected
