from ultralytics import YOLO
from ..base_ppe_detection_without_iou import BasePPEDetectionWithoutIOU

class VestDetection(BasePPEDetectionWithoutIOU):
    """
    Yelek tespiti yapılan sınıf.
    """

    def __init__(self, model_path, device=None, vest_conf=0.5, use_track_count=True, track_count=5):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.    
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            vest_conf (float): Yelek tespiti için minimum güven eşiği.
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez 
            track_count (int): Her takip ID'si için tutulacak geçmiş etiket sayısı  
        """

        super().__init__(model_path, target_label="vest", device=device, confidence=vest_conf,
                         use_track_count=use_track_count, track_count=track_count)

    def is_target_region_overlap(self, vest_box, person_box):
        """
        Yelek kutusunun kişi kutusu içinde olup olmadığını kontrol eder.
        
        Args:
            vest_box (list): Yelek kutusunun [x1, y1, x2, y2] koordinatları
            person_box (list): Kişi kutusunun [x1, y1, x2, y2] koordinatları
        
        Returns:
            bool: Yelek kutusu kişi kutusu içinde ise True, değilse False
            """

        vx1, vy1, vx2, vy2 = map(int, vest_box)
        px1, py1, px2, py2 = map(int, person_box)
        person_height = py2 - py1

        # Üst gövdenin 25% - 75% arası kısmı göğüs bölgesi kabul edilir
        chest_top = int(py1 + person_height * 0.25)
        chest_bottom = int(py1 + person_height * 0.75)
        chest_box = (px1, chest_top, px2, chest_bottom)

        cx1, cy1, cx2, cy2 = chest_box

        # Çakışma kontrolü
        # X ekseninde çakışma yoksa
        if vx1 >= cx2 or vx2 <= cx1:
            return False
        # Y ekseninde çakışma yoksa
        if vy1 >= cy2 or vy2 <= cy1:
            return False

        return True
    
    
    
    
