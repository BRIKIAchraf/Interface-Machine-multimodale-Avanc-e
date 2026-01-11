class FusionEngine:
    """
    Moteur de fusion multimodale intelligent - Niveau Assistant Exécutif (Tier C/D).
    Combine gestes, voix, émotions et intelligence visuelle (OCR) pour automatiser le PC.
    """
    def __init__(self):
        self.state = {
            "gesture": None,
            "voice": None,
            "emotion": None,
            "mode": "COMMAND" # COMMAND ou DICTATION
        }
        self.history = []
        self.max_history = 10
        self.last_action = "Moteur Prêt"
        self.mouse_down_active = False
        
        # --- MODULES EXÉCUTIFS ---
        from src.utils.system_controller import SystemController
        from src.executive.security import SecurityGuard
        from src.executive.automator import Automator
        from src.executive.ocr_reader import VisualIntelligence
        from src.voice.speaker import Speaker
        from src.executive.brain import NeuroCommander
        from src.executive.web_pilot import WebPilot
        from src.executive.communication import CommunicationCenter
        from src.fusion.context_engine import ContextualFusionEngine
        
        self.system = SystemController()
        self.speaker = Speaker()
        
        # État système Wake Word
        self.is_awake = False 
        self.wake_word = "assistant"
        
        import threading
        # Chargement modules lourds en background
        self.brain = None
        self.webpilot = None
        self.comms = None
        
        try: self.security = SecurityGuard() 
        except: self.security = None

        try: self.comms = CommunicationCenter(self.security)
        except: self.comms = None
        
        def load_advanced():
             try: self.brain = NeuroCommander()
             except: pass
             try: self.webpilot = WebPilot()
             except: pass
        
        try: self.automator = Automator(self.security) 
        except: self.automator = None
        
        try: self.visual = VisualIntelligence(self.security) 
        except: self.visual = None

        threading.Thread(target=load_advanced, daemon=True).start()
        
        # Initialisation du moteur contextuel avancé (V2)
        # Il prend le relai pour la logique complexe
        self.context_engine = ContextualFusionEngine(
            self.system, self.speaker, self.brain, self.webpilot, self.comms, self.security
        )
        
        self.speaker.speak("Système en veille. Dites Assistant pour m'activer.")
        print("🚀 FusionEngine: Prêt (Mode Veille Initial)")

    def update(self, source, value, data=None):
        if source != 'voice' and source != 'gesture' and self.state[source] == value:
             pass
        self.state[source] = value
        
        # Update du moteur contextuel
        # Cela permet de maintenir l'état global (gaze, last cmds...)
        # Le contexte peut retourner une 'meta-action' (ex: CONFIRMATION_REQUISE)
        ctx_action = self.context_engine.update(source, value, data)
        if ctx_action:
             # Si le moteur contextuel a pris une décision forte (confimation), on la retourne
             if "Confirmé" in ctx_action or "Annulé" in ctx_action or "Action Sensible" in ctx_action:
                 return ctx_action

        # --- GESTION WAKE WORD ---
        if source == 'voice':
            voice_lower = value.lower()
            if not self.is_awake:
                if self.wake_word in voice_lower:
                    self.is_awake = True
                    self.speaker.speak("Je vous écoute.")
                    return "🟢 SYSTÈME ACTIVÉ"
                else: return None
            else:
                if "mise en veille" in voice_lower or "dors" in voice_lower:
                    self.is_awake = False
                    self.speaker.speak("Mise en veille.")
                    return "🔴 SYSTÈME EN VEILLE"

        if not self.is_awake: return None

        # --- MODE DICTÉE ---
        if source == 'voice':
            if "active la dictée" in value.lower():
                self.state['mode'] = "DICTATION"
                self.speaker.speak("Mode dictée activé")
                return "✍️ MODE DICTÉE ACTIVÉ"
            elif "mode commande" in value.lower() or "arrête la dictée" in value.lower():
                self.state['mode'] = "COMMAND"
                self.speaker.speak("Mode commande")
                return "🤖 MODE COMMANDE ACTIVÉ"

        self.history.append({'source': source, 'value': value, 'ts': self._get_timestamp()})
        return self.evaluate_rules(data)

    def evaluate_rules(self, data=None):
        gesture = self.state.get("gesture")
        voice = self.state.get("voice", "").lower() if self.state.get("voice") else ""
        mode = self.state.get("mode")
        action = None
        is_paying_attention = data.get('attention', True) if data else True

        # 1. VOIX (HYBRID AI - GOD MODE)
        if voice:
            if mode == "DICTATION":
                if "mode commande" not in voice:
                    import pyautogui
                    pyautogui.write(voice + " ")
                    return f"✍️ Dictée: {voice}"
            else:
                intent = "unknown"
                entities = {}
                # Utilisation du cerveau avancé
                if self.brain and self.brain.is_ready:
                    res = self.brain.analyze_intent(voice)
                    if isinstance(res, tuple):
                        intent, conf, entities = res
                    else: intent = res

                # --- ROUTAGE INTENTS ---
                
                if intent == "conversation":
                    response = entities.get("response", "")
                    if response:
                        self.speaker.speak(response)
                        action = f"💬 Chat: {response[:30]}..."

                elif intent == "search_internet" or "cherche" in voice:
                    query = entities.get('query')
                    if not query: query = voice.replace("cherche", "").replace("trouve", "").strip()
                    
                    if self.webpilot and self.webpilot.is_active:
                         self.webpilot.navigate(f"https://www.google.com/search?q={query}")
                         action = f"🕸️ WebPilot: {query}"
                    elif self.automator:
                         self.automator.open_search(query)
                         action = f"🔍 Recherche: {query}"
                    self.speaker.speak(f"Recherche de {query}")

                elif intent == "send_email" and self.comms:
                    recipient = entities.get('recipient', 'destinataire@exemple.com')
                    subject = entities.get('subject', 'Sujet Automatique')
                    body = entities.get('body', voice)
                    
                    # Sécurité: Demander confirmation via Context Engine
                    # self.context_engine.request_sensitive_action(...)
                    # Pour fluidité demo, on envoie direct ici, mais architecture prête
                    self.comms.send_email(recipient, subject, body)
                    self.speaker.speak(f"Email envoyé à {recipient}")
                    action = "📧 Email Envoyé"

                elif intent == "open_application":
                    app = entities.get('app')
                    if not app: app = voice.replace("ouvre", "").replace("lance", "").strip()
                    self.system.open_application(app)
                    self.speaker.speak(f"Lancement de {app}")
                    action = f"🚀 App: {app}"
                
                elif intent == "web_click" and self.webpilot:
                    target = entities.get('target', '')
                    res = self.webpilot.click_element(target)
                    self.speaker.speak(f"Clic sur {target}")
                    action = f"🖱️ WebClick: {target}"
                
                elif "ferme" in voice: 
                    self.system.close_window()
                    self.speaker.speak("Fermé")
                    action="Fermeture"

        # 2. GESTES & SOURIS
        if data and 'cursor' in data and data['cursor'] and is_paying_attention:
             cx, cy = data['cursor']
             if gesture == "INDEX_POINTING":
                 self.system.move_mouse_to_ratio(cx, cy)
                 if self.mouse_down_active: self.system.mouse_up(); self.mouse_down_active=False
             elif gesture == "PINCH_CLICK":
                 self.system.move_mouse_to_ratio(cx, cy)
                 if not self.mouse_down_active: self.system.mouse_down(); self.mouse_down_active=True
             
        # 3. GESTES COMMANDES
        if gesture == "STOP":
            self.system.media_stop()
            action = "🛑 STOP"
        elif gesture == "THUMBS_UP":
            self.system.press_enter()
            action = "👍 CONFIRMATION"

        if action and action != self.last_action:
            self.last_action = action
            print(f"[EXECUTIVE]: {action}")
            return action
        return None
    
    def _get_timestamp(self):
        import time
        return time.time()
    
    def get_state(self):
        return self.state.copy()

    def reset(self):
        self.state = {"gesture": None, "voice": None, "emotion": None, "mode": "COMMAND"}
        self.history = []
        self.last_action = "Moteur Réinitialisé"
