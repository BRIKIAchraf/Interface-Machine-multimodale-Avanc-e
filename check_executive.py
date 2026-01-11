
try:
    import easyocr
    import cryptography
    import fpdf
    import pyperclip
    from src.executive.security import SecurityGuard
    print("✅ Modules Exécutifs chargés avec succès")
except ImportError as e:
    print(f"❌ Erreur d'import: {e}")
except Exception as e:
    print(f"❌ Autre erreur: {e}")
