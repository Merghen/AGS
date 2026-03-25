from ultralytics import YOLO
from .base_ppe_detection import BasePPEDetection

class BasePPEDetectionWithoutIOU(BasePPEDetection):
    """
    Kask / Yelek vb. ekipman tespitleri için temel sınıf.
    Diğer PPE sınıfları bu sınıftan miras alır.
    """

    def __init__(self, model_path, target_label, device=None, confidence=0.5, use_track_count=True, track_count=5):
        """
        Args:
            model_path (str): Eğitilmiş modelin yolu
            target_label (str): Modelde kontrol edilecek etiket (helmet, vest, glasses, mask vb.)
            device (str): CPU veya GPU
            confidence (float): Minimum güven eşiği
            use_track_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez
            track_count (int): Stabil sonuç için geçmiş etiket sayısı

        """
        super().__init__(model_path, target_label=target_label, device=device, confidence=confidence, 
                         use_track_count=use_track_count, track_count=track_count)

    def detect(self, frame, person_detections=None):
        """
        Bir görüntü karesi (frame) üzerinde tespit işlemi yapar.

        Args:
            frame (numpy.ndarray): Tespit yapılacak görüntü karesi
            person_detections (list): Kişi tespit sonuçları listesi.

        Returns:
           list: Tespit edilen nesnelerin bilgilerini içeren sözlük listesi
                her sözlükte "box" (koordinatlar), "label" (etiket) ve "track_id" (takip ID'si) bulunur.
        """
        
        if not person_detections:
            return []

        results = self.model.predict(source=frame, verbose=False)
        detections = []

        if all(len(r.boxes) == 0 for r in results):
            return detections

        ppe_boxes = self._extract_detections(results)

        for person in person_detections:
            person_box = person["box"]
            track_id = person["track_id"]

            has_ppe = self.person_has_ppe(person_box, ppe_boxes)
            label = self.target_label if has_ppe else f"no{self.target_label}"

            if self.use_track_count:
                self.update_tracker(track_id, label)
                final_label = self.get_majority_label(track_id)
            else:
                final_label = label

            detections.append({
                "box": person_box,
                "label": final_label,
                "track_id": track_id
            })

        if self.use_track_count:
            # aktif olmayayan kişi id'lerini sil.
            active_ids = [p["track_id"] for p in detections]
            self.cleanup_history(active_ids)
            
        return detections

    def person_has_ppe(self, person_box, ppe_boxes):
        """Kişinin ilgili ekimanı giyip giymediğini kontrol eder."""

        for ppe_box, _, label in ppe_boxes:
            if label==self.target_label and self.is_target_region_overlap(ppe_box, person_box):
                return True
        return False


