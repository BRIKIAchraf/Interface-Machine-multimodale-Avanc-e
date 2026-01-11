"""
Centre de Communication (Email & Calendrier).
Gère l'envoi/réception d'emails via SMTP/IMAP et la gestion d'agenda.
Conçu pour être sécurisé et robuste.
"""
import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime

class CommunicationCenter:
    def __init__(self, security_guard):
        self.security = security_guard
        self.email_user = None
        self.email_pass = None
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.imap_server = "imap.gmail.com"
        
        # Mode démo/simulation par défaut si pas de crédentials
        self.simulation_mode = True
        print("📧 CommsCenter: Initialisé (Mode Simulation)")

    def configure_credentials(self, user, password):
        """Configure les identifiants pour le mode réel"""
        self.email_user = user
        self.email_pass = password
        self.simulation_mode = False
        print("📧 CommsCenter: Identifiants configurés. Mode Réel activé.")

    def send_email(self, to_addr, subject, body):
        """Envoie un email (Réel ou Simulé)"""
        if self.simulation_mode:
            print(f"📧 [SIMULATION] Envoi mail à {to_addr} | Sujet: {subject} | Corps: {body}")
            return True, "Email simulé envoyé avec succès."

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_user
            msg['To'] = to_addr
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_pass)
            text = msg.as_string()
            server.sendmail(self.email_user, to_addr, text)
            server.quit()
            return True, "Email envoyé avec succès."
        except Exception as e:
            return False, f"Erreur envoi email: {e}"

    def get_unread_emails(self, limit=5):
        """Récupère les emails non lus (Réel ou Simulé)"""
        if self.simulation_mode:
            # Emails fictifs pour démo
            return [
                {"sender": "boss@company.com", "subject": "Réunion urgente", "body": "Merci de préparer le rapport."},
                {"sender": "newsletter@tech.com", "subject": "Nouvelles IA", "body": "Découvrez les nouveautés..."}
            ]

        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_pass)
            mail.select('inbox')

            status, data = mail.search(None, '(UNSEEN)')
            mail_ids = data[0].split()[-limit:] # Prendre les derniers

            emails = []
            for i in mail_ids:
                status, data = mail.fetch(i, '(RFC822)')
                for response_part in data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        sender = msg['from']
                        subject = msg['subject']
                        # Simplification lecture corps...
                        model = {"sender": sender, "subject": subject, "body": "Contenu..."}
                        emails.append(model)
            return emails
        except Exception as e:
            print(f"Erreur lecture emails: {e}")
            return []

    def add_calendar_event(self, title, date_str):
        """Ajoute un événement au calendrier (Simulé)"""
        # Pour le calendrier réel, il faudrait l'API Google Calendar (OAuth complexe)
        # On reste sur une simulation locale efficace
        print(f"📅 [CALENDRIER] Nouvel événement: {title} le {date_str}")
        return f"Événement '{title}' ajouté pour le {date_str}."
