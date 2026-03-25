from ultralytics import YOLO
from ..base_ppe_detection_without_iou import BasePPEDetectionWithoutIOU

class MaskDetection(BasePPEDetectionWithoutIOU):
    """
    Maske tespiti yapılan sınıf.
    """

    def __init__(self, model_path, device=None, mask_conf=0.5, use_track_count=True, track_count=5):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.     
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            mask_conf (float): Maske tespiti için minimum güven eşiği. 
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Her takip ID'si için tutulacak geçmiş etiket sayısı 
        """

        super().__init__(model_path, target_label="mask", device=device, confidence=mask_conf,
                         use_track_count=use_track_count, track_count=track_count)
    
    def is_target_region_overlap(self, mask_box, person_box):
        """
        Maske kutusunun kişi kutusu içinde olup olmadığını kontrol eder.
        
        Args:
            mask_box (list): Maske kutusunun [x1, y1, x2, y2] koordinatları
            person_box (list): Kişi kutusunun [x1, y1, x2, y2] koordinatları
        
        Returns:
            bool: Maske kutusu kişi kutusu içinde ise True, değilse False
            """
        
        mx1, my1, mx2, my2 = map(int, mask_box)
        px1, py1, px2, py2 = map(int, person_box)
        person_height = py2 - py1

        head_height = int(person_height * 0.35)
        head_box = (px1, py1, px2, py1 + head_height)
        hx1, hy1, hx2, hy2 = head_box

        # maske kutusu ile kafa kutusunun çakışıp çakışmadığını kontrol et
        # X çakışması yoksa
        if mx1 >= hx2 or mx2 <= hx1:
            return False
        # Y çakışması yoksa
        if my1 >= hy2 or my2 <= hy1:
            return False

        return True
    
