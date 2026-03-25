class BaseInfoLogger:
    """Tüm logger sınıfları için ortak temel logger sınıfı."""

    def __init__(self, detection_type):
        self.frame_result = {
            "detection": detection_type,
            "detect": False,
            "detail": {}
        }

    def set_detection_status(self, status: bool):
        """Tespit durumunu günceller."""
        self.frame_result["detect"] = status

    def get_result(self):
        """Güncel tespit sonuçlarını döndürür."""
        return self.frame_result