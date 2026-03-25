# AGS

Bu proje, görüntü üzerinde tehlike durumlarını analiz eder. Sistem, herhangi bir tehlike durumunda ilgili kanallara bildiri gönderir.

## Tanıtım

1. Görüntü üzerinde ilgili analiz türlerini tespit eder.
2. Tespit sonuçlarını analiz ederek tehlike durumlarını ve seviyelerini belirler.
3. Tehlike durum bilgilerini ilgili iletişim kanallarına gönderir.

## Bağımlılıklar

1. OpenCV (cv2): Görüntü işleme, nesne tespiti ve çizim işlemleri için kullanılmıştır.
2. Ultralytics (YOLO): Derin öğrenme tabanlı modeller aracılığıyla nesne tespiti işlemlerinde kullanılmıştır.
3. Torch (PyTorch): Modelin çalışacağı cihazı kontrol etmek için kullanılmıştır.
4. Asyncio: Bildiri gönderme süreçlerinde asenkron işlemlerin gerçekleştirilmesi amacıyla kullanılmıştır.
5. Telethon: Telegram API’si üzerinden mesaj göndermek için kullanılmıştır.
6. aiosmtplib: E-posta gönderimi için kullanılmıştır
7. slack_sdk: Slack üzerinden bildirim işlemlerini gerçekleştirmek için kullanılmıştır.

## Kurulum

1. Projeyi klonlayın:

```python
git clone https://github.com/halilmuslu/AGS.git
```

2. Gerekli gereksinimleri yükleyin:

```python
pip install -r requirements.txt
```

## Kullanım

```python
import cv2
import asyncio
from src.notification_system.alert_system import AlertSystemManager
from src.analyse_danger.danger_analyse import DangerAnalyzerManager
from src.draw.visualize_results import FrameVisualizer
from manage_detections import DetectionManager

async def main():

    source = "assets/test_video.mp4"
    cap = cv2.VideoCapture(source)
    detection = DetectionManager()

    # İstenilen tespit türlerini aktif hale getirin
    detection.activate_fire()
    detection.activate_vest()

    danger_analayzer = DangerAnalyzerManager() # Tehlike analizi, aktif hale getirilir.
    visualizer = FrameVisualizer() # Tespit ve tehlike sonuçlarını görselleştirmek için bu sınıfı aktif hale getiriyoruz.
    # alert = AlertSystemManager() # Tehlike durumlarını mesaj olarak gönderme işlemini yönetir.

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Aktif tespit türlerini kullanarak görüntüyü analiz eder.
        analysis_results=detection.analyze(frame)

        # Tespit edilen kişileri ekrana çizdirmek için kişi tespit bilgilerini alır.
        person_detection=detection.get_person_detection()

        # Tespit sonuçlarını analiz ederek tehlike durumlarını ve seviyelerini belirler.
        danger_result=danger_analayzer.calculate_danger(analysis_results)

        # Tehlike sonucunu ilgili kanala gönderir.
        #await alert.evaluate_and_notify(result=danger_result, selected_notifiers=['telegram'])

        # Sonuçları görselleştirir.
        frame=visualizer.visualize(frame,
                                   analysis_results=analysis_results,
                                   danger_result=danger_result,
                                   person_detection=person_detection)

        cv2.imshow("Sonuc", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
```

## Dikkat edilmesi gerekenler

### **NOT:**

- Ekipman, alan ve hareketsizlik analizleri için kişi tespiti aktif hale getirilmelidir. Eğer kişi tespiti manuel olarak aktif hale getirilmemişse, sistem otomatik olarak varsayılan parametreler ile kişi tespitini aktif hale getirir.

- Eğer kişi tespitindeki parametreleri özelleştirmek isterseniz kişi tespitini manuel olarak aktif hale getirin.

```python
detection.activate_person(person_threshold=0.5, device="cuda")
detection.activate_vest()
```

### **NOT:**

Bölge(Zone) tespitini **aktif** hale getirebilmek için dışardan analizi yapılacak **bölgenin bilgisi** girilmesi **zorunludur**.

Örnek Bölge & Hareketsizlik Tespit Kullanımı:

```python
import cv2
import asyncio
from src.notification_system.alert_system import AlertSystemManager
from src.analyse_danger.danger_analyse import DangerAnalyzerManager
from src.draw.visualize_results import FrameVisualizer
from manage_detections import DetectionManager
from src.detections.detect_zone_inactivity.zone_inactivity_processor import ZoneSelector, ZoneManager

async def main():

    source = "assets/test.mp4"
    cap = cv2.VideoCapture(source)

    # Bölge bilgilerini belirleyeceğimiz/çizeceğimiz görüntüyü alıyoruz.
    ret, first_frame = cap.read()

    detection = DetectionManager()
    zone_manager = ZoneManager()

    # Çizim işlemi yapılacak görseli ve bölge bilgilerinin kaydedileceği nesne bilgisini ilgili sınıfa veriyoruz.
    selector = ZoneSelector(first_frame, zone_manager=zone_manager)

    selector.start_interface() # Çizim işlemlerini gerçekleştireceğimiz konsol arayüzünü çalıştırır.

    # Bölge veya hareketsizlik tespitini bağımsız şekilde aktif hale getirebilirsiniz.
    # Sadece hareketsizlik tespiti aktif olduğu durumda zone manager nesnesine gerek yok.
    detection.activate_zone_inactivity(detect_zone=True, detect_inactivity=True, zone_manager=zone_manager)

    danger_analayzer = DangerAnalyzerManager()  # Tehlike analizi aktif hale getirilir.

    input_zone_infos=zone_manager.get_zones() # Çizilen bölgelere ait bilgileri al.

    # Bölge bilgilerini ekranda çizdirmek için bölge bilgilerini FrameVisualizer sınıfına gönder(Opsiyonel).
    visualizer = FrameVisualizer(input_zone_infos=input_zone_infos)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        analysis_results=detection.analyze(frame)
        person_detection=detection.get_person_detection()
        danger_result=danger_analayzer.calculate_danger(analysis_results)

        frame=visualizer.visualize(frame,
                                   analysis_results=analysis_results,
                                   danger_result=danger_result,
                                   person_detection=person_detection)

        cv2.imshow("Sonuc", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    asyncio.run(main())
```

### Manuel Bölge Bilgisi Ekleme

```python
import asyncio
from manage_detections import DetectionManager
from src.detections.detect_zone_inactivity.zone_inactivity_processor import ZoneManager

async def main():

    zone_manager = ZoneManager()
    # Bölgelere ait bilgileri manuel olarak tek tek eklenebilir.
    zone_manager.add_zone([(350, 350), (600, 350), (800, 600), (150, 600)], "alan1", "red", line_color=(0, 0, 255))
    zone_manager.add_zone([(720, 320), (900, 290), (1000, 480), (900, 550)], "alan2", "yellow", line_color=(0, 255, 255))
    detection = DetectionManager()
    detection.activate_zone_inactivity(detect_zone=True, detect_inactivity=True, zone_manager=zone_manager)

if __name__ == "__main__":
    asyncio.run(main())
```

### Performans Hızını Artırma

1. Model tespit işlemini GPU üzerinden çalıştır.
2. Ekipman tespitlerinde RIO özelliğini kapat (tespit başarısını düşürebilir).

```python
detection.activate_mask(activate_iou=False, device="cuda")

```

3. Tespit işlemini belirli aralıklar ile yap.

```python
    # Tespit işlemi kaç frame'de bir çalıştırılacak
    analysis_interval= 3
    frame_count = analysis_interval - 1

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % analysis_interval == 0:
            last_analysis_results=detection.analyze(frame)

        analysis_results=last_analysis_results
        danger_result=danger_analayzer.calculate_danger(analysis_results)
```
