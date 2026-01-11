"""
Module de Synthèse Vocale (TTS - Text-to-Speech).
Utilise le moteur natif de Windows (SAPI.SpVoice) via PowerShell.
Approche 100% native sans dépendance lourde (pyttsx3, etc).
"""
import subprocess
import threading
import time

class Speaker:
    def __init__(self):
        self.queue = []
        self.is_speaking = False
        print("🔊 Speaker: Initialisé (Moteur Windows Natif)")

    def speak(self, text):
        """
        Prononce le texte donné de manière non-bloquante.
        """
        # Lancer dans un thread pour ne pas geler l'UI
        threading.Thread(target=self._speak_thread, args=(text,), daemon=True).start()

    def _speak_thread(self, text):
        # Nettoyage basique pour PowerShell
        safe_text = text.replace('"', '\\"').replace("'", " ")
        
        # Commande PowerShell pour utiliser l'API Speech de .NET
        ps_command = (
            f"Add-Type -AssemblyName System.Speech; "
            f"$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$synth.SelectVoiceByHints('French'); " # Force une voix française si dispo
            f"$synth.Speak('{safe_text}');"
        )
        
        try:
            # -NoProfile pour rapidité, -WindowStyle Hidden pour discrétion
            subprocess.run(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_command], check=False)
        except Exception as e:
            print(f"Erreur TTS: {e}")

# Test rapide si exécuté directement
if __name__ == "__main__":
    s = Speaker()
    s.speak("Bonjour, je suis votre assistant multimodal.")
    time.sleep(2)
