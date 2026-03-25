from .base_analyzers import BaseDangerAnalyzer, DangerInfo
import time 
class ZoneDangerAnalyzer(BaseDangerAnalyzer):
    """ Alan bazlı tehlike analizi yapan sınıf."""

    # Olası durumların tehlike seviyeleri ve nedenleri
    GREEN_VIOLATION = DangerInfo("Yeşil alan ihlali", "yellow")
    YELLOW_VIOLATION = DangerInfo("Sarı alan ihlali", "red")
    RED_VIOLATION = DangerInfo("Kırmızı alan ihlali", "red")
    
    def __init__(self, yellow_zone_limit=2):
        """ Bölge tespiti için gerekli parametreyi sağlar.

            Args:  
                yellow_zone_limit (float, optional): Sarı alanda kalma süresi limiti(sarı alanda bu süreyi aşarsa tehlike oluşur).
                danger_duration_threshold (int/float): Tehlike durumunun devam etmesi gereken süre (saniye).
        """

        self.yellow_zone_limit = yellow_zone_limit

        super().__init__(use_duration_check=True, danger_duration_threshold=2, unseen_timeout=1)

    def compute_danger(self, frame_result):

        input_zone_types = frame_result["input_zone_levels"]
        zone_types = frame_result["detail"]["zone_type"]
        persons_in_zone = frame_result["detail"]["is_person_in_zone"]
        passed_time = frame_result["detail"]["passed_time"]
        ids = frame_result["detail"]["id"]
        detection_name = frame_result.get("detection", "Null")
        current_ids = []

        levels, reasons = [], []
        for pid, z_type, in_zone, time_spent in zip(ids, zone_types, persons_in_zone, passed_time):
            person_id = f"{detection_name}_{pid}"
            current_ids.append(person_id)

            violation = self._analyze_violation(z_type, in_zone, time_spent,
                                                self.yellow_zone_limit, input_zone_types)
            danger_state = True if violation is not None else False
            if violation is not None and self._update_and_confirm_danger_state(person_id, danger_state, violation):
                levels.append(violation.level)
                reasons.append(violation.reason)
                
        self._handle_unseen_persons(current_ids, levels, reasons)

        return levels, reasons
    
    def _analyze_violation(self, z_type, in_zone, time_spent, limit, input_zone_types):
        """
             Her bir kişi için tehlike ihmal durumunu analiz eder.
            
             Args:
                z_type (string): Kişinin bulunduğu alan türünü belirtir(yellow,green,red,None).
                in_zone (bool): Kişinin alan içinde olup olmadığını belirtir.
                time_spent (float): Kişinin alan içinde geçirdiği süreyi içerir.
                limit (float): Sarı alanda kalma süresi limiti. 
                input_zone_types (list): Input olarak girilen zone seviyelerini tutar.

            returns:
                DangerInfo veya None: Eğer tehlike durumu varsa ilgili DangerInfo nesnesini döner, yoksa None döner.
        
        """
        
        if self._check_red_zone(z_type):
            return self.RED_VIOLATION
        elif self._check_yellow_zone(z_type, time_spent, limit):
            return self.YELLOW_VIOLATION
        elif self._check_green_zone(input_zone_types, in_zone):
            return self.GREEN_VIOLATION
        return None

    def _check_green_zone(self,input_zone_types, person_in_zone):
        """ Yeşil alan için tehlike kontrolü yapar. 
        
        Args:
            input_zone_types (list): Input olarak girilen zone seviyelerini tutar
            person_in_zone (bool): Kişinin alan içinde olup olmadığını belirtir.
            
        Returns:
            bool: Eğer input verisinde yeşil alan varsa ve kişi herhangi bir alanda değilse True, aksi halde False."""

        # Input zonelar arasında yeşil alan var mı kontrol et
        has_green_zone= True if "green" in input_zone_types else False

        # Yeşil alan varsa ve herhangi bir kişi alanda değilse tehlike var
        if has_green_zone and not person_in_zone:
            return True
        return False

    def _check_red_zone(self,zone_type):
        """ Kırmızı alan için tehlike kontrolü yapar."""
        
        return zone_type == "red"

    def _check_yellow_zone(self, zone_type, time_spent, limit):
        """ Sarı alan için tehlike kontrolü yapar."""
        
        return zone_type == "yellow" and time_spent > limit
    
