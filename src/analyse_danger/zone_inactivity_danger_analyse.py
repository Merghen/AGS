from .base_analyzers import BaseDangerAnalyzer
from .inactivity_danger_analyse import InactivityDangerAnalyzer
from .zone_danger_analyse import ZoneDangerAnalyzer

class ZoneInactivityDangerAnalyzer(BaseDangerAnalyzer):
    """Hem alan (zone) hem de hareketsizlik (inactivity) tehlikelerini birlikte yöneten sınıf."""

    def __init__(self,
                 yellow_zone_limit=5,
                 inactivity_time_default=3,
                 inactivity_time_for_green=1,
                 inactivity_time_for_red=4,
                 inactivity_time_for_yellow=2,
                 inactivity_unseen_timeout=5):
        """
        Args:
            yellow_zone_limit (float): Zone tehlike tespiti için sarı alanda kalma süresi(saniye).
            inactivity_time_default (float: Herhangi bir alanda değilken hareketsiz kalma süresi(saniye). 
            inactivity_time_for_yellow (float): Sarı alanda hareketsiz kalma süresi(saniye). 
            inactivity_time_for_red (float): Kırmızı alanda hareketsiz kalma süresi(saniye). 
            inactivity_time_for_green (float): Yeşil alanda hareketsiz kalma süresi(saniye). 
            inactivity_unseen_timeout (float): hareketsiz olarak nitelendirilen kişi, bu süre boyunca(saniye)
                                               ekranda tespit edilemezse kişinin hareketsizlik tehlike bilgisi silinir.""" 
        
        super().__init__(use_duration_check=False)
        
        self.zone_analyzer = ZoneDangerAnalyzer(yellow_zone_limit) 
        self.inactivity_analyzer = InactivityDangerAnalyzer(default_min_inactivity_time=inactivity_time_default,
                                                            min_inactivity_time_for_green=inactivity_time_for_green,
                                                            min_inactivity_time_for_red=inactivity_time_for_red,
                                                            min_inactivity_time_for_yellow=inactivity_time_for_yellow,
                                                            inactivity_unseen_timeout=inactivity_unseen_timeout) 


    def compute_danger(self, frame_result):
        """" Zone ve/veya hareketsizlik analizini yapar 
        Args:
            frame_result (dict): o anki frame için tespit sonuçları 
        
        Returns:    
            tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""

        levels, reasons = [], []
        
        zone_enabled=frame_result['detect_zone']
        inactivity_enabled=frame_result['detect_inactivity']

        if (zone_enabled != []):
            z_levels, z_reasons = self.zone_analyzer.compute_danger(frame_result)
            levels.extend(z_levels)
            reasons.extend(z_reasons)

        if (inactivity_enabled != []):
            i_levels, i_reasons = self.inactivity_analyzer.compute_danger(frame_result)
            levels.extend(i_levels)
            reasons.extend(i_reasons)

        return levels, reasons