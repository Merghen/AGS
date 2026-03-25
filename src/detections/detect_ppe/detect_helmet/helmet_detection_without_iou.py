from ultralytics import YOLO
from ..base_ppe_detection_without_iou import BasePPEDetectionWithoutIOU

class HelmetDetection(BasePPEDetectionWithoutIOU):
    """
    Kask tespiti yapılan sınıf.
    """

    def __init__(self, model_path, device=None, helmet_conf=0.4, use_track_count=True, track_count= 10):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.     
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            helmet_conf (float): Kask tespiti için minimum güven eşiği.  
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Her takip ID'si için tutulacak geçmiş etiket sayısı
        """

        super().__init__(model_path, target_label="helmet", device=device, confidence=helmet_conf,
                         use_track_count=use_track_count, track_count=track_count)
    
    def is_target_region_overlap(self, helmet_box, person_box, tolarance=50):
        """
        Kask kutusunun kişi kutusu içinde olup olmadığını kontrol eder.
        
        Args:
            helmet_box (list): Kask kutusunun [x1, y1, x2, y2] koordinatları
            person_box (list): Kişi kutusunun [x1, y1, x2, y2] koordinatları
            tolarance (int): Kask kutusunun kişi kutusunun ne kadar üzerinde olabileceğini belirten limit değeri
        
        Returns:
            bool: Kask kutusu kişi kutusu içinde ( kask kişinin biraz üzerinde de olabilir.) ise True, değilse False
            """
        
        hlx1, hly1, hlx2, hly2 = map(int, helmet_box)
        px1, py1, px2, py2 = map(int, person_box)
        person_height = py2 - py1

        head_height = int(person_height * 0.35)
        head_box = (px1, py1 - tolarance, px2, py1 + head_height)
        hx1, hy1, hx2, hy2 = head_box

        # kask kutusu ile kafa kutusunun çakışıp çakışmadığını kontrol et
        # X çakışması yoksa
        if hlx1 >= hx2 or hlx2 <= hx1:
            return False
        # Y çakışması yoksa
        if hly1 >= hy2 or hly2 <= hy1:
            return False

        return True
    
    
    
    

