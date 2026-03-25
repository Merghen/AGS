from .glasses_log_info import GlassesInfoLogger

class GlassesProcessor:
    """ 
    Kişi ve gözlük tespiti için görüntüyü işleyerek görüntü çıktı sonuçlarını verir.
    """

    def __init__(self, model_path, device=None, glasses_threshold=0.4, track_count=10, use_track_count=True, activate_iou=False):
        """
        Gözlük ve insan tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            glasses_threshold (float): Gözlük tespiti için güven eşiği.
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Her kişi için geçmişte saklanacak gözlük etiket sayısını
                               (label sonucu bu etiketlerin ortalaması alınarak belirlenir)
            activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
            False ise tüm kare üzerinde çalışır.
        """

        if activate_iou:
            from .glasses_detection_with_iou import GlassesDetection
        else:
            from .glasses_detection_without_iou import GlassesDetection

        self.glasses_detector = GlassesDetection(model_path=model_path, device=device, glasses_conf=glasses_threshold,
                                                 use_track_count=use_track_count, track_count=track_count)
        self.glasses_info_logger = GlassesInfoLogger()

    def process_frame(self, frame, person_detections):
        """
        Kişinin gözlük takma durmunu analiz ederek sonuç bilgisini dönderir.

        Args:
          frame (np.ndarray): BGR formatında görüntü.
          person_detections (list): Kişi tespit sonuçları.

        Returns:
          dict: Anlık görüntü analiz sonucunu dönderir.
        """

        results = self.glasses_detector.detect(frame, person_detections=person_detections)
        self.glasses_info_logger.set_default()

        if results:
                self.glasses_info_logger.set_detection_status(True)
                for r in results:
                    label = r['label']
                    track_id = r['track_id']
                    status=True if label=="glasses" else False

                    self.glasses_info_logger.add_detection(track_id, status)
        else:
            self.glasses_info_logger.set_detection_status(False)
        
        return self.glasses_info_logger.get_result()
  
#test
def main():
    """Model ve video kaynağını ayarlayıp gözlük tespit işlemini başlatır."""
    from person_detect import PersonDetection
    import cv2

    model_path = "models/yolov11_glasses.pt"
    source = "assets/glasses_test.mp4"

    glasses = GlassesProcessor(model_path=model_path,draw=True, glasses_threshold=0.4, track_count=5)
    person_detector = PersonDetection("models/yolo11n.pt",draw=False)
    cap = cv2.VideoCapture(source)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        person_res = person_detector.detect(frame)

        glasses_result_info = glasses.process_frame(frame, person_detections=person_res)
        print(glasses_result_info)
        
        cv2.imshow("Yolov11 - Gözlük Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main() 
    