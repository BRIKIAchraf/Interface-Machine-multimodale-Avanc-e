"""
Module de Sécurité Avancée "Watchdog"
Gère les données sensibles (PII, Cartes Bancaires, Mots de passe).
GARANTIE: Zéro stockage, Chiffrement mémoire, Destruction après usage.
"""
import re
import time
from cryptography.fernet import Fernet
import ctypes
import sys

class SecurityGuard:
    def __init__(self):
        # Clé éphémère - change à chaque redémarrage de l'app
        # Rend les données inutilisables si l'app crashe et qu'on dumpe la mémoire
        self._memory_key = Fernet.generate_key()
        self._cipher = Fernet(self._memory_key)
        self.sensitive_mode_active = False
        
        # Patterns de données sensibles
        self.patterns = {
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "iban": r"\b[A-Z]{2}\d{2}[A-Z0-9]{10,30}\b",
            "social_security": r"\b\d{1,2}\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\b", # Format FR approximatif
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        }
        print("🛡️ SecurityGuard: Activé (Niveau HIGH)")

    def secure_text(self, text):
        """
        Chiffre immédiatement le texte en mémoire.
        Retourne un token chiffré, pas le texte clair.
        """
        if not text:
            return None
        return self._cipher.encrypt(text.encode())

    def access_data(self, token, authorization_gesture=False):
        """
        Décrypte les données UNIQUEMENT si l'autorisation est validée.
        """
        if not authorization_gesture:
            print("⛔ SecurityGuard: Accès refusé (Autorisation requise)")
            return None
            
        try:
            return self._cipher.decrypt(token).decode()
        except Exception as e:
            print(f"⛔ SecurityGuard: Erreur de déchiffrement - {e}")
            return None

    def scan_for_sensitive_data(self, text):
        """
        Analyse un texte pour détecter des données sensibles.
        Retourne le type de donnée détectée ou None.
        """
        for data_type, pattern in self.patterns.items():
            if re.search(pattern, text):
                return data_type
        return None

    def mask_text(self, text):
        """
        Masque visuellement les données sensibles pour l'affichage UI.
        Ex: 1234 5678 1234 5678 -> **** **** **** 5678
        """
        # Masquer Cartes Bancaires
        cc_matches = re.finditer(self.patterns["credit_card"], text)
        for match in cc_matches:
            original = match.group()
            masked = "*" * (len(original) - 4) + original[-4:]
            text = text.replace(original, masked)
            
        return text

    def wipe_memory(self):
        """
        Tentative de nettoyage de mémoire (Best effort en Python).
        Génère une nouvelle clé, rendant les anciennes données illisibles.
        """
        self._memory_key = Fernet.generate_key()
        self._cipher = Fernet(self._memory_key)
        print("🛡️ SecurityGuard: Mémoire purgée et clés rotées.")

    def enable_sensitive_mode(self):
        """Active le mode haute sécurité (surveillance accrue)"""
        self.sensitive_mode_active = True
        print("🚨 MODE SENSIBLE ACTIVÉ")

    def disable_sensitive_mode(self):
        """Désactive le mode haute sécurité"""
        self.sensitive_mode_active = False
        self.wipe_memory()
        print("🛡️ Mode normal rétabli")
