import cv2
import numpy as np
import time

class ZoneManager:
    """
     Zone/bölge yönetiminin yapıldığı sınıf. Zone ekleme, kontrol ve süre hesaplama gibi işlemleri yapar."""
    
    def __init__(self):
        """ Zone bilgilerini tutan listeyi oluşturur.  """

        self.zones = []

    def add_zone(self, zone_coordinates, zone_name, zone_type, line_color=(0, 255, 0), text_color=(255, 255, 255),scale=1, thickness=2):

        """
        Yeni bir bölge ekler.  
        
        Args:
            zone_coordinates (list): Bölgenin köşe koordinatları (saat yönünde sıralanmaktadır.(sol üst, sağ üst, sağ alt, sol alt)).
            zone_name (str): Bölge adı.
            zone_type (str): Bölge tipi (örneğin: "green", "red", "yellow").
            line_color (tuple): Bölge çizgi rengi (BGR formatında). 
            text_color (tuple): Bölge metin rengi (BGR formatında).
            scale (float): Bölge metin ölçeği.
            thickness (int): Bölge çizgi kalınlığı.
        """

        self.zones.append({
            'coordinates': zone_coordinates,
            'name': zone_name,
            'type': zone_type,
            "line_color": line_color,  
            "text_color": text_color,  
            "scale": scale,
            "thickness": thickness
        })

    def get_zones(self):

        """
        Bölgeye ait tüm bilgileri dönderir. 
         
        Returns:
            list: Bölge bilgilerini içeren liste."""
        
        return self.zones
    
    def _find_zone_info_for_person(self, person_box):

        """
        Tesbit edilen kişinin hangi bölgede olduğunu belirler ve o bölgenin bilgilerini dönderen private fonksiyon.
        
        Args:
            person_box (tuple): Kişinin bounding box'u (x1, y1, x2, y2).

        Returns:
            dict: Kişinin bulunduğu bölge bilgilerini içeren sözlük. Eğer kişi hiçbir bölgede değilse None döner.
        """

        x1, y1, x2, y2 = person_box
        foot_point = ((x1 + x2) // 2, y2)

        for zone in self.zones:
            zone_coordinates = np.array(zone['coordinates'], np.int32)
            if cv2.pointPolygonTest(zone_coordinates, foot_point, False) >= 0:
                return zone
        return {"name": None, "type": None, "coordinates": None, "line_color": None, "text_color": None, "scale": None, "thickness": None}
    
    def is_person_in_any_zone(self, person_box):

        """Kişinin herhangi bir alanın içerisinde olup olmadığını kontrol eder.
        
        Args:
            person_box (tuple): Kişinin bounding box'u (x1, y1, x2, y2).

        Returns:
            bool: Kişi herhangi bir bölgede ise True, değilse False.
        """
        zone = self._find_zone_info_for_person(person_box)
        return zone["name"] is not None


    def is_person_in_specific_zone(self, person_box, spesific_zone):

        """Kişinin belirtilen alanda olup olmadığını kontrol eder.
        
        Args:
            person_box (tuple): Kişinin bounding box'u (x1, y1, x2, y2).
            spesific_zone (str): Kontrol edilecek bölge adı ("green", "red", "yellow").

        Returns:
            bool: Kişi belirtilen bölgede ise True, değilse False.
        """
        zone = self._find_zone_info_for_person(person_box)
        match spesific_zone.lower():
            case "green":
                return zone["type"] == "green"
            case "red":
                return zone["type"] == "red"
            case "yellow":
                return zone["type"] == "yellow"
            case _:
                return False

    def get_zone_info_for_person(self, person_box):

        """
        Kişinin bulunduğu bölgenin bilgilerini döner.
        
        Args: Kişinin bounding box'u (x1, y1, x2, y2).
        
        Returns:
            dict: Kişinin bulunduğu bölge bilgilerini içeren sözlük. """

        return self._find_zone_info_for_person(person_box)
    
    def calculate_passed_time(self, pass_time, last_zone, current_zone=None):

        """
        Kişinin zone içinde geçirdiği süreyi hesaplar.
        - Zone dışına çıkarsa süre sıfırlanır.
        - Zone değişirse süre sıfırlanır.
        - Aynı zone’da kalıyorsa süre artar.
        
        Args:
            pass_time (float): Son giriş zamanını tutar, None ise yeni başlatılır.
            person_box (tuple): Kişinin lokasyon bilgileri
            last_zone (str/None): Son zone adı. Zone değişimini kontrol eder.
            
        Returns:
            (pass_time, passed_time)
        """
        if current_zone is None:
            return None, None

        
        if pass_time is None or current_zone != last_zone:
            return time.time(), 0

        
        passed_time = round(time.time() - pass_time, 2)
        return pass_time, passed_time   
    
    def get_input_zone_types(self):
        
        zone_type_infos=[]
        zone_infos=self.get_zones()

        for zone_info in zone_infos:
            zone_type=zone_info["type"]
            zone_type_infos.append(zone_type) 
        
        return zone_type_infos




