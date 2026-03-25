from ultralytics import YOLO
from ..base_enviromental_detection import BaseEnviromentalDetection

class ArcDetection(BaseEnviromentalDetection):
    """
    Ark tespiti yapılan sınıf.
    """

    def __init__(self, model_path, device=None, history_count=3):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu. 
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
        """

        super().__init__(model_path=model_path, target_label="ark", device=device, history_count=history_count)

    def detect(self, frame):
        """
        Bir görüntü karesi (frame) üzerinde tespit işlemi yapar.

        Args:
            frame (numpy.ndarray): Tespit yapılacak görüntü karesi

        Returns:
            bool: Ark tespitinin var olup olmadığını tutar.
        """

        results = self.model.predict(frame,verbose=False)
        pred_class = results[0].probs.top1  # en yüksek olasılıklı sınıf indexi
        class_name = self.model.names[pred_class]
        is_ark = (class_name == "ark")

        self.update_history(is_ark)
        majority_result=self.get_majority_decision()

        return majority_result
          