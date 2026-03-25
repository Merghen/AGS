from .base_analyzers import BaseDangerAnalyzer, DangerInfo

class ArkDangerAnalyzer(BaseDangerAnalyzer):
    """ Ark tespiti için tehlike analizini yapar."""

    # Ark tespit durumunun tehlike seviyesini belirler..
    ARC_VIOLATION = DangerInfo("Ark Tespiti", "red")

    def __init__(self):
        super().__init__(use_duration_check=False, danger_duration_threshold=3)

    def compute_danger(self,frame_result):
        """ Ark tespiti için tehlike analizini yapar

            Args:
                frame_result (dict): Bir karedeki tespit sonuçlarını içeren sözlük.
                
            Returns:
                tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""

        return self.simple_detect(violation=self.ARC_VIOLATION, frame_result=frame_result)
