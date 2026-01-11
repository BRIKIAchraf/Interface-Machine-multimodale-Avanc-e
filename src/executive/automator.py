"""
Module d'Automatisation "Executive Hand".
Gère l'interaction Web, la rédaction d'emails de simulation, et les workflows RPA.
"""
import webbrowser
import time
import pyautogui
import urllib.parse
from src.executive.security import SecurityGuard

class Automator:
    def __init__(self, security_guard):
        self.security = security_guard

    def open_search(self, query):
        """Recherche Google intelligente"""
        encoded_query = urllib.parse.quote(query)
        url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open(url)
        return f"Recherche lancée : '{query}'"

    def compose_email(self, recipient, subject, body):
        """
        Ouvre le client mail par défaut avec un brouillon pré-rempli.
        Compatible mailto: pour une portabilité maximale sans config SMTP.
        """
        # Nettoyage basique
        if self.security.scan_for_sensitive_data(body):
            print("⚠️ Attention: L'email contient des données sensibles.")
        
        encoded_subject = urllib.parse.quote(subject)
        encoded_body = urllib.parse.quote(body)
        mailto_link = f"mailto:{recipient}?subject={encoded_subject}&body={encoded_body}"
        
        webbrowser.open(mailto_link)
        return f"Brouillon email ouvert pour {recipient}"

    def fill_form_simulation(self, data_dict):
        """
        Simule le remplissage de formulaire par tabulation + écriture.
        Très basique mais universel.
        """
        print("🤖 Début du remplissage automatique...")
        time.sleep(2) # Temps pour l'utilisateur de cliquer sur le premier champ
        
        for key, value in data_dict.items():
            # Si c'est une donnée chiffrée (bytes), on ne l'écrit PAS sans auth
            if isinstance(value, bytes):
                print(f"🔒 Champ '{key}' sécurisé - Ignoré sans validation biométrique")
                continue
                
            pyautogui.write(str(value))
            pyautogui.press('tab')
            time.sleep(0.5)
            
        return "Remplissage terminé"

    def navigate_to(self, target):
        """Navigation intelligente basée sur des keywords"""
        targets = {
            "amazon": "https://www.amazon.fr",
            "youtube": "https://www.youtube.com",
            "meteo": "https://weather.com/fr-FR",
            "news": "https://news.google.com"
        }
        
        url = targets.get(target.lower())
        if url:
            webbrowser.open(url)
            return f"Navigation vers {target}"
        else:
            return self.open_search(target)

    def generate_report(self, title, content, filename="rapport.pdf"):
        """Génère un rapport PDF simple (RPA)"""
        try:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=title, ln=1, align="C")
            pdf.multi_cell(0, 10, txt=content)
            pdf.output(filename)
            return f"Rapport généré: {filename}"
        except Exception as e:
            return f"Erreur génération PDF: {e}"
