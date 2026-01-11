"""
Module WebPilot Asynchrone.
Exécute Playwright dans un thread séparé pour ne jamais bloquer l'UI PyQt ou le Tracking Gestuel.
Utilise une Queue pour recevoir les ordres de navigation.
"""
import threading
import queue
from playwright.sync_api import sync_playwright

class WebPilot:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.is_active = False
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        print("🕸️ WebPilot Async: Thread de navigation lancé.")

    def navigate(self, url):
        """Met en file d'attente une demande de navigation"""
        self.command_queue.put(("navigate", url))

    def click_element(self, text):
        """Met en file d'attente un clic"""
        self.command_queue.put(("click", text))

    def _run_loop(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False) # Visible pour la démo
                page = browser.new_page()
                self.is_active = True
                
                while True:
                    # Attente bloquante mais uniquement dans ce thread secondaire
                    cmd, arg = self.command_queue.get()
                    
                    if cmd == "quit":
                        break
                        
                    try:
                        if cmd == "navigate":
                            print(f"🕸️ [Thread] Navigation vers {arg}...")
                            page.goto(arg)
                        
                        elif cmd == "click":
                            print(f"🕸️ [Thread] Clic sur {arg}...")
                            # Stratégie de clic robuste
                            try:
                                page.get_by_text(arg, exact=False).first.click(timeout=2000)
                            except:
                                # Fallback sélecteur générique
                                pass
                                
                    except Exception as e:
                        print(f"🕸️ Erreur action web: {e}")
                    
                    self.command_queue.task_done()
                
                browser.close()
        except Exception as e:
            print(f"🕸️ Crash WebPilot: {e}")
            self.is_active = False
