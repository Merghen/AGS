from ultralytics import YOLO
from ..base_enviromental_detection import BaseEnviromentalDetection

class FireDetection(BaseEnviromentalDetection):
    """
    Ateş tespiti yapılan sınıf.
    """

    def __init__(self, model_path=None, fire_conf=0.5, device=None, history_count=10):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.    
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            fire_conf (float): ateş tespiti için güven eşiği
            history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
        """

        super().__init__(model_path=model_path, target_label="fire", device=device, confidence=fire_conf,
                          history_count=history_count)
    
    # Bu fonksiyon şimdilik aktif olarak kullanılmıyor.
    def calculate_passed_time(self, pass_time):
        import time
        """
        Başlangıç/Güncel zamanından itibaren geçen süreyi hesaplar.
        
        Args:
            pass_time (float):  Başlangıç zamanını tutar. Eğer None ise geçerli zaman alınır.
        
        Returns:
            tuple: (başlangıç zamanı, geçen süre saniye cinsinden)

        """
        if pass_time is None:
            pass_time = time.time()

        passed_time = round(time.time() - pass_time, 2)
        return pass_time, passed_time

    
