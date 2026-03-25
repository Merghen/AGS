from ultralytics import YOLO
import torch
from ..base_enviromental_detection import BaseEnviromentalDetection

class SmokeDetection(BaseEnviromentalDetection):
    """
    Duman tespiti yapılan sınıf.
    """

    def __init__(self, model_path, device=None, smoke_conf=0.5, history_count=5):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu. 
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            smoke_conf (float): Duman tespiti için güven eşiği    
            history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
        """

        super().__init__(model_path=model_path, target_label="smoke", device=device, confidence=smoke_conf,
                          history_count=history_count)
    
    