from ..base_detection_info_logger import BaseInfoLogger

class ZoneInactivityInfoLogger (BaseInfoLogger):
    """ Her bir karedeki zone bilgilerini dönderir."""
   
    def __init__(self, detection_type="zone_inactivity",
                 detect_inactivity=True,
                 detect_zone=True,
                 input_zone_levels=[]):

        """ Anlık tespit bilgisini oluşturur ve sözlük olarak saklar.

        Args:
            detection_type (str, optional): Tespit edilen sınıf ismi.
            detect_inactivity (bool): Hareketsizlik tespiti yapılıp yapılmayacağı.
            detect_zone (bool): Zone tespiti yapılıp yapılmayacağı.
            input_zone_levels (list): Dışardan tanımlanan bölgelere ait hata seviyeleri.

        """
        super().__init__(detection_type)
        
        # Özel alanlar
        self.frame_result.update({
            "detect_inactivity": detect_inactivity,
            "detect_zone": detect_zone,
            "input_zone_levels": input_zone_levels,
        })

        # Detail alanı Zone’a ait özel yapı
        self.frame_result["detail"] = {
            "id": [],
            "zone_name": [],
            "zone_type": [],
            "passed_time": [],
            "is_person_in_zone": [],
            "is_person_moving": [],
            "person_idle_time": []
        }
    
    def set_default(self):
        """Frame için tespit bilgilerini sıfırlar."""

        self.frame_result["detect"] = False
        self.frame_result["detail"] ={
                "id": [],
                "zone_name": [],
                "zone_type": [],
                "passed_time": [],
                "is_person_in_zone": [],
                "is_person_moving": [],
                "person_idle_time": []
            }
 
    def add_person_id_detection(self,track_id):
        """ Kişiye ait ID bilgisini ekler
         
          Args:
            track_id (int): Kişinin takip ID'si
        """

        self.frame_result["detail"]["id"].append(track_id)

    def add_zone_detection(self, zone_type, zone_name, passed_time,is_person_in_zone):
        """ Tespit edilen zone bilgilerini tespit sözlüğüne ekler.

        Args:
            zone_type (str): Tespit edilen etiket ("green, red, yellow").
            zone_name (str): Kişinin bulunduğu zone adı.
            passed_time (float): Kişinin zone içinde geçirdiği süre.
            is_person_in_zone (bool): Kişinin zone içinde olup olmadığını belirtir.
            is_person_moving (bool/None): Kişinin hareketli olup olmadığını belirtir. 
            person_idle_time (float): Kişinin hareketsiz kaldığı süre (saniye).
        """

        self.frame_result["detail"]["zone_name"].append(zone_name)
        self.frame_result["detail"]["zone_type"].append(zone_type)
        self.frame_result["detail"]["passed_time"].append(passed_time)
        self.frame_result["detail"]["is_person_in_zone"].append(is_person_in_zone)
   

    def add_inactivity_detection(self, is_person_moving, person_idle_time):
        """ Hareketsizlik ile alakalı bilgileri tespit sözlüğüne ekler.

        Args:
            is_person_moving (bool/None): Kişinin hareketli olup olmadığını belirtir. 
            person_idle_time (float): Kişinin hareketsiz kaldığı süre (saniye).
        """
        
        self.frame_result["detail"]["is_person_moving"].append(is_person_moving)
        self.frame_result["detail"]["person_idle_time"].append(person_idle_time)
        

