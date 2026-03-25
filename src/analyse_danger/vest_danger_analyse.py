from .base_analyzers import BaseDangerAnalyzer, DangerInfo   

class VestDangerAnalyzer(BaseDangerAnalyzer):   
    """ Yelek tespiti için tehlike analizi yapar. """

    VEST_VIOLATION = DangerInfo("Yelek ihmali", "yellow")

    def __init__(self):
        super().__init__(use_duration_check=True, danger_duration_threshold=3)

    def compute_danger(self,frame_result):
       """ Yelek tespiti için tehlike analizini yapar

            Args:
                frame_result (dict): Bir karedeki tespit sonuçlarını içeren sözlük.
                
            Returns:
                tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""
       
       return self.analyze_equipment_danger(violation=self.VEST_VIOLATION, frame_result=frame_result)