from .vest_log_info import VestInfoLogger
    
class VestProcessor:
    """ 
    Kişi ve yelek tespiti için görüntüyü işleyerek görüntü çıktı sonuçlarını verir.
    """

    def __init__(self, model_path, device= None, vest_threshold=0.3, use_track_count=True, track_count=20, activate_iou=False):
        """
        Yelek ve insan tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            vest_threshold (float): Yelek tespiti için güven eşiği.
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez 
            track_count (int): Her kişi için geçmişte saklanacak yelek etiket sayısını
                               (label sonucu bu etiketlerin ortalaması alınarak belirlenir)
            activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
            False ise tüm kare üzerinde çalışır.
        """
        if activate_iou:
            from .vest_detection_with_iou import VestDetection
        else:
            from .vest_detection_without_iou import VestDetection
        self.vest_detector = VestDetection(model_path=model_path, device=device, vest_conf=vest_threshold,
                                           use_track_count=use_track_count, track_count=track_count)
        self.vest_info_logger = VestInfoLogger()

    def process_frame(self, frame, person_detections):
        """
        Kişinin yelek takma durmunu analiz ederek sonuç bilgisini dönderir.

        Args:
          frame (np.ndarray): BGR formatında görüntü.
          person_detections (list): Kişi tespit sonuçları.

        Returns:
            dict: Anlık görüntü analiz sonucunu dönderir.
        """

        results = self.vest_detector.detect(frame, person_detections=person_detections)
        self.vest_info_logger.set_default()

        if results:
                self.vest_info_logger.set_detection_status(True)
                for r in results:
                    label = r['label']
                    track_id = r['track_id']
                    status=True if label=="vest" else False

                    self.vest_info_logger.add_detection(track_id, status)
        else:
            self.vest_info_logger.set_detection_status(False)
        
        return self.vest_info_logger.get_result()

#test
if __name__=="__main__":  
    """Model ve video kaynağını ayarlayıp yelek tespit işlemini başlatır."""
    from person_detect import PersonDetection
    import cv2
    model_path = "models/last_vest.pt"
    source = "assets/test_video.mp4"

    vest = VestProcessor(model_path=model_path,draw=True,vest_threshold=0.4,track_count=10)
    person_detector = PersonDetection("models/yolo11n.pt",draw=False)
    cap = cv2.VideoCapture(source)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        person_res = person_detector.detect(frame)
        vest_result_info = vest.process_frame(frame, person_res)
        print(vest_result_info)
        
        cv2.imshow("Yolov11 - Yelek Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()