from ultralytics import YOLO
import torch

class BasePPEDetection:
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
        self.model = YOLO(model_path)
        device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(device)

        self.target_label = target_label
        self.use_track_count=use_track_count
        self.history = {}
        self.confidence = confidence
        self.track_count = track_count

    def _extract_detections(self, results):
        """
        Model sonucunda elde edilen bilgileri ayıklar. 
        
        Args:
            results (list): YOLO modelden dönen tespit sonuçlar listesi.

        Returns:
            list: Ekipmana ait bilgileri içeren liste
        """

        ppe_boxes = []

        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                label = r.names[cls_id]
                conf = float(box.conf[0])
                if label == self.target_label:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    ppe_boxes.append(([x1, y1, x2, y2], conf, label))

        return ppe_boxes


    def update_tracker(self, track_id, label):
        """
        Verilen track_id'ye ait geçmiş etiket listesini günceller.

        Args:
            track_id (int): Takip ID'si
            label (str): Mevcut etiket 

        Returns:
            dict: Güncellenmiş history sözlüğü 
        """
        # eğer track id history içinde yoksa boş liste ekler daha sonra o track'id nin tuttuğu listeye label' etiketini ekler.
        # böylece her track_id için ayrı bir etiket geçmişi tutulur.
        if track_id not in self.history:
            self.history[track_id] = []
        self.history[track_id].append(label)

        # history sözlüğümde aynı id'ye sahip sadece x adet güncel veriyi tutacağım..
        # daha stable sonuçlar verebilmesi için..
        if len(self.history[track_id]) > self.track_count:
            self.history[track_id] = self.history[track_id][-self.track_count:]
        
        return self.history
        
    def get_majority_label(self, track_id):
        """
        Belirli bir takip ID'si için listeden en sık görülen etiketi döndürür. böylece kısa süreli yanlış
        tespitlerini optimize eder.

        Args:
            track_id (int): Takip ID'si

        Returns:
            str: İlgili ekipmanın çıktı label'i  (vest - novest gibi)
        """
        
        if self.history[track_id]:  

            labels = self.history[track_id]              # Etiketler listesi
            unique_labels = set(labels)                  # Aynı olanları bir kere al
            most_common = max(unique_labels, key=labels.count)  # En sık olanı bul
            return most_common 
        
        return None
    
    def cleanup_history(self, active_track_ids):
        """O anda aktif olmayan track_id'leri history'den sil."""
        
        to_delete = [tid for tid in self.history if tid not in active_track_ids]
        for tid in to_delete:
            del self.history[tid]
    
    def is_target_region_overlap(self, ppe_box, person_box):
        """
        Kişinin ilgili ekipmanı giyip giymediğini kontrol eder.
        """
        raise NotImplementedError("Bu fonksiyon alt sınıfta tanımlanmalıdır.")

