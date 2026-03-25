from ultralytics import YOLO
from .base_ppe_detection import BasePPEDetection

class BasePPEDetectionWithIOU(BasePPEDetection):
    """
    Kask / Yelek vb. ekipman tespitlerini RIO tekniği kullanarak tespiti için temel sınıf.
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
            person_detections (list): Kişi tespit sonuçları.

        Returns:
           list: Tespit edilen nesnelerin bilgilerini içeren sözlük listesi
                her sözlükte "box" (koordinatlar), "label" (etiket), ve "track_id" (takip ID'si) bulunur.
        """

        detections = []
        if not person_detections:
            return detections

        person_info = self._get_person_crop_info(frame, person_detections)

        ppe_results_for_persons = self.model.predict(source=person_info["crop_boxes"], verbose=False, conf=self.confidence)

        for ppe_results_for_person, original_person_box, track_id, cropped_person_shape in zip(
            ppe_results_for_persons,
            person_info["original_person_boxes"],
            person_info["person_id"],
            person_info["crop_shape"]
        ):
            if not ppe_results_for_person or len(ppe_results_for_person.boxes) == 0:
                continue

            detection_info = self._process_single_person(ppe_results_for_person, original_person_box, track_id, 
                                                      cropped_person_shape)
            detections.append(detection_info)

        if self.use_track_count:
            # aktif olmayayan kişi id'lerini sil.
            active_ids = [p["track_id"] for p in detections]
            self.cleanup_history(active_ids)

        return detections

    def _get_person_crop_info(self, frame, person_detections):
        """
        Kişinin crop edilmiş halini ve orijinal bilgilerini dönderir.
        """

        person_info={
            "person_id":[],
            "original_person_boxes":[],
            "crop_boxes":[],
            "crop_shape":[]
            
        }
        for person in person_detections:
            person_box = person.get("box")
            track_id = person.get("track_id")
            if not person_box:
                continue

            x1, y1, x2, y2 = map(int, person_box)
            person_crop = frame[y1:y2, x1:x2]

            person_info["crop_boxes"].append(person_crop)
            person_info["original_person_boxes"].append(person_box)
            person_info["person_id"].append(track_id)
            person_info["crop_shape"].append(person_crop.shape)

        return person_info
    
    def _process_single_person(self, ppe_results_for_person, person_box, track_id, cropped_person_shape):
        """
        Tespit edilen her kişi için model sonucunu işler, etiket belirler ve tracker günceller.

            Args:
                ppe_results_for_person: Kişi üzerinde tespit edilen ppe sonuçları
                track_id (int): Kişinin takip ID'si
                person_box (list): Kişiye ait orijinal bbox bilgisini tutar.
                cropped_person_shape (tuple): Kesilmiş kişi bbx'a ait h,w,c değerlerini tutar.
            
            Returns:
                dict: Kişi için tespit edilen ppe durumu bilgisi
        """

        ppe_detections = self._extract_detections(ppe_results_for_person)

        has_ppe = False
        for (ppe_box, conf, label) in ppe_detections:
            if self.is_target_region_overlap(ppe_box, cropped_person_shape):
                has_ppe = True
                break

        current_label = self.target_label if has_ppe else f"no{self.target_label}"

        if self.use_track_count:
            self.update_tracker(track_id, current_label)
            final_label = self.get_majority_label(track_id)

        else:
            final_label = current_label


        return {
            "box": person_box,
            "label": final_label,
            "track_id": track_id
        }
    