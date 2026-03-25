from .smoke_detection import SmokeDetection
from .smoke_log_info import SmokeInfoLogger

class SmokeProcessor:
    """ 
    Duman tespiti için görüntüyü işleyerek görüntü çıktı sonuçlarını verir.
    """

    def __init__(self, model_path=None, device=None, threshold=0.35, history_count=5):
        """
        Duman tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            threshold (float): Sınıflandırma için güven eşiği.
            history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
        """

        self.smoke_detector = SmokeDetection(model_path=model_path, device=device, smoke_conf=threshold, history_count=history_count)
        self.smoke_info_logger = SmokeInfoLogger()

        
    def process_frame(self, frame,results=None):
        """
        Duman tespitini yapararak sonuç bilgisini dönderir.

        Args:
          frame (np.ndarray): BGR formatında görüntü.
          results (list): Duman tespiti sonuçları.(Aynı model çıktısında perfomrans artışı sağlar).

        Returns:
            dict: Anlık duman analiz sonucunu dönderir.
        """

        is_smoke = self.smoke_detector.detect(frame, results=results)   
        self.smoke_info_logger.set_detection_status(status=is_smoke)

        return self.smoke_info_logger.get_result()
    
#test
if __name__ == "__main__":
    """Model ve video kaynağını ayarlayıp duman tespit işlemini başlatır."""

    from ultralytics import YOLO
    import cv2

    model_path = "models/fire_smoke_last.pt"
    source = "assets/smoke test.mp4"
    smoke = SmokeProcessor(draw=True,threshold=0.40)
    cap = cv2.VideoCapture(source)
    frame_smoke= YOLO(model_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        fire_smoke_res = frame_smoke.predict(source=frame, verbose=False, conf=0.5)
        smoke_result_info = smoke.process_frame(frame,results=fire_smoke_res)
        print(smoke_result_info)
        
        cv2.imshow("Yolov11 - Duman Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()