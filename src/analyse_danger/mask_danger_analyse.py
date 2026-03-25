from .base_analyzers import BaseDangerAnalyzer, DangerInfo

class MaskDangerAnalyzer(BaseDangerAnalyzer):   
    """ Maske tespiti için tehlike analizi yapar. """

    MASK_VIOLATION = DangerInfo("Maske ihmali", "yellow")

    def __init__(self):
        super().__init__(use_duration_check=True, danger_duration_threshold=3)

    def compute_danger(self,frame_result):
       """ Maske tespiti için tehlike analizini yapar

            Args:
                frame_result (dict): Bir karedeki tespit sonuçlarını içeren sözlük.
                
            Returns:
                tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""
       
       return self.analyze_equipment_danger(violation=self.MASK_VIOLATION, frame_result=frame_result)