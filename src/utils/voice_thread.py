from PyQt6.QtCore import QThread, pyqtSignal
import threading

class VoiceThread(QThread):
    command_detected = pyqtSignal(str) # Signal émis quand du texte est transcrit

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.recognizer_engine = None
        self.stop_event = threading.Event()

    def run(self):
        try:
            # Initialisation dans le thread pour ne pas bloquer l'UI
            from src.voice.recognizer import VoiceRecognizer
            self.recognizer_engine = VoiceRecognizer()
            
            # Callback pour traiter les commandes vocales
            def on_voice_command(text):
                if text and self._run_flag:
                    print(f"[VOIX]: {text}")
                    self.command_detected.emit(text)
            
            # Lancer l'écoute continue
            self.recognizer_engine.listen_continuous(on_voice_command, self.stop_event)
            
        except Exception as e:
            print(f"Erreur thread voix: {e}")
            self.command_detected.emit(f"ERREUR: {str(e)}")

    def stop(self):
        self._run_flag = False
        self.stop_event.set()
        if self.recognizer_engine:
            self.recognizer_engine.stop_listening()
        self.wait()
