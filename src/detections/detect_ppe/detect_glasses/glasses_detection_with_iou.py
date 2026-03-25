from ultralytics import YOLO
import torch
from ..base_ppe_detection_with_iou import BasePPEDetectionWithIOU

class GlassesDetection(BasePPEDetectionWithIOU):
    """
    Kişilerin gözlük takıp takmadığını tespit eden sınıf.
    """

    def __init__(self, model_path, device=None, glasses_conf=0.45, use_track_count=True, track_count= 30):
        """
        Modeli yükler.
        
        Args:
            model_path (str): Eğitilmiş YOLO modelinin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu)    
            glasses_conf (float): Gözlük tespiti için minimum güven eşiği.  
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Her takip ID'si için tutulacak geçmiş etiket sayısı.
        """

        super().__init__(model_path, target_label="glasses", device=device, confidence=glasses_conf,
                          use_track_count=use_track_count, track_count=track_count)

    def is_target_region_overlap(self, glasses_box, crop_shape):
        """
        Gözlük kutusunun, kişinin baş bölgesi içinde olup olmadığını kontrol eder.
        
        Args:
            glasses_box (list): Gözlük kutusunun [x1, y1, x2, y2] koordinatları
            crop_shape (tuple): Kesilmiş kişinin h,w,c tutar.
        
        Returns:
            bool: kişinin gözlük takıp takmadığı bilgisi
        """

        gx1, gy1, gx2, gy2 = map(int, glasses_box)
        h, w, _ = crop_shape
        aspect_ratio = h / w

        if aspect_ratio < 1.5:
            head_box = (0, 0, w, h)
        else:
            head_height = int(h * 0.35)
            head_box = (0, 0, w, head_height)

        hx1, hy1, hx2, hy2 = head_box
        return hx1 <= gx1 and hy1 <= gy1 and hx2 >= gx2 and hy2 >= gy2

    
