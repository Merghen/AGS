from ultralytics import YOLO
import torch
from concurrent.futures import ThreadPoolExecutor, as_completed

class DetectionManager:
    """
    DetectionManager, farklı tespit türlerini (insan, gözlük, kask, maske, ateş, duman, ark, zone ve hareketsizlik)
    aktif hale getirir ve görüntü karesi üzerinde analiz yaparak tespit sonuçlarını döner.

    Kullanımı:
        1. activate_* metotları ile ihtiyaç duyulan tespit türlerini aktif et.
        2. get_person_detection() ile kişi tespit sonuçlarını al (opsiyonel). 
            (Sadece kişi tespitlerinin görselleştirilmesinde kullanılır.)
        3. analyze(frame) aktif edilen tespit türlerini analiz et."""
        
    def __init__(self):

        self.person = None 
        self.vest = None 
        self.helmet = None 
        self.mask = None
        self.glasses = None
        self.fire = None
        self.smoke = None
        self.arc = None
        self.zone_inactivity = None 
        self.fire_smoke = None
        self.detections = {
            "person": None,
            "vest": None,
            "helmet": None,
            "mask": None,
            "glasses": None,
            "fire": None,
            "smoke": None,
            "arc": None,
            "zone_inactivity": None
        }

    def activate_person(self, device=None, person_threshold=0.4):
        """ İnsan tespitini aktif hale getirir.

            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                person_threshold (float): Kişi tespiti için güven eşiği."""
                
        from src.detections.detect_person.person_detect import PersonDetection
        model_path="models/yolov11_person.pt"

        self.person = PersonDetection(model_path=model_path, device=device, person_threshold=person_threshold)
        print("İnsan tespit modeli başarı ile aktif edildi.")

    def activate_vest(self, device=None, vest_threshold=0.4, use_history_count=True, history_count=5, activate_iou=True):
        """ Yelek tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                vest_threshold (float): Yelek tespitinde minimum güven skoru.
                use_history_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez 
                history_count (int): Her kişinin label tespiti için ortalaması alınacak geçmiş frame miktarı
                               (O anki label sonucu, belirlenen geçmiş x adet frame sonuçlarnının ortalaması alınarak belirlenir)"""
        
        from src.detections.detect_ppe.detect_vest.vest_processor import VestProcessor
        model_path="models/yolov11_vest.pt"

        self.vest = VestProcessor(model_path, vest_threshold=vest_threshold, device=device, use_track_count=use_history_count,
                                   track_count=history_count, activate_iou=activate_iou)
        print("Yelek tespit modeli başarı ile aktif edildi.")

    def activate_helmet(self, device=None, helmet_threshold=0.7, use_history_count=True, history_count=10, activate_iou=True):
        """ Kask tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                helmet_threshold (float): Kask tespitinde minimum güven skoru.
                use_history_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez 
                history_count (int): Her kişinin label tespiti için ortalaması alınacak geçmiş frame miktarı
                               (O anki label sonucu, belirlenen geçmiş x adet frame sonuçlarnının ortalaması alınarak belirlenir)
                activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
                                     False ise tüm kare üzerinde çalışır. """
        
        from src.detections.detect_ppe.detect_helmet.helmet_processor import HelmetProcessor
        model_path="models/yolov11_helmet.pt"

        self.helmet = HelmetProcessor(model_path, helmet_threshold=helmet_threshold, device=device, use_track_count=use_history_count,
                                      track_count=history_count, activate_iou=activate_iou)
        print("Kask tespit modeli başarı ile aktif edildi.")

    def activate_mask(self, device=None, mask_threshold=0.6, history_count=5, use_history_count=True, activate_iou=True):
        """ Maske tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                mask_threshold (float): Maske tespitinde, minimum güven skoru.
                use_history_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez 
                history_count (int): Her kişinin label tespiti için ortalaması alınacak geçmiş frame miktarı
                               (O anki label sonucu, belirlenen geçmiş x adet frame sonuçlarnının ortalaması alınarak belirlenir)
                activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
                                     False ise tüm kare üzerinde çalışır. """
        
        from src.detections.detect_ppe.detect_mask.mask_processor import MaskProcessor
        model_path="models/yolov11_mask.pt"
        
        self.mask = MaskProcessor(model_path=model_path, mask_threshold=mask_threshold, device=device, use_track_count=use_history_count,
                                  track_count=history_count, activate_iou=activate_iou)
        print("Maske tespit modeli başarı ile aktif edildi.")

    def activate_glasses(self, glasses_threshold=0.6, device=None, use_history_count=True, history_count=5, activate_iou=True):
        """ Gözlük tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                glasses_threshold (float): Gözlük tespitinde minimum güven skoru.
                use_history_count (bool): True ise geçmiş tespitleri dahil eder, False ise etmez 
                history_count (int): Her kişinin label tespiti için ortalaması alınacak geçmiş frame miktarı
                               (O anki label sonucu, belirlenen geçmiş x adet frame sonuçlarnının ortalaması alınarak belirlenir)
                activate_iou (bool): True ise model sadece tespit edilen kişilerin üzerinde çalışır, 
                                     False ise tüm kare üzerinde çalışır. """
        
        from src.detections.detect_ppe.detect_glasses.glasses_processor import GlassesProcessor
        model_path="models/yolov11_glasses.pt"

        self.glasses = GlassesProcessor(model_path,glasses_threshold=glasses_threshold, device=device, use_track_count=use_history_count,
                                        track_count=history_count, activate_iou=activate_iou)
        print("Gözlük tespit modeli başarı ile aktif edildi.")

    def activate_arc(self, device=None, history_count=2):
        """ Ark tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği
        """
                
        from src.detections.detect_environmental_danger.detect_ark.arc_processor import ArcProcessor
        model_path="models/yolov11_arc.pt"

        self.arc = ArcProcessor(model_path=model_path, device=device, history_count=history_count)
        print("Ark tespit modeli başarı ile aktif edildi.")

    def activate_fire(self, fire_threshold=0.4, device=None, history_count=20):
        """ Ateş tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                fire_threshold (float): Ateş tespitinde minimum güven skoru.
                history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği """
        
        from src.detections.detect_environmental_danger.detect_fire.fire_processor import FireProcessor
        import torch
        model_path="models/yolov11_fire_smoke.pt"

        if (self.fire_smoke is None):
            self.fire_smoke = YOLO(model_path)
            device = device if device is not None else "cuda" if torch.cuda.is_available() else "cpu"
            self.fire_smoke.to(device)
            
        self.fire = FireProcessor(threshold=fire_threshold,history_count=history_count)
        print("Ateş tespit modeli başarı ile aktif edildi.")

    def activate_smoke(self, smoke_threshold=0.4, device=None, history_count=20):
        """ Duman tespitini aktif hale getirir.
        
            Args:
                device (str): Modelin çalışacağı cihaz (cpu/cuda).
                smoke_threshold (float): Duman tespitinde minimum güven skoru.
                history_count (int): Son kaç frame'e göre çoğunluk kararı verileceği """
        
        from src.detections.detect_environmental_danger.detect_smoke.smoke_processor import SmokeProcessor
        model_path="models/yolov11_fire_smoke.pt"
        
        if (self.fire_smoke is None):
            self.fire_smoke = YOLO(model_path)
            device = device if device is not None else "cuda" if torch.cuda.is_available() else "cpu"
            self.fire_smoke.to(device)
        
        self.smoke = SmokeProcessor(threshold=smoke_threshold, history_count=history_count)
        print("Duman tespit modeli başarı ile aktif edildi.")

    def activate_zone_inactivity(self, detect_zone=True, detect_inactivity=True, zone_manager=None,
                                 movement_threshold=5, max_idle_time=0.2, cleanup_interval=300, cleanup_timeout=120):
        """ Alan ve/veya hareketsizlik tespitini aktif hale getirir.

        Args:
            zone_manager (object): ZoneManager sınıfından oluşturulmuş nesne 
            detect_inactivity (bool): hareketsizlik tespitinin yapılıp yapılmayacağını tutar.
            detect_zone (bool): zone tespitinin yapılıp yapılmayacaığını tutar.
            movement_threshold (float): Hareketsizlik tespiti için Kişinin hareketli olarak nitelendirilmesi için piksel
                                        cinsinden değişim. Bu eşik değerinden az değişim olursa kişi hareketsiz kabul edilir.
            max_idle_time (float): Kişinin hareketsiz olarak nitelendirilmesi için gereken maksimum süre (saniye).
            cleanup_interval (float): Otomatik temizlik işlemi aralığı (saniye). Varsayılan 5dk.
            cleanup_timeout (float): Bu süreden(2 dakika) uzun süredir ekranda gözükmeyen kişilere ait bilgileri temizler. 
             """ 
        
        from src.detections.detect_zone_inactivity.zone_inactivity_processor import ZoneInactivityProcessor, ZoneManager
        zone_manager = zone_manager if zone_manager is not None else  ZoneManager()
        if (detect_zone):
            if(not zone_manager.get_zones()):
                raise ValueError("Zone analizi için input alan bilgileri gerekli")

        self.zone_inactivity = ZoneInactivityProcessor(zone_manager, detect_inactivity, detect_zone,
                                                       movement_threshold=movement_threshold, max_idle_time=max_idle_time,
                                                       cleanup_interval=cleanup_interval,
                                                       cleanup_timeout=cleanup_timeout,
                                                       )
        print("Zone/inactivity tespit modeli başarı ile aktif edildi.")
    
    def activate_all(self, zone_manager=None, device=None, person_threshold=0.4, vest_threshold=0.3, 
                     helmet_threshold=0.3, mask_threshold=0.3,glasses_threshold=0.3,fire_threshold=0.4,smoke_threshold=0.4):
        """ Bütün analizleri aktif eder. (Zone analizi için input alan bilgileri gerekli) """

        self.activate_arc(device=device)
        self.activate_fire(fire_threshold=fire_threshold, device=device)
        self.activate_smoke(smoke_threshold=smoke_threshold, device=device)
        self.activate_person(device=device, person_threshold=person_threshold)
        self.activate_zone_inactivity(zone_manager=zone_manager)
        self.activate_glasses(glasses_threshold=glasses_threshold, device=device)
        self.activate_helmet(device=device, helmet_threshold=helmet_threshold)
        self.activate_mask(device=device, mask_threshold=mask_threshold)
        self.activate_vest(device=device, vest_threshold=vest_threshold)
            
    def analyze(self, frame):
        """Aktif edilen tespit türlerini çalıştırır ve tespit sonuçlarını birleştirerek döner.
            
            Args:
                frame (numpy.ndarray): Tespit yapılacak görüntü karesi 

            Returns:
                List: Dict türündeki her bir analiz sonucunun birleştirildiği liste."""

        tasks = {}
        person_future = None

        with ThreadPoolExecutor() as executor:

            if (self.vest or self.helmet or self.mask or self.glasses or self.zone_inactivity) and self.person is None:
                self.activate_person()

            if self.person:
                person_future = executor.submit(self.person.detect, frame)

            if self.fire_smoke:
                fire_smoke_future = executor.submit(
                    self.fire_smoke.predict,
                    source=frame,
                    classes=[0, 2],
                    verbose=False,
                )

            if self.arc:
                tasks[executor.submit(self.arc.process_frame, frame)] = "arc"

            person_detections = person_future.result() if person_future else None
            self.detections["person"] = person_detections

            if self.vest:
                tasks[executor.submit(self.vest.process_frame, frame, person_detections)] = "vest"
            if self.helmet:
                tasks[executor.submit(self.helmet.process_frame, frame, person_detections)] = "helmet"
            if self.mask:
                tasks[executor.submit(self.mask.process_frame, frame, person_detections)] = "mask"
            if self.glasses:
                tasks[executor.submit(self.glasses.process_frame, frame, person_detections)] = "glasses"
                
            if self.zone_inactivity:
                tasks[executor.submit(self.zone_inactivity.process_frame, person_detections)] = "zone_inactivity"

            if self.fire_smoke:
                env_model_results = fire_smoke_future.result()

                if self.fire:
                    tasks[executor.submit(self.fire.process_frame, frame, env_model_results)] = "fire"
                if self.smoke:
                    tasks[executor.submit(self.smoke.process_frame, frame, env_model_results)] = "smoke"    

            for future in as_completed(tasks):
                key = tasks[future]
                self.detections[key] = future.result()
          
        return self._combine_active_analysis()
        
    def _combine_active_analysis(self):
        """ Aktif analiz türlerini birleştirirek dizi halinde dönderir. (Kişi tespiti bir analiz türü olarak alınmamakta.) """

        frame_results=[]
        for k, v in self.detections.items():
            if v is not None and k != "person":
                frame_results.append(v)

        return frame_results

    def get_person_detection(self):
        """ Kişi tespit sonuçlarını liste biçiminde dönderir. """

        person_rest=self.detections["person"] if self.detections["person"] is not None else []
        return person_rest

