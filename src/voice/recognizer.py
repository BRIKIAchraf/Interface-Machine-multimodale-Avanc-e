import speech_recognition as sr
import threading
from queue import Queue
import time

class VoiceRecognizer:
    """
    Reconnaissance vocale utilisant Google Speech Recognition (gratuit, sans API key).
    Alternative légère à Whisper pour éviter les problèmes de dépendances.
    """
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_listening = False
        
        # Ajuster les paramètres pour de meilleures performances
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        
        print("VoiceRecognizer initialisé (Google Speech Recognition)")
        
        # Tester la disponibilité du microphone
        try:
            with sr.Microphone() as source:
                print("Microphone détecté et prêt")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
        except Exception as e:
            print(f"Attention: Problème avec le microphone - {e}")

    def listen_once(self, timeout=5, phrase_time_limit=5):
        """
        Écoute une fois et retourne le texte transcrit.
        """
        try:
            with sr.Microphone() as source:
                print("Écoute en cours...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                
                try:
                    # Utiliser Google Speech Recognition (gratuit)
                    text = self.recognizer.recognize_google(audio, language='fr-FR')
                    print(f"Reconnu: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Parole non comprise")
                    return ""
                except sr.RequestError as e:
                    print(f"Erreur du service de reconnaissance: {e}")
                    return ""
                    
        except sr.WaitTimeoutError:
            return ""
        except Exception as e:
            print(f"Erreur d'écoute: {e}")
            return ""

    def listen_continuous(self, callback, stop_event):
        """
        Écoute en continu et appelle le callback avec le texte reconnu.
        """
        self.is_listening = True
        
        with sr.Microphone() as source:
            print("Ajustement au bruit ambiant...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Écoute continue activée")
            
            while not stop_event.is_set() and self.is_listening:
                try:
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    
                    # Reconnaissance en arrière-plan pour ne pas bloquer
                    def recognize_thread():
                        try:
                            text = self.recognizer.recognize_google(audio, language='fr-FR')
                            if text:
                                callback(text)
                        except sr.UnknownValueError:
                            pass
                        except sr.RequestError as e:
                            print(f"Erreur service: {e}")
                    
                    threading.Thread(target=recognize_thread, daemon=True).start()
                    
                except sr.WaitTimeoutError:
                    continue
                except Exception as e:
                    if not stop_event.is_set():
                        print(f"Erreur écoute: {e}")
                    time.sleep(0.1)
        
        self.is_listening = False
        print("Écoute continue arrêtée")

    def stop_listening(self):
        """Arrête l'écoute continue"""
        self.is_listening = False
