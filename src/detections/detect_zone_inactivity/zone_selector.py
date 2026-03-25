import cv2
import numpy as np
from .zone_manager import ZoneManager


class ZoneSelector:
    
    """ Kullanıcının basit bir arayüz ile zone bilgilerini girmesini ve fare ile ilgili bölgeyi seçerek ZoneManager'a eklemesini sağlar. "
    "        Bu sınıf, genel yapı için gerekli olmayıp sadece dışardan daha kolay koordinat eklemek için oluşturulmuştur. """

    def __init__(self, frame, zone_manager, display_size=None):

        """ Zone işlemleri için başlangıç değişkenleri oluşturulur.
        
        Args:
            frame (np.array): Bölge seçimi için kullanılacak video karesi.
            zone_manager (ZoneManager): Bölge yönetimne atama için ZoneManager örneği.
        """
        self.frame=cv2.resize(frame, display_size) if display_size is not None else frame
        self.zone_manager = zone_manager
        self.points = []

    def mouse_callback(self, event, x, y, flags, param):

        """" Fare olaylarını yakalar ve nokta ekleme/silme işlemlerini yapar. Sol tık ekleme, sağ tık silme.
        
        Args:
            event: Fare olayı türü.
            x (int): Fare tıklama x koordinatı.
            y (int): Fare tıklama y koordinatı.
        """

        if event == cv2.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            print(f"Koordinat eklendi: {(x, y)}")

        elif event == cv2.EVENT_RBUTTONDOWN and self.points:
            removed = self.points.pop()
            print(f"Son nokta silindi: {removed}")

    def _get_input(self, prompt, input_type, default):

        """ Dışardan inputları alır ve doğrulama işlemi yapar. Hatalı girişte varsayılan değeri dönderir.

        Args:
            prompt (str): Kullanıcıya gösterilecek mesaj.
            input_type (str): Beklenen giriş türü ("color", "int", "float").
            default: Hatalı girişte döndürülecek varsayılan değer.

        Returns:
            girilen input_type değişkenine göre farklı türde değer dönderir.
                - "color": (B, G, R) tuple
                - "int": Pozitif tam sayı
                - "float": Pozitif ondalık sayı
        
        """

        while True:
            try:
                val = input(prompt)
                if not val.strip(): 
                    return default
                if input_type == "color":
                    c = tuple(map(int, val.split(",")))
                    if len(c) == 3 and all(0 <= x <= 255 for x in c):
                        return c
                elif input_type == "int":
                    num = int(val)
                    if num > 0:
                        return num
                elif input_type == "float":
                    num = float(val)
                    if num > 0:
                        return num
            except:
                pass
            print(f"Hatalı giriş! Varsayılan değer kullanılacak: {default}")
            return default    

    def ask_zone_details(self, index):

        """ Kullanıcıdan bölge ile ilgili bilgileri arayüz ilealır.
        
        Args:
            index (int): Kaçıncı bölge olduğu bilgisi.

        Returns:
            tuple: Bölge adı, tehlike seviyesi, çizgi rengi, yazı rengi, çizgi kalınlığı, yazı ölçeği.
        """

        zone_name = input(f"{index+1}. Bölge adı nedir? ")

        danger_map = {"1": "green", "2": "yellow", "3": "red"}
        danger_choice = input(f"{index+1}. Bölge etiketi (1=yeşil, 2=sarı, 3=kırmızı): ").strip()

        if danger_choice in danger_map:
            zone_danger = danger_map[danger_choice]
        else:
            zone_danger = "green"
            print("Geçersiz giriş! Varsayılan olarak 'green' (yeşil) etiketi atanmıştır.")



        detail = input(f"{index+1}. Bölge için detay eklemek ister misin? (y/n) ")
        if detail == "y":
            line_color = self._get_input("Çizgi rengi (örn: 255,0,0): ", "color", (255, 255, 0))
            text_color = self._get_input("Yazı rengi (örn: 255,255,255): ", "color", (255, 255, 255))
            thickness = self._get_input("Çizgi kalınlığı (örn: 2): ", "int", 2)
            scale = self._get_input("Yazı ölçeği (örn: 1): ", "float", 0.8)
        elif detail == "n":
            print("Varsayılan detaylar uygulandı.")
            line_color, text_color, thickness, scale = (255, 255, 0), (255, 255, 255), 2, 0.8
        else:
            print("Geçersiz giriş! Varsayılan olarak 'n' belirlenmiştir...")
            line_color, text_color, thickness, scale = (255, 255, 0), (255, 255, 255), 2, 0.8

        return zone_name, zone_danger, line_color, text_color, thickness, scale

    def select_zone(self, zone_name, zone_danger, line_color, text_color, thickness, scale):

        """ Kullanıcının fare ile bölgeyi seçer ve kaydeder.
        
        Args:
            zone_name (str): Bölge adı. 
            zone_danger (str): Bölge tehlike seviyesi (green, yellow, red).
            line_color (tuple): Çizgi rengi (B, G, R).
            text_color (tuple): Yazı rengi (B, G, R).
            thickness (int): Çizgi kalınlığı.
            scale (float): Yazı ölçeği.
        """

        self.points = []
        print(f"{zone_name} için alan seç (Sol tık=ekle, Sağ tık=geri al, ENTER=kaydet, ESC=iptal).")

        cv2.namedWindow("Select Zone")
        cv2.setMouseCallback("Select Zone", self.mouse_callback)

        while True:
            temp_frame = self.frame.copy()

            for z in self.zone_manager.get_zones():
                cv2.polylines(temp_frame, [np.array(z["coordinates"])], True, z["line_color"], z["thickness"])
                if z["coordinates"]:
                    x, y = z["coordinates"][0]
                    cv2.putText(temp_frame, z["name"], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
                                z["scale"], z["text_color"], z["thickness"])

            cv2.putText(temp_frame, f"Enter=Kaydet, Sag Tik=Geri al, Esc=Iptal",
                        (10, 30), cv2.FONT_HERSHEY_SIMPLEX, scale, text_color, thickness)

            for j, pt in enumerate(self.points):
                cv2.circle(temp_frame, pt, 5, (0, 0, 255), -1)
                if j > 0:
                    cv2.line(temp_frame, self.points[j - 1], pt, line_color, thickness)

            if len(self.points) > 2:
                cv2.polylines(temp_frame, [np.array(self.points)], True, line_color, thickness)

            cv2.imshow("Select Zone", temp_frame)
            key = cv2.waitKey(1)

            if key == 13 and len(self.points) > 2:  # Enter tuşu ve en az 3 nokta
                self.zone_manager.add_zone(self.points, zone_name, zone_danger,
                                           line_color=line_color, text_color=text_color,
                                           thickness=thickness, scale=scale)
                print(f"{zone_name} eklendi: {self.points}")
                break
            elif key == 27:  
                print("Seçim iptal edildi.")
                break

        cv2.destroyWindow("Select Zone")

    def start_interface(self):

        """
        Kullanıcıdan kaç bölge eklemek istediğini sorar ve her biri için detayları alır.
        Ardından fare ile bölge seçimi yapılmasını sağlar."""

        try:
            zone_count = int(input("Kaç bölge eklemek istiyorsun? "))
        except ValueError:
            print("Geçersiz sayı!")
            return

        for i in range(zone_count):
            zone_name, zone_danger, line_color, text_color, thickness, scale = self.ask_zone_details(i)
            
            self.select_zone(zone_name, zone_danger, line_color, text_color, thickness, scale)


