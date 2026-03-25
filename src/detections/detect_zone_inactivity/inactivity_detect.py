import time
import numpy as np

class InactivityDetector:
    """ Kişinin hareketsiz kalma durumunu tespit eder ve süreyi hesaplar."""

    def __init__(self,  movement_threshold=15, max_idle_time=50):
        """
        Args:
            movement_threshold (float): Kişinin hareketli olarak nitelendirilmesi için piksel cinsinden değişim.
                                         Bu eşik değerinden az değişim olursa kişi hareketsiz kabul edilir.
            max_idle_time (float): Kişinin hareketsiz olarak nitelendirilmesi için gereken maksimum süre (saniye). 
        """
        
        self.movement_threshold = movement_threshold
        self.max_idle_time=max_idle_time
        self.person_states = {} # kişinin güncel merkez noktası ve son hareket zamanını tutar

    def update_position(self, person_id, bbox):
        """
         Kişinin bounding box'u ve ID'si ile konum bilgisini günceller.
        
        Args:
            person_id (int): Kişinin takip ID'si.
            bbox (tuple): Kişinin bounding box'u (x1, y1, x2, y2).

        """
        center = self.get_center(bbox)
        current_time = time.time()

        if person_id not in self.person_states:
            self.person_states[person_id] = {
                "last_position": center,
                "last_move_time": current_time
            }
            return
            
        last_position = self.person_states[person_id]["last_position"]

        if self.has_moved(last_position, center):
            self.person_states[person_id]["last_position"] = center
            self.person_states[person_id]["last_move_time"] = current_time

    def get_center(self, bbox):
        """
        tespit edilen kişinin merkez noktasını döner.
        
        Args:
            bbox (tuple): Kişinin bounding box'u (x1, y1, x2, y2).
            
        Returns:
            tuple: Kişinin merkez noktası (x, y)."""

        x1, y1, x2, y2 = bbox
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        center=(center_x, center_y)
        return center

    def has_moved(self, last_position, new_position):
        """
        Kişinin hareket edip etmediğini kontrol eder.
        
        Args:
            last_position (tuple): Kişinin önceki merkez noktası (x, y).    
            new_position (tuple): Kişinin yeni merkez noktası (x, y).
        
        Returns:
            bool: Kişi hareket ettiyse True, etmediyse False."""
        
        distance = np.linalg.norm(np.array(new_position) - np.array(last_position))
        return distance > self.movement_threshold
    
    def get_status(self, person_id):
        """
        Kişinin hareketsiz olup olmadığını döner.
        
        Args:
            person_id (int): Kişinin takip ID'si.
            
        Returns:
            bool/None: Kişi hareket ediyorsa ise True, hareketsiz ise False, kişi bulunamazsa None döner."""

        if person_id not in self.person_states:
            return None

        current_time = time.time()
        last_move_time = self.person_states[person_id]["last_move_time"]
        idle_time = current_time - last_move_time

        if idle_time > self.max_idle_time:
            return False # hareketsiz
        else: 
            return True # hareketli

    def get_idle_time(self, person_id):
        """
        Kişinin hareketsiz kaldığı süreyi döner.
        
        Args:
            person_id (int): Kişinin takip ID'si.
        
        Returns:
            float: Kişinin hareketsiz kaldığı süre (saniye). Kişi bulunamazsa 0.0 döner."""

        if person_id not in self.person_states:
            return 0.0

        current_time = time.time()
        last_move_time = self.person_states[person_id]["last_move_time"]
        return current_time - last_move_time
    
