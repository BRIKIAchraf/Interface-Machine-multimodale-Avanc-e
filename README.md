# Interface Homme-Machine Multimodale Avancée

## 🎯 Objectif
Système intelligent de contrôle multimodal combinant **gestes**, **voix** et **émotions** pour une interaction homme-machine naturelle et intuitive.

## ✨ Fonctionnalités Implémentées

### 1. 🖐️ Détection de Gestes
- **Technologie**: Segmentation par couleur de peau + Analyse de contours (OpenCV)
- **Gestes détectés**:
  - ✊ Poing Fermé
  - ✋ Main Ouverte  
  - ☝️ Index Pointé
  - ✌️ V de Victoire / Peace
  - 3️⃣ Trois Doigts
  - 4️⃣ Quatre Doigts

- **Fonctionnalités avancées**:
  - Comptage automatique des doigts levés
  - Détection d'enveloppe convexe
  - Analyse des défauts de convexité
  - Affichage en temps réel sur le flux vidéo

### 2. 🎤 Reconnaissance Vocale
- **Technologie**: Google Speech Recognition (gratuit, sans API key)
- **Langue**: Français (fr-FR)
- **Fonctionnalités**:
  - Écoute continue en arrière-plan
  - Ajustement automatique au bruit ambiant
  - Transcription en temps réel
  - Support multi-threading pour ne pas bloquer l'interface

### 3. 😊 Détection d'Émotions
- **Technologie**: OpenCV Haar Cascades
- **Émotions détectées**:
  - 😊 Happy (Joie) - Détection de sourire
  - 😐 Neutral (Neutre)
  - 😢 Sad (Tristesse) - Analyse de l'intensité faciale
  - 😠 Angry (Colère) - Détection de sourcils froncés

- **Fonctionnalités**:
  - Détection de visage en temps réel
  - Analyse des yeux et de la bouche
  - Affichage des rectangles de détection

### 4. 🔗 Fusion Multimodale Intelligente
Le moteur de fusion combine les trois modalités pour prendre des décisions contextuelles.

#### Règles Implémentées:

**Fusion Voix + Geste:**
- Index pointé + "ouvre" / "sélectionne" → 🎯 SÉLECTION ACTIVÉE

**Commandes Vocales:**
- "mode sombre" / "dark mode" → 🌙 MODE SOMBRE
- "mode clair" / "light mode" → ☀️ MODE CLAIR
- "ferme" / "quitte" → ❌ FERMETURE
- "aide" / "help" → ❓ AIDE
- "volume monte" → 🔊 VOLUME +
- "volume baisse" → 🔉 VOLUME -
- "suivant" / "next" → ⏭️ SUIVANT
- "précédent" / "previous" → ⏮️ PRÉCÉDENT

**Gestes Seuls:**
- Poing Fermé → ⏸️ PAUSE / STOP
- Main Ouverte → ✋ PRÊT
- V de Victoire → ✌️ CONFIRMATION

**Fusion Émotion + Geste:**
- Colère + Poing Fermé → ⚠️ ALERTE UTILISATEUR MÉCONTENT
- Joie + Main Ouverte → 😊 UTILISATEUR SATISFAIT

## 🛠️ Installation

### Prérequis
- Python 3.12+
- Webcam fonctionnelle
- Microphone (pour la reconnaissance vocale)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

### Dépendances principales
- `opencv-python` - Traitement d'image et vidéo
- `PyQt6` - Interface graphique
- `SpeechRecognition` - Reconnaissance vocale
- `pyaudio` - Capture audio
- `numpy` - Calculs numériques

## 🚀 Lancement

```bash
python main.py
```

## 📖 Utilisation

### Interface Utilisateur
L'interface affiche:
1. **Flux vidéo** avec superpositions en temps réel
2. **Dashboard** avec 4 panneaux:
   - 🖐️ Geste Détecté
   - 😊 Émotion
   - 🎤 Dernière Commande Vocale
   - ⚡ Action Système (résultat de la fusion)

### Conseils d'utilisation

**Pour les gestes:**
- Placez votre main bien éclairée devant la caméra
- Évitez les arrière-plans de couleur chair
- Gardez une distance de 30-60 cm de la caméra

**Pour la voix:**
- Parlez clairement et distinctement
- Attendez le signal "Écoute en cours" dans la console
- Utilisez les commandes en français

**Pour les émotions:**
- Regardez la caméra de face
- Assurez un bon éclairage du visage
- Les expressions marquées sont mieux détectées

## 🏗️ Architecture du Projet

```
Interface Homme-Machine Multimodale Avancée/
│
├── main.py                          # Point d'entrée
├── requirements.txt                 # Dépendances
├── README.md                        # Ce fichier
│
└── src/
    ├── gestures/                    # Module de gestes
    │   ├── hand_tracking.py         # Détection de mains
    │   └── analyzer.py              # Analyse de gestes
    │
    ├── voice/                       # Module vocal
    │   └── recognizer.py            # Reconnaissance vocale
    │
    ├── emotions/                    # Module émotions
    │   └── detector.py              # Détection d'émotions
    │
    ├── fusion/                      # Moteur de fusion
    │   └── engine.py                # Règles multimodales
    │
    ├── ui/                          # Interface utilisateur
    │   └── main_window.py           # Fenêtre principale
    │
    └── utils/                       # Utilitaires
        ├── video_thread.py          # Thread vidéo
        └── voice_thread.py          # Thread vocal
```

## 🔧 Configuration Avancée

### Ajuster la sensibilité de détection de peau
Dans `src/gestures/hand_tracking.py`:
```python
self.lower_skin = np.array([0, 20, 70], dtype=np.uint8)
self.upper_skin = np.array([20, 255, 255], dtype=np.uint8)
```

### Modifier la langue de reconnaissance vocale
Dans `src/voice/recognizer.py`:
```python
text = self.recognizer.recognize_google(audio, language='fr-FR')
# Changez 'fr-FR' en 'en-US' pour l'anglais
```

### Ajouter de nouvelles règles de fusion
Dans `src/fusion/engine.py`, méthode `evaluate_rules()`:
```python
elif "votre_commande" in voice:
    action = "VOTRE_ACTION"
```

## 🎨 Personnalisation de l'Interface

L'interface utilise PyQt6 avec un thème sombre moderne. Pour personnaliser:
- Modifiez les styles CSS dans `src/ui/main_window.py`
- Ajustez les couleurs dans `setStyleSheet()`

## 🐛 Dépannage

### La webcam ne s'ouvre pas
- Vérifiez qu'aucune autre application n'utilise la webcam
- Essayez de changer l'index de la caméra dans `video_thread.py`:
  ```python
  cap = cv2.VideoCapture(1)  # Essayez 1 au lieu de 0
  ```

### Le microphone ne fonctionne pas
- Vérifiez les permissions du microphone dans Windows
- Installez `pyaudio` correctement:
  ```bash
  pip install pyaudio
  ```

### Les gestes ne sont pas détectés
- Améliorez l'éclairage
- Ajustez les seuils de couleur de peau
- Vérifiez que votre main est bien visible

### La reconnaissance vocale ne fonctionne pas
- Vérifiez votre connexion Internet (Google Speech Recognition nécessite une connexion)
- Testez votre microphone avec un autre logiciel
- Augmentez le volume du microphone

## 📊 Performances

- **FPS Vidéo**: ~25-30 FPS (dépend de la puissance du PC)
- **Latence Gestes**: < 50ms
- **Latence Voix**: 1-2 secondes (dépend de la connexion)
- **Latence Émotions**: ~300ms (analyse toutes les 10 frames)

## 🚀 Améliorations Futures

- [ ] Support multi-utilisateurs
- [ ] Reconnaissance de posture corporelle
- [ ] Détection d'objets pointés
- [ ] Prédiction d'intentions (LSTM)
- [ ] Interface AR avec overlays 3D
- [ ] Support haptique
- [ ] Apprentissage adaptatif personnalisé
- [ ] Export en exécutable standalone

## 📝 Licence

Ce projet est développé à des fins éducatives et de recherche.

## 👥 Contribution

Pour contribuer:
1. Forkez le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📧 Contact

Pour toute question ou suggestion, n'hésitez pas à ouvrir une issue sur GitHub.

---

**Développé avec ❤️ pour l'interaction homme-machine du futur**
