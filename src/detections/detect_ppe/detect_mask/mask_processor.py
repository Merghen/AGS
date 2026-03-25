from .mask_log_info import MaskInfoLogger

class MaskProcessor:
    """ 
    Maske tespiti için görüntüyü işler ve maske tespitini kontrol eder.
    """

    def __init__(self, model_path, device=None, mask_threshold=0.5, use_track_count=True, track_count=20, activate_iou=False):
        """
        ateş tespiti için gerekli parametreleri ayarlar.

        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            mask_threshold (float): Maske takıyor olması için güven eşiği. 
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Geçmişte saklanacak maske etiket sayısını
                               (label sonucu bu etiketlerin ortalaması alınarak belirlenir)
            activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
            False ise tüm kare üzerinde çalışır.
        """

        if activate_iou:
            from .mask_detection_with_iou import MaskDetection
        else:
            from .mask_detection_without_iou import MaskDetection
        self.mask_detector= MaskDetection(model_path=model_path, device=device, mask_conf=mask_threshold,
                                          use_track_count=use_track_count, track_count=track_count)
        self.mask_info_logger = MaskInfoLogger()

    def process_frame(self, frame, person_detections=None):
        """
        Kişinin maske takma durmunu analiz ederek görüntü ve sonuç bilgisini dönderir.

        Args:
          frame (np.ndarray): BGR formatında görüntü.
          person_detections (list): Kişi tespit sonuçları.

        Returns:
            dict: Anlık görüntü analiz sonucunu dönderir.
        """

        results = self.mask_detector.detect(frame,person_detections)
        self.mask_info_logger.set_default()

        if results:
                self.mask_info_logger.set_detection_status(True)
                for r in results:
                    label = r['label']
                    track_id = r['track_id']
                    status=True if label=="mask" else False
                    self.mask_info_logger.add_detection(track_id, status)
        else:
            self.mask_info_logger.set_detection_status(False)
        
        return self.mask_info_logger.get_result()

#test
if __name__=="__main__":
    """Model ve video kaynağını ayarlayıp maske tespit işlemini başlatır."""

    from person_detect import PersonDetection
    import cv2
    model_path = "models/yolov11_mask.pt"
    source = "assets/test_video.mp4"

    mask = MaskProcessor(model_path=model_path,draw=True, threshold=0.45,track_count=20)
    person_detector = PersonDetection("models/yolo11n.pt",draw=False)
    cap = cv2.VideoCapture(source)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        person_res = person_detector.detect(frame)
        mask_result_info = mask.process_frame(frame,person_res)
        print(mask_result_info)
        
        cv2.imshow("Yolov11 - Maske Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()
