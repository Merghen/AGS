from .zone_manager import ZoneManager
from .inactivity_detect import InactivityDetector
from .zone_inactivity_log import ZoneInactivityInfoLogger
from .zone_selector import ZoneSelector
import time

class ZoneInactivityProcessor:
    """ 
    Alan ve hareketsizlik tespiti için görüntüyü işler 
    """

    def __init__(self,zone_manager=ZoneManager(), detect_inactivity=True, detect_zone=True,
                 movement_threshold=10, max_idle_time=0.2, cleanup_interval=300, cleanup_timeout=120):
        """
        Alan ve hareketsizlik tespiti için gerekli parametreleri ayarlar.

        Args:
            zone_manager (object): ZoneManager sınıfından oluşturulmuş nesne 
            detect_inactivity (bool): hareketsizlik tespitinin yapılıp yapılmayacağını tutar.
            detect_zone (bool): zone tespitinin yapılıp yapılmayacaığını tutar.
            movement_threshold (float): Hareketsizlik tespiti için Kişinin hareketli olarak nitelendirilmesi için piksel cinsinden değişim.
                                        Bu eşik değerinden az değişim olursa kişi hareketsiz kabul edilir.
            max_idle_time (float): Kişinin hareketsiz olarak nitelendirilmesi için gereken maksimum süre (saniye).
            cleanup_interval (float): Otomatik temizlik işlemi aralığı (saniye). Varsayılan 5dk.
            cleanup_timeout (float): Bu süreden(2 dakika) uzun süredir ekranda gözükmeyen kişilere ait bilgileri temizler. 
        """

        self.zone_manager=zone_manager if detect_zone else None
        input_zone_levels=[]

        if (detect_zone):
            if(not self.zone_manager.get_zones()):
                raise ValueError("Zone analizi için input alan bilgileri gerekli")
            input_zone_levels=self.zone_manager.get_input_zone_types()
            input_zone_levels=list(set(self.zone_manager.get_input_zone_types())) #tekrarlı girdileri dahil etmene gerek yok
            
        self.inactivity_manager=InactivityDetector(movement_threshold=movement_threshold, max_idle_time=max_idle_time
                                                   ) if detect_inactivity else None
        
        self.zone_inactivity_logger=ZoneInactivityInfoLogger(detect_inactivity=detect_inactivity,
                                                             detect_zone=detect_zone,
                                                             input_zone_levels=input_zone_levels)

        self.detect_inactivity=detect_inactivity
        self.detect_zone=detect_zone
        self.pass_times = {}  
        self.last_zones = {}   
        self.last_seen = {}  
        self.cleanup_interval = cleanup_interval
        self.cleanup_timeout = cleanup_timeout
        self.last_cleanup_time = time.time()

    def process_frame(self, person_detections):
        """
        Alan ve hareketsizlik durmunu analiz ederek sonuç bilgisini dönderir.

        Args:
            person_detections (list): Kişi tespit sonuçları.

        Returns:
            tuple (dict, ndarray): Anlık görüntü analiz sonucunu dönderir.
        """

        results = person_detections
        self.zone_inactivity_logger.set_default()

        if results:
                self.zone_inactivity_logger.set_detection_status(True)
                for r in results:
                    box = r['box']
                    track_id = r['track_id']

                    self.last_seen[track_id] = time.time()

                    self.zone_inactivity_logger.add_person_id_detection(track_id=track_id)

                    if self.detect_zone:
                        self._set_zone_danger_infos(track_id, box)
                    
                    if self.detect_inactivity:
                        self._set_inactivity_danger_infos(track_id,box)

        else:
            self.zone_inactivity_logger.set_detection_status(False)
        
        # belirli aralıklarla temizlik yap belleğin şişmesini önlemek için.
        if self._is_cleanup_time():
            self._cleanup_inactive_persons()
            self.last_cleanup_time = time.time()

        return self.zone_inactivity_logger.get_result()
        
    def _set_zone_danger_infos(self, track_id, box):
        """ Zone için analiz bilgilerini günceller """

        is_person_in_zone=self.zone_manager.is_person_in_any_zone(box)
        current_zone_info= self.zone_manager.get_zone_info_for_person(box)
        current_zone_name=current_zone_info["name"]
        current_zone_type=current_zone_info["type"]
        last_pass_time = self.pass_times.get(track_id, None)
        last_zone = self.last_zones.get(track_id, None)
        new_pass_time, passed_time = self.zone_manager.calculate_passed_time(
            last_pass_time, last_zone, current_zone_name
        )

        # Güncelle
        self.pass_times[track_id] = new_pass_time
        self.last_zones[track_id] = current_zone_name
        
        self.zone_inactivity_logger.add_zone_detection(current_zone_type, current_zone_name, passed_time, is_person_in_zone)

    def _set_inactivity_danger_infos(self, track_id, box):
        """ Hareketsizlik bilgilerini günceller"""

        self.inactivity_manager.update_position(track_id, box)
        inactivity_status = self.inactivity_manager.get_status(track_id)   
        inactivity_time = self.inactivity_manager.get_idle_time(track_id)
        self.zone_inactivity_logger.add_inactivity_detection(inactivity_status,inactivity_time)

    def _is_cleanup_time(self):
        status = True if time.time() - self.last_cleanup_time > self.cleanup_interval else False
        return status

    def _cleanup_inactive_persons(self):
            """ Uzun süredir ekranda görünmeyen kişilerin verilerini siler """

            current_time = time.time()
            to_delete = []
            for pid, last_seen_time in self.last_seen.items():
                if current_time - last_seen_time > self.cleanup_timeout:
                    to_delete.append(pid)

            for pid in to_delete:
                self.pass_times.pop(pid, None)
                self.last_zones.pop(pid, None)
                self.last_seen.pop(pid, None)

                if self.inactivity_manager:
                    self.inactivity_manager.person_states.pop(pid, None)
                print(f"{pid} id'li kişi {current_time:.2f} saniyede temizlendi (hareketsiz/görünmeyen).")


if __name__ == "__main__":
    """Model ve video kaynağını ayarlayıp yasak alan tespit işlemini başlatır."""
    import cv2

    model_path = "models/human_detect.pt"
    source = "assets/test.mp4"

    # ----------------------------------- manuel bölge seçimi -----------------------------------

    # zone_manager = ZoneManager()

    # zone_manager.add_zone([(350, 350), (600, 350), (800, 600),(150, 600)], "alan1 ", "red", line_color=(0,255,0))

    # zone_manager.add_zone([(720, 320), (900, 290), (1000, 480),(900, 550)], "alan2", "green", line_color=(0,0,255))


    # ----------------------------------- arayüz ile bölge seçimi -----------------------------------
    cap = cv2.VideoCapture(source)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Video okunamadı!")
    zone_manager = ZoneManager()
    selector = ZoneSelector(frame,zone_manager=zone_manager)
    selector.start_interface()
    print(zone_manager.get_input_zone_types())
    print(zone_manager.get_zones())

    # ----------------------------------- zone tespit işlemi -----------------------------------
    # zone_inactivity = ZoneInactivityProcessor(model_path=model_path,detect_inactivity=False,detect_zone=False,draw=True,
    #                                           person_threshold=0.4,
    #                                           max_idle_time=1,
    #                                           zone_manager=zone_manager
    #                                           )
    # cap = cv2.VideoCapture(source)
    
    # while cap.isOpened():
    #     ret, frame = cap.read()
    #     if not ret:
    #         break

    #     zone_inactivity_info = zone_inactivity.process_frame(frame)
    #     print(zone_inactivity_info)
        
    #     cv2.imshow("Bölge & Hareketsizlik Tespiti", frame)
    #     if cv2.waitKey(1) & 0xFF == 27: 
    #         break

    # cap.release()
    # cv2.destroyAllWindows()