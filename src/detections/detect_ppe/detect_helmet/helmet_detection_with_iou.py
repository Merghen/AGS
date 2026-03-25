from ultralytics import YOLO
from ..base_ppe_detection_with_iou import BasePPEDetectionWithIOU

class HelmetDetection(BasePPEDetectionWithIOU):
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
    
    def is_target_region_overlap(self, helmet_box, crop_shape):
        """
        Kask kutusunun kişi kutusu içinde olup olmadığını kontrol eder.
        
        Args:
            helmet_box (list): Kask kutusunun [x1, y1, x2, y2] koordinatları
            crop_shape (tuple): Kesilmiş kişinin h,w,c tutar.
        
        Returns:
            bool: Kask kutusu kişi kutusu içinde ise True, değilse False
            """
        
        hlx1, hly1, hlx2, hly2 = map(int, helmet_box)
        h, w, _ = crop_shape
        head_height = int(h * 0.35)
        head_box = (0, 0, w, head_height)
        hx1, hy1, hx2, hy2 = head_box

        # kask kutusu ile kafa kutusunun çakışıp çakışmadığını kontrol et
        # X çakışması yoksa
        if hlx1 >= hx2 or hlx2 <= hx1:
            return False
        # Y çakışması yoksa
        if hly1 >= hy2 or hly2 <= hy1:
            return False
            
        return True
    
    
    
    

