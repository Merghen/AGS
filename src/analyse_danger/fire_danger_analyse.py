from .base_analyzers import BaseDangerAnalyzer, DangerInfo

class FireDangerAnalyzer(BaseDangerAnalyzer):
    """ Ateş tespiti için tehlike analizini yapar."""

    # Ateş tespit durumunun tehlike seviyesini belirler..
    FIRE_VIOLATION = DangerInfo("Ateş Tespiti", "red")

    def __init__(self):
        super().__init__(use_duration_check=True, danger_duration_threshold=4)

    def compute_danger(self,frame_result):
        """ Ateş tespiti için tehlike analizini yapar

            Args:
                frame_result (dict): Bir karedeki tespit sonuçlarını içeren sözlük.
                
            Returns:
                tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""

        return self.simple_detect(violation=self.FIRE_VIOLATION, frame_result=frame_result)
    
   