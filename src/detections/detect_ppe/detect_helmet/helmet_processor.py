from .helmet_log_info import HelmetInfoLogger

class HelmetProcessor:
    """ 
    Kişi ve kask tespiti için görüntüyü işleyerek görüntü çıktı sonuçlarını verir.
    """

    def __init__(self, model_path, device=None, helmet_threshold=0.3, use_track_count=True, track_count=20, activate_iou=False):
        """
        Kask ve insan tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            helmet_threshold (float): Kask tespiti için güven eşiği.
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Her kişi için geçmişte saklanacak kask etiket sayısını
                               (label sonucu bu etiketlerin ortalaması alınarak belirlenir)
            activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
            False ise tüm kare üzerinde çalışır.
                               
        """
        if activate_iou:
            from .helmet_detection_with_iou import HelmetDetection
        else:
            from .helmet_detection_without_iou import HelmetDetection
        self.helmet_detector = HelmetDetection(model_path=model_path, device=device, helmet_conf=helmet_threshold,
                                               use_track_count=use_track_count, track_count=track_count)
        self.helmet_info_logger = HelmetInfoLogger()

    def process_frame(self, frame, person_detections):
        """
        Kişinin kask takma durmunu analiz ederek sonuç bilgisini dönderir.

        Args:
          frame (np.ndarray): BGR formatında görüntü.
          person_detections (list): Kişi tespit sonuçları.

        Returns:
            dict: Anlık görüntü analiz sonucunu dönderir.
        """

        results = self.helmet_detector.detect(frame, person_detections=person_detections) 
        self.helmet_info_logger.set_default()

        if results:
                self.helmet_info_logger.set_detection_status(True)
                for r in results:
                    label = r['label']
                    track_id = r['track_id']
                    status=True if label=="helmet" else False
                    self.helmet_info_logger.add_detection(track_id, status)
        else:
            self.helmet_info_logger.set_detection_status(False)
        
        return self.helmet_info_logger.get_result()

#test
if __name__=="__main__":
    """Model ve video kaynağını ayarlayıp Kask tespit işlemini başlatır."""
    from person_detect import PersonDetection
    import cv2

    model_path = "models/yolov11_helmet.pt"
    source = "assets/vest-helmet-test.mp4"

    helmet = HelmetProcessor(model_path=model_path,draw=True, helmet_threshold=0.4, track_count=10)
    person_detector = PersonDetection("models/yolo11n.pt",draw=False)
    cap = cv2.VideoCapture(source)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        person_res = person_detector.detect(frame)

        helmet_result_info= helmet.process_frame(frame, person_detections=person_res)
        print(helmet_result_info)
        
        cv2.imshow("Yolov11 - Kask Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()