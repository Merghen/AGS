from .fire_detection import FireDetection
from .fire_log_info import FireInfoLogger

class FireProcessor:
    """ 
    Ateş tespiti için görüntüyü işler ve ateş tespitini kontrol eder.
    """

    def __init__(self, model_path=None, threshold=0.5, device=None, history_count=10):
        """
        Ateş tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            threshold (float): Sınıflandırma için güven eşiği.
            device (str): Modelin çalışacağı cihaz(cpu,gpu)  
            history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
        """
        self.fire_detector= FireDetection(model_path=model_path,fire_conf=threshold, device=device, history_count=history_count)
        self.fire_info_logger = FireInfoLogger()
        self.pass_time = None 
        
    def process_frame(self, frame, results=None):
        """
        Ateş tespitini yapararak sonuç bilgisini dönderir.

        Args:
            frame (np.ndarray): BGR formatında görüntü.
            results (list): Ateş tespiti sonuçları.(Aynı model çıktısında perfomrans artışı sağlar).

        Returns:
            dict: Anlık ateş analiz sonucunu dönderir.
        """

        isfire = self.fire_detector.detect(frame, results=results)   
        self.fire_info_logger.set_detection_status(status=isfire)
        
        return self.fire_info_logger.get_result()


if __name__ == "__main__":
    """Model ve video kaynağını ayarlayıp yangın tespit işlemini başlatır."""
    from ultralytics import YOLO
    import cv2

    model_path = "models/fire_smoke_last.pt"
    source = "assets/fire_smoke (2).mp4"

    fire = FireProcessor(draw=True,threshold=0.5)
    cap = cv2.VideoCapture(source)
    frame_smoke= YOLO(model_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        fire_smoke_res = frame_smoke.predict(source=frame, verbose=False, conf=0.5)

        fire_result_info, frame = fire.process_frame(frame, fire_smoke_res=fire_smoke_res)
        print(fire_result_info)
        
        cv2.imshow("Yolov11 - Ateş Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()