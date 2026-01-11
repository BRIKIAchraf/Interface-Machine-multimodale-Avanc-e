"""
Module de Sécurité & Authentification Faciale.
Gère FaceID, l'Attention (Gaze), et la protection des données.
"""
import cv2
import numpy as np
import os
import pickle
import time
# Utilise MediaPipe FaceMesh pour le regard et attention (plus précis que Haar)
import mediapipe as mp

class FaceAuthenticator:
    def __init__(self):
        self.known_embeddings = {} # {name: data}
        self.auth_active = False # Est-ce que l'utilisateur est authentifié ?
        self.current_user = None
        
        # MediaPipe Face Mesh pour l'attention (Gaze)
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            refine_landmarks=True # Important pour iris
        )
        
        # Stockage local simulé (fichier pickle)
        self.db_path = "face_db.pkl"
        self._load_db()
        
        print("👤 FaceAuthenticator: Initialisé (FaceMesh + Auth)")

    def update(self, img):
        """
        Traite l'image pour l'authentification et l'attention.
        Retourne: (is_authenticated, user_name, looking_at_screen)
        """
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_img)
        
        looking_at_screen = False
        
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # 1. Check Attention (Gaze Direction basis)
                # On utilise les iris (refine_landmarks=True ajoute iris markers)
                # Indices Iris Gauche: 474-477, Droite: 469-472 (approx)
                # Méthode simple: Head Pose Estimation
                if self._check_attention(face_landmarks.landmark, img.shape):
                    looking_at_screen = True
                
                # 2. Auth (Si pas encore auth)
                if not self.auth_active:
                    # Ici on ferait une reconnaissance faciale complète
                    # Pour cette demo sans dlib, on simule l'auth si "Regarde l'écran" pendant 2 sec
                    # En vrai: self._verify_face(face_encoding)
                    pass 
        
        return self.auth_active, self.current_user, looking_at_screen

    def register_user(self, name, img):
        """Enregistre un nouvel utilisateur (Mock)"""
        print(f"Enregistrement visage pour {name}...")
        self.known_embeddings[name] = "fake_embedding_data"
        self._save_db()
        self.auth_active = True
        self.current_user = name
        return True

    def login_user(self):
        """Simule un login réussi"""
        self.auth_active = True
        self.current_user = "Admin"
        print("✅ Authentification réussie: Admin")

    def logout(self):
        self.auth_active = False
        self.current_user = None
        print("🔒 Déconnexion")

    def _check_attention(self, landmarks, shape):
        """
        Estime si l'utilisateur regarde l'écran via l'orientation du visage (Nose tip vs Face center).
        """
        h, w, c = shape
        # Nose tip: 1
        # Left cheek: 234, Right cheek: 454
        nose_tip = landmarks[1]
        left_cheek = landmarks[234]
        right_cheek = landmarks[454]
        
        # Si le nez est "au milieu" horizontalement des joues
        mid_cheek_x = (left_cheek.x + right_cheek.x) / 2
        
        # Seuil de tolérance
        if abs(nose_tip.x - mid_cheek_x) < 0.05: # Centré
            return True
            
        return False

    def _load_db(self):
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'rb') as f:
                    self.known_embeddings = pickle.load(f)
            except: pass

    def _save_db(self):
        with open(self.db_path, 'wb') as f:
            pickle.dump(self.known_embeddings, f)
