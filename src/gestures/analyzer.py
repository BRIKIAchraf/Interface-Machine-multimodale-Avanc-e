import math
import collections

class GestureAnalyzer:
    def __init__(self):
        self.tip_ids = [4, 8, 12, 16, 20]
        self.last_gesture = None
        self.position_history = collections.deque(maxlen=10)
        self.swipe_threshold = 50
        self.swipe_cooldown = 0
        self.pinch_counter = 0 # Compteur de stabilité pour le clic
        
        # Pour le Zoom
        self.last_zoom_dist = None
        self.zoom_sensitivity = 5

    def analyze_gesture_with_fingers(self, lm_list, finger_count):
        """
        Analyse complète : Statique, Dynamique (Swipe, Zoom), et Spécifique avec stabilisation.
        """
        if not lm_list:
            self.last_zoom_dist = None
            self.pinch_counter = 0
            return "Aucune main"

        # 1. Mise à jour de l'historique (Centre)
        current_center = (lm_list[0][1], lm_list[0][2])
        self.position_history.append(current_center)
        
        # 2. Détection dynamique (SWIPE)
        dynamic_gesture = self._detect_swipe()
        if dynamic_gesture:
            return dynamic_gesture

        # 3. Détection ZOOM
        if len(lm_list) > 8:
            x1, y1 = lm_list[4][1], lm_list[4][2]
            x2, y2 = lm_list[8][1], lm_list[8][2]
            current_dist = math.hypot(x2 - x1, y2 - y1)
            
            if finger_count == 2 and self.last_zoom_dist is not None:
                delta = current_dist - self.last_zoom_dist
                if abs(delta) > self.zoom_sensitivity:
                    self.last_zoom_dist = current_dist
                    if delta > 0: return "ZOOM_IN"
                    else: return "ZOOM_OUT"
            
            if finger_count == 2:
                self.last_zoom_dist = current_dist
            else:
                self.last_zoom_dist = None

        # 4. Détection Statique Spécifique

        # --- THUMBS UP ---
        if finger_count == 1:
            thumb_tip_y = lm_list[4][2]
            index_tip_y = lm_list[8][2]
            if thumb_tip_y < index_tip_y and self._is_thumb_up(lm_list):
                 return "THUMBS_UP"
            return "INDEX_POINTING"

        # --- STOP ---
        if finger_count >= 5:
            return "STOP"

        # --- PINCH (CLIC) AVEC STABILISATION ---
        if len(lm_list) > 8:
            dist_pinch = math.hypot(lm_list[8][1] - lm_list[4][1], lm_list[8][2] - lm_list[4][2])
            
            # Seuil de déclenchement (un peu plus strict)
            pinch_threshold = 30 
            
            if dist_pinch < pinch_threshold:
                self.pinch_counter += 1
            else:
                self.pinch_counter = 0

            # Il faut maintenir le pinch pendant 2 frames minimum pour valider (Anti-tremblement)
            if self.pinch_counter >= 2:
                return "PINCH_CLICK"

        # --- SCROLL (2 doigts collés) ---
        if finger_count == 2:
             # Vérifier que les doigts sont assez proches pour différencier du "V"
             d_scroll = math.hypot(lm_list[8][1]-lm_list[12][1], lm_list[8][2]-lm_list[12][2])
             if d_scroll < 50:
                return "TWO_FINGERS_SCROLL"
        
        # --- Autres ---
        if finger_count == 0:
            return "Poing Fermé"
        
        return "Main Ouverte"

    def _is_thumb_up(self, lm_list):
        thumb_tip = lm_list[4]
        index_pip = lm_list[6] 
        return thumb_tip[2] < index_pip[2]

    def _detect_swipe(self):
        if self.swipe_cooldown > 0:
            self.swipe_cooldown -= 1
            return None

        if len(self.position_history) < 5:
            return None

        start_pos = self.position_history[0]
        end_pos = self.position_history[-1]
        
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        if abs(dx) > self.swipe_threshold and abs(dx) > abs(dy) * 1.5:
            self.swipe_cooldown = 15 
            self.position_history.clear()
            
            if dx > 0: return "Swipe Droite"
            else: return "Swipe Gauche"
                
        return None
