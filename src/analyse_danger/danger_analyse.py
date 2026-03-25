from .zone_inactivity_danger_analyse import ZoneInactivityDangerAnalyzer
from .vest_danger_analyse import VestDangerAnalyzer
from .mask_danger_analyse import MaskDangerAnalyzer  
from .helmet_danger_analyse import HelmetDangerAnalyzer
from .glasses_danger_analyse import GlassesDangerAnalyzer
from .fire_danger_analyse import FireDangerAnalyzer
from .smoke_danger_analyse import SmokeDangerAnalyzer
from .arc_danger_analyse import ArkDangerAnalyzer
from datetime import datetime

class DangerAnalyzerManager:
    """ Farklı tehlike analiz sınıflarını yöneten ve uygun olanı çağıran sınıf."""
    
    def __init__(self,
                 yellow_zone_limit=600,
                 inactivity_time_default=1500,
                 inactivity_time_for_green=1500,
                 inactivity_time_for_red=1200,
                 inactivity_time_for_yellow=600,
                 inactivity_unseen_timeout=60
                 ):
        """
        Args:
            yellow_zone_limit (float): Sarı alanda geçirilen sürenin tehlike oluşturması için gerekli süre limiti (saniye). 
            inactivity_time_default (float: Herhangi bir alanda değilken hareketsiz kalma süresi(saniye). 
            inactivity_time_for_yellow (float): Sarı alanda hareketsiz kalma süresi(saniye). 
            inactivity_time_for_red (float): Kırmızı alanda hareketsiz kalma süresi(saniye). 
            inactivity_time_for_green (float): Yeşil alanda hareketsiz kalma süresi(saniye).
            inactivity_unseen_timeout (float): hareketsiz olarak nitelendirilen kişi, bu süre boyunca(saniye)
                                               ekranda tespit edilemezse kişinin hareketsizlik tehlike bilgisi silinir."""

        self.analyzers = {
            "zone_inactivity": ZoneInactivityDangerAnalyzer(
                                                            yellow_zone_limit=yellow_zone_limit,
                                                            inactivity_time_default=inactivity_time_default,
                                                            inactivity_time_for_green=inactivity_time_for_green,
                                                            inactivity_time_for_red=inactivity_time_for_red,
                                                            inactivity_time_for_yellow=inactivity_time_for_yellow,
                                                            inactivity_unseen_timeout=inactivity_unseen_timeout
                                                            ),
            "vest": VestDangerAnalyzer(),
            "mask": MaskDangerAnalyzer(),
            "helmet": HelmetDangerAnalyzer(),
            "glasses": GlassesDangerAnalyzer(), 
            "fire": FireDangerAnalyzer(),
            "smoke": SmokeDangerAnalyzer(),
            "ark": ArkDangerAnalyzer()
        }
    
    def calculate_danger(self, analysis_results, selected_analyzers=None):
        """
        Analiz tespit sonuçlarını kullanarak tehlike durumunu hesaplar.
        
        Args:
            analysis_results (list): o anki frame için tespit edilmiş analiz sonuçları
            selected_analyzers (list): Analiz edilecek tespit türlerinin listesi. Varsayılan olarak tüm analizleri dahil eder
                        Mevcut analizler: zone_inactivity, vest, mask, helmet, glasses, fire, smoke, ark.
                        
        Returns:
            dict: Genel tehlike seviyesi, tehlike sayısı ve detayları içeren sözlük.
        """

        valid_analyzers = self._get_valid_analyzers(selected_analyzers)
        all_levels, all_reasons = self._collect_danger_data(analysis_results, valid_analyzers)
        
        overall_level = self._determine_overall_level(all_levels)
        amount_of_danger = self._determine_amount_of_danger(all_levels)
        
        return {
            'overall_danger_level': overall_level,
            'amount_of_danger': amount_of_danger,
            'time': datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
                'danger_level': all_levels,
                'danger_reason': all_reasons
            }
        
    def _get_valid_analyzers(self, selected_analyzers):
        """ 
            Geçerli analiz türlerini belirler.

            Args:
                selected_analyzers (list): Seçilen analizlerin listesi.

            Returns:
                list: Geçerli analizlerin listesi.
        """

        valid_analyzers = []

        if selected_analyzers is None:
            valid_analyzers = list(self.analyzers.keys())  # Tüm analiz türlerini seç
        
        else:
            for analyzer in selected_analyzers:
                if analyzer in self.analyzers:
                    valid_analyzers.append(analyzer)  
                else:
                    raise ValueError(f"Geçersiz analiz türü bulundu {analyzer} \n Seçilebilecek analiz türleri: zone_inactivity, vest, mask, helmet, glasses, fire, smoke, ark.")

        return valid_analyzers
    
    def _collect_danger_data(self, analysis_results, valid_analyzers):
        
        """ Tespit sonuçlarını işleyip tüm seviyeleri ve sebepleri toplar.

            Args:
                frame_result (list): Frame analiz sonuçları.
                valid_analyzers (list): Geçerli analiz türlerinin listesi.

            Returns:
                tuple: Tüm tehlike seviyeleri ve sebepleri içeren iki liste.
        """

        all_levels, all_reasons = [], []

        for detection in analysis_results:
            detection_type = detection.get('detection',"none")

            if detection_type not in valid_analyzers:
                continue # o anki tespit türü, seçili analizde mevcut değilse o tür için tehlike analizine gerek yok.
            
            levels, reasons = self._run_analysis(detection_type, detection)
            all_levels.extend(levels)
            all_reasons.extend(reasons)

        return all_levels, all_reasons
    
    def _run_analysis(self, detection_type, detection):
        """Doğrudan ilgili analyzer tespitini çağırır."""
    
        analyzer = self.analyzers.get(detection_type)
        return analyzer.compute_danger(detection)

    def _determine_overall_level(self, danger_levels):
        """ 
            Genel tehlike seviyesini belirler."""

        if "red" in danger_levels:
            return "red"
        elif "yellow" in danger_levels:
            return "yellow"
        else:
            return "green"
    
    def _determine_amount_of_danger(self, danger_levels):
        """ 
            Toplam tehlike miktarını belirler """

        amount=0
        for type in danger_levels:
            if type =="red" or type =="yellow":
                amount+=1

        return amount
         
# test
if __name__ == "__main__":
    from create_dummy_log import LogGenerator
    generator = LogGenerator()
    manager = DangerAnalyzerManager(inactivity_enabled=True,zone_enabled=True,)

    input_zone_types=["yellow","red","green"]
    res = generator.get_logs(selected_detection_types=['mask','glasses','vest'],inactivity_detect=True,zone_detect=True)
    result = manager.analyze_detections(res, input_zone_types=input_zone_types,selected_analyzers=['mask','glasses','vest'])
    print("Frame results:", res)
    print(result)
    

        
    