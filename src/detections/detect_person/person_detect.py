from ultralytics import YOLO
import torch

class PersonDetection:
    """
    İnsan tespiti yapılan sınıf.
    """

    def __init__(self, model_path, device=None, person_threshold=0.4):
        """
        Modeli yükler
        
        Args:
            model_path (str): Eğitilmiş modelin dosya yolu.     
            device (str): Modelin çalışacağı cihaz(cpu,gpu) 
            person_threshold (float): insan tespiti için güven eşiği.
        """

        self.person_threshold=person_threshold
        device = device if device is not None else "cuda" if torch.cuda.is_available() else "cpu"
        self.model = YOLO(model_path)
        self.model.to(device)

    def set_track_id(self, box):
        """
        Her nesne için ID dönderir.

       Args:
           box: YOLO nesne kutusu

       Returns:
           int: Takip ID'si, yoksa -1
       """
        return int(box.id[0]) if box.id is not None else -1
    
    def detect(self, frame):
        """
        Bir görüntü karesi (frame) üzerinde tespit işlemi yapar.

        Args:
            frame (numpy.ndarray): Tespit yapılacak görüntü karesi

        Returns:
           tuple(dict, ndarray): Tespit edilen nesnelerin bilgilerini içeren sözlük listesi 
                her sözlükte "box" (koordinatlar), "label" (etiket), "confidence" (güven skoru) ve "track_id" (takip ID'si) bulunur.
        """

        results=self.model.track(source=frame, persist=True, stream=True, verbose=False, classes=[0],tracker="bytetrack.yaml")
        detections=self._extract_detections(results, self.person_threshold)

        return detections
        
    def _extract_detections(self, results, person_conf):

        """
        Model sonuçlarından geçerli tespitleri (detections) çıkarır.

        Args:
            results: Modelin tespit çıktıları (boxes, labels, vb. içeren sonuç nesneleri)
            person_conf (float): İnsan tespiti için minimum güven eşiği

         Returns:
            list[dict]: Her bir tespiti temsil eden sözlük listesi.
                Sözlük yapısı:
                {
                    "box": [x1, y1, x2, y2] veya None,
                    "label": str veya None,
                    "confidence": float veya None,
                    "track_id": int veya None
                }
        """
        detections = []
        if not results:
            return [{
                "box": None,
                "label": None,
                "confidence": None,
                "track_id": None
            }]

        for r in results:
            boxes = r.boxes
            names = r.names

            if boxes is not None and len(boxes) > 0:

                for box in boxes:
                    detection = self._create_detection(box, names, person_conf)
                    if detection:
                        detections.append(detection)

        return detections
    
    def _create_detection(self, box, names, person_conf):

        """ Tespit edilen kutu bilgisinden anlamlı bir tespit sözlüğü oluşturur.

        Args:
            box: YOLO nesne kutusu
            names: Modelin sınıf isimleri
            person_conf (float): İnsan tespiti için güven eşiği

        Returns:
            dict/None: Tespit edilen nesnenin bilgilerini içeren sözlük. Eğer nesne insan değilse veya güven skoru eşikten düşükse None döner.
        
        """
        cls_id = int(box.cls[0])
        label = names[cls_id]
        conf = float(box.conf[0])

        if label == "person" and conf < person_conf:
            return None

        x1, y1, x2, y2 = map(int, box.xyxy[0])
        track_id = self.set_track_id(box)

        return {
            "box": [x1, y1, x2, y2],
            "label": label,
            "confidence": conf,
            "track_id": track_id
        }
    
if __name__ == "__main__":

    import cv2
    
    model_path = "models/yolo11s.pt"
    source = "assets/glasses_test.mp4"

    person=PersonDetection(model_path)

    cap = cv2.VideoCapture(source)
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results=person.detect(frame,person_conf=0.4)
        
        if results:
            for r in results:
                    box = r['box']
                    label = r['label']
                    track_id = r['track_id']

                    x1, y1, x2, y2 = box
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255,0,0), 2)
                    cv2.putText(frame, f"person {track_id}", (x1, y1),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0), 2)
        
        cv2.imshow("Yolov11 - İnsan Tespiti", frame)
        if cv2.waitKey(1) & 0xFF == 27: 
            break

    cap.release()
    cv2.destroyAllWindows()