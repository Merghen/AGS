from ultralytics import YOLO
import torch

class BaseEnviromentalDetection:
    """ Duman, Ateş ve Ark gibi çevre koşullarının tespiti için temel sınıf 
    Diğer çevre koşulu ile ilgli sınıflar, bu sınıftan miras alır """

    def __init__(self, target_label, model_path=None, device=None, confidence=0.5, history_count=5):
        """
        Args:
            model_path (str): Eğitilmiş modelin yolu
            target_label (str): Modelde kontrol edilecek etiket (helmet, vest, glasses, mask vb.)
            device (str): CPU veya GPU
            confidence (float): Minimum güven eşiği
            track_count (int): Stabil sonuç için geçmiş etiket sayısı
        """
        self.model = YOLO(model_path) if model_path is not None else None
        device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device) if self.model else None

        self.target_label = target_label
        self.history = []
        self.confidence = confidence
        self.history_count = history_count

    def detect(self, frame, results=None):
        """
        Bir görüntü karesi (frame) üzerinde tespit işlemi yapar.

        Args:
            frame (numpy.ndarray): Tespit yapılacak görüntü karesi
            results (list): Dışarıdan model çıktısı verilmek istenirse (opsiyonel).

        Returns:
           bool: Çevresele tehlikenin tespit edilip edilmediğini dönderir.
        """
        
        if results is None:
            if self.model is None:
                raise ValueError(f"Model veya {self.target_label} tespit sonucu mevcut değil.")
            results = self.model.predict(frame, verbose=False)

        if not results:
            return False
        
        detected = self._is_detected(results)

        self.update_history(detected)
        majority_result=self.get_majority_decision()

        return majority_result
    
    def _is_detected(self, results):
        """
        İlgili çevresel tehditin oluşup oluşmadığını döner.

        Args:
            results (list): YOLO modelinin tespit sonucunu tutar.
        
        Returns:
            bool: Çevresel tehditin oluşup oluşmadığı bilgisi.

        """

        for r in results:
            boxes = r.boxes
            names = r.names

            if not boxes:
                continue

            for box in boxes:
                cls_id = int(box.cls[0])
                label = names[cls_id]
                conf = float(box.conf[0])

                if label == self.target_label and conf >= self.confidence:
                    return True
        
        return False
    
    def update_history(self, is_detected):
        """
        Güncel son (history_count) kadar sonucu kaydeder.
        """

        self.history.append(is_detected)

        if len(self.history) > self.history_count:
            self.history = self.history[-self.history_count:]

    def get_majority_decision(self):
        """
        Son sonuçların çoğunluğunu döndürür.
        True sayısı fazla ise True, değilse False.
        """

        if not self.history:
            return False

        true_count = self.history.count(True)
        false_count = self.history.count(False)

        return true_count >= false_count