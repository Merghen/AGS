from .base_analyzers import BaseDangerAnalyzer, DangerInfo
import time

class InactivityDangerAnalyzer(BaseDangerAnalyzer):
    """ Hareketsizlik kaynaklı tehlike analizini yapan sınıf."""

    # Olası durumların tehlike seviyeleri ve nedenleri
    GREEN_VIOLATION = DangerInfo("Yeşil alanda hareketsizlik", "yellow")
    YELLOW_VIOLATION = DangerInfo("Sarı alanda hareketsizlik", "red")
    RED_VIOLATION = DangerInfo("Kırmızı alanda hareketsizlik", "red")
    OUTSIDE_VIOLATION = DangerInfo("Hareketsizlik", "yellow")

    def __init__(self,default_min_inactivity_time=3, min_inactivity_time_for_yellow=1, min_inactivity_time_for_red=4,
                 min_inactivity_time_for_green=2,inactivity_unseen_timeout=10):
        """
        Hareketsizlik tespiti için her bir alanda hareketsiz kalma sınır süresini belirler.

        Args:
            default_min_inactivity_time (float, optional): Alan dışındayken hareketsiz kalma süresi limiti(saniye). 
            min_inactivity_time_for_yellow (float, optional): Sarı alanda hareketsiz kalma süresi limiti(saniye). 
            min_inactivity_time_for_red (float, optional): Kırmızı alanda hareketsiz kalma süresi limiti(saniye). 
            min_inactivity_time_for_green (float, optional): Yeşil alanda hareketsiz kalma süresi limiti(saniye). 
            inactivity_unseen_timeout (float): hareketsiz olarak nitelendirilen kişi, bu süre boyunca(saniye)
                                               ekranda tespit edilemezse kişinin hareketsizlik durumu silinir. """
        
        self.default_limit = default_min_inactivity_time
        self.green_limit = min_inactivity_time_for_green
        self.yellow_limit = min_inactivity_time_for_yellow
        self.red_limit = min_inactivity_time_for_red

        # kişi bazlı state: {pid: {"violation": DangerInfo, "idle_time": float, "zone_type": str, "last_seen": float}}
        self.active_violations = {}
        self.disappear_timeout = inactivity_unseen_timeout

    def compute_danger(self, frame_result):
        """Hareketsizlik ihlallerini analiz eder.

        Args:
            frame_result (dict): O anki frame için tespit sonuçları.

        Returns:
            list: Tehlike durumlarını içeren liste.
        """

        detect_zone=frame_result["detect_zone"]
        zone_types = frame_result["detail"]["zone_type"]
        person_idle_times = frame_result["detail"]["person_idle_time"]
        current_ids = frame_result["detail"]["id"]
        now = time.time()

        if not detect_zone:
            # zone tespiti aktif olmadığı için her kişi alan dışında kabul edilir.
            zone_types = [None for _ in person_idle_times]
            
        for pid, zone_type, idle_time in zip(current_ids, zone_types, person_idle_times):
            violation = self._check_zone_inactivity(zone_type, idle_time)

            if pid in self.active_violations:
                self._update_violation_info(pid, idle_time, now)

            if violation:
                self.active_violations[pid] = {"violation": violation,
                                               "idle_time": idle_time,
                                               "zone_type": zone_type,
                                               "last_seen": now
                                               }

        self._cleanup_unseen_persons(now=now, current_ids=current_ids)
        
        levels,reasons=self._get_active_violation()

        return levels,reasons

    def _check_zone_inactivity(self, zone_type, idle_time):
        """Zone tipine göre ilgili kontrol fonksiyonunu çağırır.

        Args:
            zone_type (str or None): Kişinin bulunduğu alan türü. Alan dışındaysa None.
            idle_time (float): Kişinin hareketsiz kaldığı süre.

        Returns: DangerInfo or None: Eğer tehlike durumu varsa ilgili DangerInfo nesnesini döner, yoksa None döner.
        """

        if zone_type == "green":
            return self._check_green_inactivity(idle_time)
        elif zone_type == "yellow":
            return self._check_yellow_inactivity(idle_time)
        elif zone_type == "red":
            return self._check_red_inactivity(idle_time)
        elif zone_type is None:
            return self._check_outside_inactivity(idle_time)
        return None

    def _check_green_inactivity(self, idle_time):
        """Yeşil alanda hareketsizlik kontrolü yaparak Tehlike bilgisini(DangerInfo) döner."""

        return self._check_inactivity(idle_time, self.green_limit, self.GREEN_VIOLATION)

    def _check_yellow_inactivity(self, idle_time):
        """Sarı alanda hareketsizlik kontrolü yaparak Tehlike bilgisini(DangerInfo) döner"""

        return self._check_inactivity(idle_time, self.yellow_limit, self.YELLOW_VIOLATION)

    def _check_red_inactivity(self, idle_time):
        """Kırmızı alanda hareketsizlik kontrolü yaparak Tehlike bilgisini(DangerInfo) döner."""

        return self._check_inactivity(idle_time, self.red_limit, self.RED_VIOLATION)

    def _check_outside_inactivity(self, idle_time):
        """Alan dışında hareketsizlik kontrolü yaparak Tehlike bilgisini(DangerInfo) döner."""

        return self._check_inactivity(idle_time, self.default_limit, self.OUTSIDE_VIOLATION)
    
    def _check_inactivity(self, idle_time, limit, violation):
        """Genel hareketsizlik kontrol fonksiyonu.

        Args:
            idle_time (float): Kişinin hareketsiz kaldığı süre.
            limit (float): Hareketsizlik tespiti için eşik değer.
            violation (DangerInfo): İhlal bilgisi.

        Returns:
            DangerInfo or None: Eğer eşik aşılırsa ilgili DangerInfo nesnesi, aksi halde None.
        """
        return violation if idle_time >= limit else None
    
    def _update_violation_info(self, pid, idle_time, now):
        """
        Kişinin son görülme zamanını günceller ve eğer kişi hereket ettiyse kişiyi aktif tehlike listesinden siler.
        """
        
        self.active_violations[pid]["last_seen"] = now
        if self._is_person_moved(idle_time):
            del self.active_violations[pid]
    
    def _is_person_moved(self, idle_time):
        return  True if idle_time == 0 else False

    def _cleanup_unseen_persons(self, now, current_ids):
        """ Eğer kişi belirli bir sürenin üzerinde ekranda tespit edilmemişse ise o kişiye ait tehlike bilgisini siler.

                Args
                    now(timer): anlık zaman bilgisi
                    current_ids(list): anlık görüntüde tespit edilen kişilere ait id """
        
        to_delete = []
        for pid, info in self.active_violations.items():
            if pid not in current_ids:
                if now - info["last_seen"] > self.disappear_timeout:
                    to_delete.append(pid)

        for pid in to_delete:
            del self.active_violations[pid]
            print(f"{pid} ID'li kişi {self.disappear_timeout} saniye görüntüde görünmediği için aktiflik durumu silindi")

    def _get_active_violation(self):
        """
        Aktif ihlallerden tehlike seviyelerini ve nedenlerini toplar.

        Returns:
            tuple: (levels, reasons) listeleri """

        levels, reasons=[], []

        for pid, info in self.active_violations.items():
            v = info["violation"]
            levels.append(v.level)
            reasons.append(v.reason)

        return levels,reasons