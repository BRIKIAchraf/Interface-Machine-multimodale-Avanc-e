"""
Module de contrôle système pour Windows.
Permet d'exécuter des actions concrètes sur le PC (ouvrir apps, contrôler média, etc.)
"""
import subprocess
import os
import pyautogui
import webbrowser
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
# Try import pycaw, if fails, handle gracefully (user constraint native)
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

class SystemController:
    """
    Contrôleur système pour exécuter des actions sur Windows.
    """
    def __init__(self):
        # Configuration PyAutoGUI
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05 # Plus rapide pour mouvement souris
        
        # Initialisation du contrôle audio
        self.audio_available = False
        if PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self.volume = cast(interface, POINTER(IAudioEndpointVolume))
                self.audio_available = True
            except Exception as e:
                print(f"Contrôle audio non disponible: {e}")
        
        print("SystemController initialisé")
    
    # ========== CONTRÔLE MULTIMÉDIA ==========
    
    def media_play_pause(self):
        """Lecture/Pause média"""
        pyautogui.press('playpause')
        return "⏯️ LECTURE/PAUSE"
    
    def media_next(self):
        """Piste suivante"""
        pyautogui.press('nexttrack')
        return "⏭️ PISTE SUIVANTE"
    
    def media_previous(self):
        """Piste précédente"""
        pyautogui.press('prevtrack')
        return "⏮️ PISTE PRÉCÉDENTE"
    
    def media_stop(self):
        """Arrêt média"""
        pyautogui.press('stop')
        return "⏹️ ARRÊT MÉDIA"
    
    # ========== CONTRÔLE VOLUME ==========
    
    def volume_up(self, amount=0.1):
        """Augmenter le volume"""
        if self.audio_available:
            try:
                current = self.volume.GetMasterVolumeLevelScalar()
                new_volume = min(1.0, current + amount)
                self.volume.SetMasterVolumeLevelScalar(new_volume, None)
                return f"🔊 VOLUME: {int(new_volume * 100)}%"
            except:
                pyautogui.press('volumeup')
                return "🔊 VOLUME +"
        else:
            pyautogui.press('volumeup')
            return "🔊 VOLUME +"
    
    def volume_down(self, amount=0.1):
        """Diminuer le volume"""
        if self.audio_available:
            try:
                current = self.volume.GetMasterVolumeLevelScalar()
                new_volume = max(0.0, current - amount)
                self.volume.SetMasterVolumeLevelScalar(new_volume, None)
                return f"🔉 VOLUME: {int(new_volume * 100)}%"
            except:
                pyautogui.press('volumedown')
                return "🔉 VOLUME -"
        else:
            pyautogui.press('volumedown')
            return "🔉 VOLUME -"
    
    def volume_mute(self):
        """Couper/Rétablir le son"""
        pyautogui.press('volumemute')
        return "🔇 MUTE/UNMUTE"
    
    # ========== APPLICATIONS ==========
    
    def open_browser(self, url="https://www.google.com"):
        """Ouvrir le navigateur"""
        webbrowser.open(url)
        return f"🌐 NAVIGATEUR OUVERT: {url}"
    
    def open_notepad(self):
        """Ouvrir le Bloc-notes"""
        subprocess.Popen(['notepad.exe'])
        return "📝 BLOC-NOTES OUVERT"
    
    def open_calculator(self):
        """Ouvrir la Calculatrice"""
        subprocess.Popen(['calc.exe'])
        return "🔢 CALCULATRICE OUVERTE"
    
    def open_file_explorer(self):
        """Ouvrir l'Explorateur de fichiers"""
        subprocess.Popen(['explorer.exe'])
        return "📁 EXPLORATEUR OUVERT"
    
    def open_command_prompt(self):
        """Ouvrir l'Invite de commandes"""
        subprocess.Popen(['cmd.exe'])
        return "⌨️ CMD OUVERT"
    
    def open_application(self, app_name):
        """Ouvrir une application par nom"""
        try:
            subprocess.Popen([app_name])
            return f"✅ {app_name.upper()} OUVERT"
        except Exception as e:
            return f"❌ ERREUR: {app_name} non trouvé"
    
    # ========== GESTION FENÊTRES ==========
    
    def close_window(self):
        """Fermer la fenêtre active"""
        pyautogui.hotkey('alt', 'f4')
        return "❌ FENÊTRE FERMÉE"
    
    def minimize_window(self):
        """Minimiser la fenêtre active"""
        pyautogui.hotkey('win', 'down')
        return "🔽 FENÊTRE MINIMISÉE"
    
    def maximize_window(self):
        """Maximiser la fenêtre active"""
        pyautogui.hotkey('win', 'up')
        return "🔼 FENÊTRE MAXIMISÉE"
    
    def switch_window(self):
        """Basculer entre les fenêtres (Alt+Tab)"""
        pyautogui.hotkey('alt', 'tab')
        return "🔄 CHANGEMENT FENÊTRE"
    
    def show_desktop(self):
        """Afficher le bureau"""
        pyautogui.hotkey('win', 'd')
        return "🖥️ BUREAU AFFICHÉ"
    
    # ========== PRÉSENTATION / DIAPORAMA ==========
    
    def presentation_next_slide(self):
        """Diapositive suivante (PowerPoint, PDF)"""
        pyautogui.press('right')
        return "➡️ DIAPO SUIVANTE"
    
    def presentation_previous_slide(self):
        """Diapositive précédente"""
        pyautogui.press('left')
        return "⬅️ DIAPO PRÉCÉDENTE"
    
    def presentation_start(self):
        """Démarrer la présentation (F5)"""
        pyautogui.press('f5')
        return "▶️ PRÉSENTATION DÉMARRÉE"
    
    def presentation_exit(self):
        """Quitter la présentation (Échap)"""
        pyautogui.press('esc')
        return "⏹️ PRÉSENTATION ARRÊTÉE"
    
    # ========== NAVIGATION ==========
    
    def scroll_up(self, clicks=3):
        """Défiler vers le haut"""
        pyautogui.scroll(clicks * 100) # Scaling for Windows scroll
        return "⬆️ SCROLL HAUT"
    
    def scroll_down(self, clicks=3):
        """Défiler vers le bas"""
        pyautogui.scroll(-clicks * 100)
        return "⬇️ SCROLL BAS"
    
    def page_up(self):
        """Page précédente"""
        pyautogui.press('pageup')
        return "📄 PAGE HAUT"
    
    def page_down(self):
        """Page suivante"""
        pyautogui.press('pagedown')
        return "📄 PAGE BAS"
    
    # ========== CLAVIER ==========
    
    def press_enter(self):
        """Appuyer sur Entrée"""
        pyautogui.press('enter')
        return "⏎ ENTRÉE"
    
    def press_escape(self):
        """Appuyer sur Échap"""
        pyautogui.press('esc')
        return "⎋ ÉCHAP"
    
    def press_space(self):
        """Appuyer sur Espace"""
        pyautogui.press('space')
        return "␣ ESPACE"
    
    def copy_text(self):
        """Copier (Ctrl+C)"""
        pyautogui.hotkey('ctrl', 'c')
        return "📋 COPIÉ"
    
    def paste_text(self):
        """Coller (Ctrl+V)"""
        pyautogui.hotkey('ctrl', 'v')
        return "📋 COLLÉ"
    
    def undo(self):
        """Annuler (Ctrl+Z)"""
        pyautogui.hotkey('ctrl', 'z')
        return "↩️ ANNULÉ"
    
    def redo(self):
        """Rétablir (Ctrl+Y)"""
        pyautogui.hotkey('ctrl', 'y')
        return "↪️ RÉTABLI"
    
    # ========== SOURIS ==========

    def move_mouse_to_ratio(self, x_ratio, y_ratio):
        """Déplacer la souris à une position relative (0.0 - 1.0)"""
        w, h = pyautogui.size()
        # On clame pour rester dans l'écran
        x = max(0, min(w, int(x_ratio * w)))
        y = max(0, min(h, int(y_ratio * h)))
        # Tweening désactivé pour réactivité max
        try:
            pyautogui.moveTo(x, y, _pause=False)
        except Exception:
            pass # Fail safe trigger
        return None 

    def mouse_down(self):
        pyautogui.mouseDown()
        return "🖱️ CLIC MAINTENU"

    def mouse_up(self):
        pyautogui.mouseUp()
        return "🖱️ CLIC RELÂCHÉ"

    def mouse_click(self):
        """Clic gauche"""
        pyautogui.click()
        return "🖱️ CLIC"
    
    def mouse_right_click(self):
        """Clic droit"""
        pyautogui.rightClick()
        return "🖱️ CLIC DROIT"
    
    def mouse_double_click(self):
        """Double-clic"""
        pyautogui.doubleClick()
        return "🖱️ DOUBLE CLIC"
    
    # ========== SYSTÈME ==========
    
    def lock_screen(self):
        """Verrouiller l'écran"""
        pyautogui.hotkey('win', 'l')
        return "🔒 ÉCRAN VERROUILLÉ"
    
    def take_screenshot(self, filename="screenshot.png"):
        """Prendre une capture d'écran"""
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        return f"📸 CAPTURE: {filename}"
    
    def open_task_manager(self):
        """Ouvrir le Gestionnaire des tâches"""
        pyautogui.hotkey('ctrl', 'shift', 'esc')
        return "📊 GESTIONNAIRE TÂCHES"
    
    def search_windows(self, query=""):
        """Ouvrir la recherche Windows"""
        pyautogui.hotkey('win', 's')
        if query:
            pyautogui.write(query)
        return f"🔍 RECHERCHE: {query if query else 'OUVERTE'}"
