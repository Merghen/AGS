from ultralytics import YOLO
import torch
from ..base_ppe_detection_without_iou import BasePPEDetectionWithoutIOU

class GlassesDetection(BasePPEDetectionWithoutIOU):
    """
    Gözlük tespiti yapılan sınıf.
    """
    def __init__(self, model_path, device=None, glasses_conf=0.45, use_track_count=True, track_count=30):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu)       
            glasses_conf (float): Gözlük tespiti için güven eşiği
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Her takip ID'si kontrol edilecek güncel etiket sayısı
        """

        super().__init__(model_path, target_label="glasses", device=device, confidence=glasses_conf,
                          use_track_count=use_track_count, track_count=track_count)

    def is_target_region_overlap(self, glasses_box, person_box):
        """
        Gözlük kutusunun, kişi kutusunun baş bölgesi içinde olup olmadığını kontrol eder.
        
        Args:
            glasses_box (list): Gözlük kutusunun [x1, y1, x2, y2] koordinatları
            person_box (list): Kişi kutusunun [x1, y1, x2, y2] koordinatları
        
        Returns:
            bool: kişinin gözlük takıp takmadığı bilgisi
        """

        gx1, gy1, gx2, gy2 = map(int, glasses_box)
        px1, py1, px2, py2 = map(int, person_box)

        person_height = py2 - py1
        person_width = px2 - px1
        aspect_ratio = person_height / person_width

        # Kişi kutusu çok kısa ise bunun kafa kısmı olduğu varsılayarak, baş bölgesi olarak tüm kutuyu al
        if aspect_ratio < 1.5:
            head_box = (px1, py1, px2, py2)
        else:
            # Başın yüksekliğini kişi kutusunun yüksekliğinin %35'u olarak al
            head_height = int(person_height * 0.35)
            head_box = (px1, py1, px2, py1 + head_height)

        hx1, hy1, hx2, hy2 = head_box
        return hx1 <= gx1 and hy1 <= gy1 and hx2 >= gx2 and hy2 >= gy2
    
    
    
    

    


