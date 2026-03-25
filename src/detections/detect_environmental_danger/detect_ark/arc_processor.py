from .arc_detection import ArcDetection
from .arc_log_info import ArcInfoLogger 

class ArcProcessor:
    """ 
    Elektrik ark tespiti için görüntüyü işleyerek görüntü çıktı sonuçlarını verir.

    """
    def __init__(self, model_path, device=None, history_count=3):
        """
        Elektrik arkı tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
            
        """

        self.arc_detector = ArcDetection(model_path=model_path, device=device, history_count=history_count)
        self.arc_info_logger = ArcInfoLogger()

    def process_frame(self, frame):
        """
        Ark tespitini yapararak sonuç bilgisini dönderir.

        Args:
            frame (np.ndarray): BGR formatında görüntü.

        Returns:
            dict: Anlık ark analiz sonucu
        """

        is_ark = self.arc_detector.detect(frame)
        self.arc_info_logger.set_detection_status(status=is_ark)
     
        return self.arc_info_logger.get_result()

# test
if __name__ == "__main__":
    import cv2
    video_path = "assets/videos/youtube_514vYrh17B4_720x1280_h264.mp4"
    arc_model_path="models/mobilenetv2_ark.pth"
    arc = ArcProcessor(model_path=arc_model_path,draw=True)
    cap = cv2.VideoCapture(video_path)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        arc_result_info, frame = arc.process_frame(frame)
        print(arc_result_info)
        
        cv2.imshow("Yolov11 - Ark Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()

