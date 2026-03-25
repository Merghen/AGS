import time
from dataclasses import dataclass

@dataclass
class DangerInfo:
    """ Tehlike durumlarının sebeplerini ve seviyelerini tutan veri sınıfı."""
    reason: str  
    level: str   # 'red','yellow' (green tehlike durumu yok anlamında kullanıldığı için kullanılmıyor)

class BaseDangerAnalyzer:
    """
    Tüm tehlike analiz sınıfları için temel arayüz (interface) sınıfıdır."""

    def __init__(self, use_duration_check=False, danger_duration_threshold=2, unseen_timeout=3):
        """
        Tehlike analizinde süre bazlı kontrolün kullanılıp kullanılmayacağını ve
        bu sürenin ne kadar olacağını ayarlar.

        Args:
            use_duration_check (bool): Tehlike durumunun süre bazlı kontrol edilip edilmeyeceği.
            danger_duration_threshold (int/float): Tehlike durumunun devam etmesi gereken süre (saniye).
            unseen_timeout (int/float): Kişinin gerçekten tespit edilmeme durumunu belirlemek için gerekli süre (saniye).
                                        Kişinin geçmiş tespit bilgisi bu süre boyunca devam eder."""

        self.use_duration_check = use_duration_check
        self.threshold = danger_duration_threshold
        self.person_danger_memory = {}  
        self.single_danger_memory = {}
        self.unseen_timeout=unseen_timeout

    def compute_danger(self, frame_result, **kwargs):
        raise NotImplementedError("Her analyzer kendi compute_danger metodunu yazmalı.")

    def simple_detect(self, violation, frame_result):
        """ Basit tespit tabanlı tehlike analizini yapar.

            Args:
                violation (DangerInfo): Tehlike sebebi ve seviyesi bilgisi.
                frame_result (dict): Bir karedeki tespit sonuçlarını içeren sözlük.
    
            Returns:
                tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""
        
        levels, reasons = [], []
        is_detected = frame_result.get("detect", False)
        detection_name = frame_result.get("detection", "Null")

        danger_state = self._update_and_confirm_danger_state(detection_name, is_detected, violation)

        if danger_state:
            levels.append(violation.level)
            reasons.append(violation.reason)

        return levels, reasons

    def analyze_equipment_danger(self, violation, frame_result):
        """ Ekipman (maske, yelek vb.) tespit tabanlı tehlike analizini yapar.

            Args:
                violation (DangerInfo): Tehlike sebebi ve seviyesi bilgisi.
                frame_result (dict): Bir karedeki tespit sonuçlarını içeren sözlük.
            
            Returns:
                tuple: Tehlike seviyesi ve nedeni içeren iki elemanlı bir liste."""

        levels, reasons = [], []
        details = frame_result["detail"]
        detection_name = frame_result.get("detection", "Null")

        ids = details.get("id", [])
        status_list = details.get("status", [])

        current_ids = []
        for person_id, is_wearing in zip(ids, status_list):
            object_id = f"{detection_name}_{person_id}"
            current_ids.append(object_id)

            danger_state = None if is_wearing is None else (not is_wearing)
            danger_state = self._update_and_confirm_danger_state(object_id, danger_state, violation)

            if danger_state:
                levels.append(violation.level)
                reasons.append(violation.reason)

        self._handle_unseen_persons(current_ids, levels, reasons)
        return levels, reasons

    def _update_and_confirm_danger_state(self, object_id, is_danger_now, violation):
        """
        Tehlike durumunun belirli süre boyunca devam edip etmediğini kontrol eder ve tehlike bilgisini günceller.
        
        Args:
            object_id (str/int): Kişiyeye ait tehlike durumu
            is_danger_now (bool): Bu karede tehlike var mı? (True/False)
            violation (DangerInfo): Tehlikeye ait bilgiyi tutar.
        
        Returns:
            bool: Kesinleşmiş tehlike durumunu kontrol eder.
        """

        if not self.use_duration_check:
            return is_danger_now

        current_time = time.time()

        person_state = self.person_danger_memory.get(
            object_id,
            {"is_danger_confirmed": False, "danger_start_time": None,"danger_finish_time": None,
              "last_violation": None, "last_seen":None
            }
        )

        if violation is not None:
            person_state["last_violation"] = violation
        
        person_state["last_seen"] = current_time
        if is_danger_now:
            # Daha önce başlatılmış tehlike yok süreci varsa, bu artık geçersizdir. Sistem yanlışlıkla tehlike yok döndermemesi için. 
            if person_state["danger_finish_time"] is not None:
                person_state["danger_finish_time"] = None

            if not person_state["is_danger_confirmed"]:
                # tehlike balangıç süresini başlatır eğer daha önce başlatılmamışsa
                if person_state["danger_start_time"] is None:
                    person_state["danger_start_time"] = current_time
                # Tehlike kesinleşti mi
                elif current_time - person_state["danger_start_time"] >= self.threshold:
                    person_state["is_danger_confirmed"] = True

        else:
            if person_state["is_danger_confirmed"]:
                # Tehlike bitiş süresini başlatır eğer daha önce başlatılmamışsa
                if person_state["danger_finish_time"] is None:
                    person_state["danger_finish_time"] = current_time
                # Tehlike gerçekten sonlandı mı
                elif current_time - person_state["danger_finish_time"] >= self.threshold:
                    person_state["is_danger_confirmed"]=False
                    person_state["danger_start_time"] = None
                    person_state["danger_finish_time"] = None
                    person_state["last_violation"] = None
            else:
                person_state["is_danger_confirmed"]=False

        self.person_danger_memory[object_id] = person_state
        return person_state["is_danger_confirmed"]
    
    def _handle_unseen_persons(self, current_ids, levels, reasons):
        """
        Kadrajdan çıkmış kişileri kontrol eder. Eğer kişi son framede tehlike aktifse, unseen_timeout süresi boyunca
        son tehlike bilgisini döner ve eğer kişi unseen_timeout süresi boyunca ekranda gözükmüyorsa kişiye ait kaydı siler.

        Args:
            current_ids (list): Bu framede görülen kişi kimlikleri
            levels (list): Tehlike seviyeleri listesi
            reasons (list): Tehlike nedenleri listesi
        """

        for object_id in list(self.person_danger_memory.keys()):
            if object_id not in current_ids:
                person_state = self.person_danger_memory.get(object_id)

                if person_state and person_state.get("is_danger_confirmed"):
                    last_violation = person_state.get("last_violation")

                    if last_violation is not None:
                        levels.append(last_violation.level)
                        reasons.append(last_violation.reason)

                if self._did_person_really_not_detected(object_id):
                    del self.person_danger_memory[object_id]

    def _did_person_really_not_detected(self, object_id):
        """
        Kişinin tespit edilmeme durumunu belirli süre boyunca kontrol ederek kişinin gerçekten tespit edilip edilmediğine karar
        verir.
        
        Args:
            object_id (str/int): Kişi veya nesne için benzersiz kimlik
        
        Returns:
            bool: Kesinleşmiş tehlike durumunu kontrol eder.
        """
        current_time = time.time()

        person_state = self.person_danger_memory.get(
            object_id,
            {"is_danger_confirmed": False, "danger_start_time": None,"danger_finish_time": None, "last_violation": None,
             "last_seen": None}
        )
            
        if person_state.get("last_seen") is None:
            person_state["last_seen"] = current_time

        if current_time - person_state["last_seen"] >= self.unseen_timeout:
            return True
            
        return False
    
        


        