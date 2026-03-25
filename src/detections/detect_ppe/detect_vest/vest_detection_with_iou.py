from ultralytics import YOLO
from ..base_ppe_detection_with_iou import BasePPEDetectionWithIOU

class VestDetection(BasePPEDetectionWithIOU):
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

    def is_target_region_overlap(self, vest_box, crop_shape):
        """
        Yelek kutusunun kişi kutusu içinde olup olmadığını kontrol eder.
        
        Args:
            vest_box (list): Yelek kutusunun [x1, y1, x2, y2] koordinatları
            crop_shape (tuple): Kesilmiş kişinin h,w,c tutar.
        
        Returns:
            bool: Yelek kutusu kişi kutusu içinde ise True, değilse False
            """

        vx1, vy1, vx2, vy2 = map(int, vest_box)
        h, w, _ = crop_shape

        # Göğüs bölgesi: crop yüksekliğinin %25 ile %75 arası
        chest_top = int(h * 0.25)
        chest_bottom = int(h * 0.75)
        chest_box = (0, chest_top, w, chest_bottom)

        cx1, cy1, cx2, cy2 = chest_box

        # X ekseninde çakışma yoksa
        if vx1 >= cx2 or vx2 <= cx1:
            return False

        # Y ekseninde çakışma yoksa
        if vy1 >= cy2 or vy2 <= cy1:
            return False

        return True
    
    
    
    
