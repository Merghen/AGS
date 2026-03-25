from ..base_detection_info_logger import BaseInfoLogger

class BasePPEInfoLogger(BaseInfoLogger):
    """Tüm PPE logger sınıfları için ortak temel logger sınıfı."""

    def __init__(self, detection_type):

        super().__init__(detection_type)

    def set_default(self):
        """Görüntü analiz sonuçlarını varsayılana getirir."""

        self.frame_result["detect"] = False
        self.frame_result["detail"] = {"id":[],"status":[]}

    def add_detection(self, track_id, label):
        """ Tespit edilen nesnenin id ve etiket bilgisini anlık tespit sözlüğüne ekler.

        Args:
            track_id (int): Takip ID'si
            label (bool): Kişi ilgili ekipmanı takıyor veya takmıyor.
        """

        self.frame_result["detail"]["id"].append(track_id)
        self.frame_result["detail"]["status"].append(label)