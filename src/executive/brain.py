"""
Cerveau HYBRIDE (Dual Brain Architecture).
Combine l'intelligence omnisciente du Cloud (OpenAI GPT-4) 
avec la rapidité et l'autonomie du Local (Flan-T5).
Assure une disponibilité 100% même sans Internet.
"""
import os
import json
# Gestion optionnelle des imports si OpenAI pas installé
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class NeuroCommander:
    def __init__(self):
        print("🧠 DualBrain: Initialisation de l'architecture Bicamérale...")
        
        # 1. Cerveau Gauche (Logique / Cloud / GPT-4)
        self.cloud_ready = False
        self.api_key = os.getenv("OPENAI_API_KEY")
        if self.api_key and OpenAI:
            try:
                self.client = OpenAI(api_key=self.api_key)
                self.cloud_ready = True
                print("☁️ Cortex Cloud: Connecté (GPT-4 Mode).")
            except Exception as e:
                print(f"☁️ Erreur Cortex Cloud: {e}")
        else:
            print("☁️ Cortex Cloud: Inactif (Pas de clé API ou lib manquante).")

        # 2. Cerveau Droit (Réflexe / Local / T5)
        self.local_ready = False
        try:
            print("🏠 Cortex Local: Chargement du modèle Flan-T5...")
            # On utilise un petit modèle pour être rapide (small)
            self.tokenizer = AutoTokenizer.from_pretrained("google/flan-t5-small")
            self.model = AutoModelForSeq2SeqLM.from_pretrained("google/flan-t5-small")
            self.local_ready = True
            print("🏠 Cortex Local: Prêt & Autonome.")
        except Exception as e:
            print(f"🏠 Erreur Cortex Local: {e}")

        # Tools Definition (Pour GPT-4)
        self.tools = [
            {"type": "function", "function": {"name": "web_search", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "system_command", "parameters": {"type": "object", "properties": {"command": {"type": "string", "enum": ["notepad", "calc", "close_window", "screenshot"]}}, "required": ["command"]}}},
            {"type": "function", "function": {"name": "send_email", "parameters": {"type": "object", "properties": {"recipient": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}}, "required": ["recipient"]}}},
            {"type": "function", "function": {"name": "web_click", "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}}}
        ]
        
        self.is_ready = self.cloud_ready or self.local_ready

    def analyze_intent(self, text):
        """
        Route la demande vers le cerveau le plus capable.
        """
        # Essai Cloud d'abord (Plus intelligent)
        if self.cloud_ready:
            try:
                return self._query_gpt4(text)
            except Exception as e:
                print(f"⚠️ Cloud Failure ({e}). Basculement sur Local...")

        # Fallback Local (Plus rapide/sûr)
        if self.local_ready:
            return self._query_local_t5(text)
            
        return "unknown", 0.0, {}

    def _query_gpt4(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": "Tu es JARVIS. Agis sur le PC. Réponds court."}, {"role": "user", "content": text}],
            tools=self.tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        if msg.tool_calls:
            t = msg.tool_calls[0]
            name = t.function.name
            args = json.loads(t.function.arguments)
            
            # Mapping standard vers les intents FusionEngine
            if name == "web_search": return "search_internet", 1.0, args
            if name == "send_email": return "send_email", 1.0, args
            if name == "system_command": 
                cmd = args.get('command')
                if cmd == "notepad": return "open_application", 1.0, {"app": "notepad"}
                if cmd == "calc": return "open_application", 1.0, {"app": "calculatrice"}
                if cmd == "close_window": return "system_control", 1.0, {"action": "close"}
                return "system_control", 1.0, args
            if name == "web_click": return "web_click", 1.0, {"target": args.get('text')}
        else:
            return "conversation", 1.0, {"response": msg.content}
        return "unknown", 0, {}

    def _query_local_t5(self, text):
        # Prompt simplifié pour T5 (Few-shot learning in-context)
        # On apprend au modèle à sortir un format pseudo-code
        prompt = f"""
        Translate to action:
        "Cherche météo" -> search("météo")
        "Ouvre Notepad" -> open("notepad")
        "Envoie mail" -> email()
        "Bonjour" -> chat("Bonjour")
        "{text}" -> 
        """
        inputs = self.tokenizer(prompt, return_tensors="pt")
        
        out = self.model.generate(**inputs, max_new_tokens=40)
        res = self.tokenizer.decode(out[0], skip_special_tokens=True)
        # print(f"DEBUG LOCAL T5: {res}")
        
        # Parsing basique T5 output (robustesse minimale)
        if "search" in res: 
            q = res.split('"')[1] if '"' in res else text.replace("Cherche", "")
            return "search_internet", 0.8, {"query": q}
        if "open" in res: 
            return "open_application", 0.8, {"app": "notepad"} # Simplification demo
        if "chat" in res: 
            return "conversation", 0.8, {"response": "Je suis en mode hors-ligne mais je vous écoute."}
        
        return "unknown", 0.5, {}
