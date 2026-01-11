"""
Module Offline Voice Recognition (Vosk).
Permet la commande vocale sans internet, robuste et rapide.
Fallback ideal si l'API Google échoue ou pour la confidentialité.
"""
import json
import pyaudio
import threading
from vosk import Model, KaldiRecognizer
import os

class OfflineVoiceRecognizer:
    def __init__(self, language="fr"):
        self.model_path = f"models/vosk-model-small-{language}" # Chemin à adapter
        self.is_ready = False
        self.rec = None
        
        # Vérification présence modèle
        if not os.path.exists(self.model_path):
            print(f"⚠️ Vosk Modèle introuvable dans {self.model_path}. Mode Offline inactif.")
            # En prod, on pourrait télécharger automatiquement le modèle ici.
            return

        try:
            print("🎙️ Chargement Modèle Vocal Offline (Vosk)...")
            model = Model(self.model_path)
            self.rec = KaldiRecognizer(model, 16000)
            self.is_ready = True
            print("🎙️ Mode Offline Prêt.")
        except Exception as e:
            print(f"Erreur Init Vosk: {e}")

    def listen_loop(self, callback, stop_event):
        """Boucle d'écoute audio non-bloquante"""
        if not self.is_ready: return

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8000)
        stream.start_stream()

        while not stop_event.is_set():
            data = stream.read(4000, exception_on_overflow=False)
            if self.rec.AcceptWaveform(data):
                res = json.loads(self.rec.Result())
                text = res['text']
                if text:
                    print(f"🎙️ [OFFLINE INTENT]: {text}")
                    callback(text)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
