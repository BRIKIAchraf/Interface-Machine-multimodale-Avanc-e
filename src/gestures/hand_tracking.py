import cv2
import mediapipe as mp
import time
import math

class HandTracker:
    """
    Module de suivi des mains utilisant MediaPipe.
    Fournit 21 landmarks par main pour une reconnaissance gestuelle précise.
    """
    def __init__(self, mode=False, max_hands=2, detection_con=0.7, track_con=0.7):
        """
        Initialise le tracker MediaPipe Hands.
        :param mode: Static Image Mode (False pour webcam stream)
        :param max_hands: Nombre maximum de mains à détecter
        :param detection_con: Seuil de confiance pour la détection
        :param track_con: Seuil de confiance pour le suivi
        """
        self.mode = mode
        self.max_hands = max_hands
        self.detection_con = detection_con
        self.track_con = track_con

        # Initialisation de MediaPipe Hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.max_hands,
            min_detection_confidence=self.detection_con,
            min_tracking_confidence=self.track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tips_ids = [4, 8, 12, 16, 20]
        self.results = None

    def find_hands(self, img, draw=True):
        """
        Traite l'image et détecte les mains.
        :param img: Image BGR (OpenCV)
        :param draw: Si True, dessine les landmarks sur l'image
        :return: Image traitée
        """
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)

        if self.results.multi_hand_landmarks:
            for hand_lms in self.results.multi_hand_landmarks:
                if draw:
                    self.mp_draw.draw_landmarks(img, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return img

    def find_position(self, img, hand_no=0, draw=True):
        """
        Récupère les positions (x, y) de tous les landmarks pour une main spécifique.
        :param img: Image pour référence de dimensions
        :param hand_no: Index de la main à analyser (0 ou 1)
        :param draw: Dessiner des points spécifiques (bounding box, tips)
        :return: Liste de [id, x, y] pour les 21 landmarks
        """
        lm_list = []
        if self.results and self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_no:
                my_hand = self.results.multi_hand_landmarks[hand_no]
                h, w, c = img.shape
                
                x_min, y_min = w, h
                x_max, y_max = 0, 0

                for id, lm in enumerate(my_hand.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append([id, cx, cy])
                    
                    # Pour la bounding box
                    if cx < x_min: x_min = cx
                    if cx > x_max: x_max = cx
                    if cy < y_min: y_min = cy
                    if cy > y_max: y_max = cy

                if draw:
                    cv2.rectangle(img, (x_min - 20, y_min - 20), (x_max + 20, y_max + 20), (0, 255, 0), 2)

        return lm_list

    def get_finger_count(self, hand_no=0):
        """
        Compte le nombre de doigts levés.
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return 0
            
        if len(self.results.multi_hand_landmarks) <= hand_no:
            return 0

        # Récupération des landmarks de l'instance
        # Note: Cette méthode est une approximation simplifiée qui ne dépend pas des pixels
        # mais on n'a que self.results qui contient des coords normalisées
        
        my_hand = self.results.multi_hand_landmarks[hand_no]
        fingers = []

        # POUCE (Astuce: x du tip vs x de ip. Dépend main droite/gauche. On assume droite pour simplifier ou on check handedness)
        # Pour une détection robuste sans handedness: regarder la distance au petit doigt ?
        # Simplification: Tip x < IP x (Main Droite). Si Main Gauche, inverse. 
        # On va assumer main droite screen-facing (Selfie mode mirrored often confuses)
        
        if my_hand.landmark[self.tips_ids[0]].x < my_hand.landmark[self.tips_ids[0] - 1].x:
            fingers.append(1)
        else:
            fingers.append(0)

        # 4 DOIGTS
        for id in range(1, 5):
            if my_hand.landmark[self.tips_ids[id]].y < my_hand.landmark[self.tips_ids[id] - 2].y:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers.count(1)

    def find_distance(self, p1_id, p2_id, img, lm_list, draw=True, r=15, t=3):
        """
        Calcule la distance entre deux landmarks.
        """
        if len(lm_list) < max(p1_id, p2_id):
            return 0, img, []

        x1, y1 = lm_list[p1_id][1], lm_list[p1_id][2]
        x2, y2 = lm_list[p2_id][1], lm_list[p2_id][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]
