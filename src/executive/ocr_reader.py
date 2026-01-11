"""
Module OCR & Vision pour l'Assistant Exécutif.
Gère la lecture de documents, écrans, et cartes.
Intègre EasyOCR pour une reconnaissance robuste.
"""
import cv2
import numpy as np
import easyocr
import threading
from src.executive.security import SecurityGuard

class VisualIntelligence:
    def __init__(self, security_guard):
        self.security = security_guard
        # Initialisation lazy pour ne pas ralentir le démarrage
        self.reader = None
        self.is_ready = False
        
        # Lancer le chargement du modèle en arrière-plan
        threading.Thread(target=self._load_model, daemon=True).start()

    def _load_model(self):
        print("👁️ Chargement du modèle OCR (support FR/EN)...")
        try:
            # gpu=False pour compatibilité maximale, True si CUDA dispo
            self.reader = easyocr.Reader(['fr', 'en'], gpu=False) 
            self.is_ready = True
            print("👁️ Modèle OCR prêt.")
        except Exception as e:
            print(f"👁️ Erreur chargement OCR: {e}")

    def read_screen_region(self, region=None):
        """
        Lit le texte sur une région de l'écran.
        region: (left, top, width, height)
        """
        import pyautogui
        screenshot = pyautogui.screenshot(region=region)
        img = np.array(screenshot)
        return self.read_image(img)

    def read_image(self, img_array):
        """
        Extrait le texte d'une image numpy (OpenCV/Screenshot).
        Retourne : (text_clean, secure_token)
        """
        if not self.is_ready:
            return "OCR en cours de chargement...", None

        try:
            results = self.reader.readtext(img_array)
            full_text = " ".join([res[1] for res in results])
            
            # Analyse de sécurité immédiate
            sensitive_type = self.security.scan_for_sensitive_data(full_text)
            
            if sensitive_type:
                print(f"🚨 DONNÉE SENSIBLE DÉTECTÉE: {sensitive_type}")
                # Chiffrer immédiatement
                token = self.security.secure_text(full_text)
                # Retourner version masquée pour UI
                masked_text = self.security.mask_text(full_text)
                return masked_text, token
            
            return full_text, None
            
        except Exception as e:
            print(f"Erreur lecture OCR: {e}")
            return "", None

    def extract_form_fields(self, img_array):
        """
        Essaie d'identifier des champs clé-valeur dans une image de document.
        Ex: "Nom: Dupont" -> {"Nom": "Dupont"}
        """
        text, _ = self.read_image(img_array)
        data = {}
        
        # Heuristiques simples (à améliorer avec LLM)
        lines = text.split('\n')
        for line in lines:
            if ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    key = parts[0].strip()
                    val = ":".join(parts[1:]).strip()
                    data[key] = val
                    
        return data
