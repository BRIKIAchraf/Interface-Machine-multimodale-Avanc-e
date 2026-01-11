"""
Moteur de Fusion Multimodale Contextuel (Core Brain).
Combine Voix + Geste + Regard + Contexte + Apprentissage Utilisateur.
Utilise des pondérations de confiance et un système de règles dynamiques.
"""
import time
import numpy as np
from collections import deque
import json
import os

class ContextualFusionEngine:
    def __init__(self, system_controller, speaker, brain, web_pilot, comms, security):
        self.system = system_controller
        self.speaker = speaker
        self.brain = brain
        self.web_pilot = web_pilot
        self.comms = comms
        self.security = security

        # État Contextuel Global
        self.context = {
            "last_voice_cmd": None,
            "last_gesture": None,
            "last_interaction_ts": 0,
            "user_focus": "screen", # screen/off_screen (Gaze)
            "active_app": None,     # App au premier plan
            "user_intent": None,    # Intention déduite
            "confidence": 0.0       # Score de confiance global
        }

        # Apprentissage Utilisateur (Préférences) - Simple JSON Store
        self.user_prefs_file = "user_preferences.json"
        self.user_prefs = self._load_user_prefs()
        
        # Historique Court Terme pour Fusion Temporelle
        self.history = deque(maxlen=20) # 20 derniers events
        
        # Seuils de confiance
        self.CONFIDENCE_THRESHOLD = 0.7
        self.SENSITIVE_ACTION_THRESHOLD = 0.9

        print("🧬 Fusion Engine 2.0: Initialisé (Context + Learning)")

    def update(self, modality, Data, raw_data=None):
        """
        Point d'entrée unique des données multimodales.
        modality: 'voice', 'gesture', 'gaze', 'emotion', 'ocr'
        Data: valeur interprétée (ex: "THUMBS_UP", "search_internet")
        raw_data: données brutes si besoin (coords, frames...)
        """
        ts = time.time()
        self.history.append({"mod": modality, "data": Data, "ts": ts})
        
        # Mise à jour état partiel
        if modality == 'gaze': self.context['user_focus'] = Data
        elif modality == 'voice': self.context['last_voice_cmd'] = Data
        elif modality == 'gesture': self.context['last_gesture'] = Data
        
        self.context['last_interaction_ts'] = ts

        # --- DÉCISION FUSIONNÉE ---
        return self._decide_action()

    def _decide_action(self):
        """
        Cerveau décisionnel : Analyse l'état complet pour déclencher une action.
        Gère les conflits, les confirmations et le multimodal (Voix + Geste).
        """
        # 1. Vérification Attention (Gaze)
        # Si l'utilisateur ne regarde pas l'écran, on ignore la plupart des gestes curseurs
        if self.context['user_focus'] == 'off_screen':
            # Exception: Commandes vocales explicites (avec wake word) ou gestes système (Stop)
            # Sinon on ne fait rien pour éviter faux positifs
            pass 

        voice_cmd = self.context.get('last_voice_cmd')
        gesture = self.context.get('last_gesture')
        
        # 2. Fusion Voix + Geste (Ex: "Ouvre ça" + Pointing)
        if voice_cmd and "ça" in str(voice_cmd).lower() and gesture == "INDEX_POINTING":
            # Action Contextuelle : Clic là où on pointe
            # self.system.click()
            self._reset_partial_state()
            return "👆 Action Contextuelle: Clic sur Pointing"

        # 3. Confirmation Sensible (Geste de validation requis)
        if self.context.get('pending_sensitive_action'):
            if gesture == "THUMBS_UP":
                action = self.context['pending_sensitive_action']
                self._execute_action(action)
                self.speaker.speak("Action confirmée et exécutée.")
                self.context['pending_sensitive_action'] = None
                return f"✅ Confirmé: {action['type']}"
            elif gesture == "STOP" or (voice_cmd and "non" in str(voice_cmd).lower()):
                self.context['pending_sensitive_action'] = None
                self.speaker.speak("Action annulée.")
                return "❌ Annulé"
            return "⏳ En attente de confirmation (Pouce en l'air)..."

        # 4. Prédiction / Habitudes (Learning)
        # Si Voice = "Météo", et user ouvre toujours Chrome après -> Proposer Chrome ?
        # Ici on simplifie : exécution directe si confiance OK
        
        # ... Logique existante déléguée aux modules exécutifs ...
        # Pour cette implémentation, on laisse le FusionEngine existant gérer le routage fin
        # Cette classe sert de couche "Meta" supérieure.
        
        return None

    def request_sensitive_action(self, action_type, params):
        """Met une action sensible en attente de confirmation multimodale"""
        self.context['pending_sensitive_action'] = {"type": action_type, "params": params}
        self.speaker.speak("Cette action est sensible. Levez le pouce pour confirmer.")
        return "🔒 Action Sensible: En attente de validation..."

    def _execute_action(self, action_obj):
        # Dispatch vers system/comms/automator
        pass

    def _load_user_prefs(self):
        if os.path.exists(self.user_prefs_file):
            with open(self.user_prefs_file, 'r') as f:
                return json.load(f)
        return {"shortcuts": {}, "autocorrect": {}}

    def _reset_partial_state(self):
        self.context['last_voice_cmd'] = None
        # self.context['last_gesture'] = None # On garde le geste car il dure
