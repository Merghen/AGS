import cv2
import numpy as np

class FrameVisualizer:
    def __init__(self, input_zone_infos=None):
        """
        Args:
            input_zone_infos (list): İnput zone bilgilerini tutan liste 
        """

        self.input_zone_infos = input_zone_infos

    def _draw_environmental_det_res(self, frame, analysis_results):
        """
        Çevresel tehlike sonuçlarını (smoke, fire, ark) frame üzerine çizer.
        """
        if not analysis_results:
            return
        
        y_offset = 50
        for result in analysis_results:
            if not result:
                continue

            detection_type = result.get("detection", "Unknown")
            detect = result.get("detect", False)

            if detection_type in ["smoke", "fire", "ark"]:
                label = f"{detection_type.capitalize()}: "
                cv2.putText(
                    frame,
                    label,
                    (10, y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (255, 255, 255), 
                    2
                )

                text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                detect_text = str(detect)
                detect_color = (0, 0, 255) if detect else (0, 255, 0) 
                cv2.putText(
                    frame,
                    detect_text,
                    (50 + text_size[0], y_offset),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    detect_color,
                    2
                )

                y_offset += 30

    def _draw_person_results(self, frame, analysis_results, person_detection):
        """
        Kişiye ait analiz sonuçlarını çizer.
        """

        if not person_detection:
            return

        for r in person_detection:
            box = r['box']
            track_id = r['track_id']
            
            person_color=(28, 141, 239)
            cv2.rectangle(frame, (box[0], box[1]), (box[2], box[3]), person_color, 2)
            cv2.putText(frame, f"ID: {track_id}", (box[0], box[3]+15),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                person_color,
                2)
            y_offset = 10

            for result in analysis_results:
                if not result or "detail" not in result:
                    continue

                detection_type = result.get("detection", "Unknown")
                detect = result.get("detect", False)
                ids = result["detail"].get("id", [])
                statuses = result["detail"].get("status", [])

                if not detect or not ids:
                    continue

                if track_id in ids:
                    idx = ids.index(track_id)

                    # PPE tespiti
                    y_offset = self._draw_ppe_result(frame, box, detection_type, statuses, idx, y_offset)

                    # inactivity tespiti
                    if detection_type == "zone_inactivity":
                        zone_types = result["detail"].get("zone_type", [])
                        zone_names = result["detail"].get("zone_name", [])
                        is_moving = result["detail"].get("is_person_moving", [])

                        y_offset = self._draw_inactivity_result(frame, box, is_moving, idx, y_offset)

                        # Zone tespiti 
                        if len(zone_names) != 0:
                            zone_type = zone_types[idx] if idx < len(zone_types) else None
                            y_offset = self._draw_zone_result(frame, box, zone_type, y_offset)

    def _draw_ppe_result(self, frame, box, detection_type, statuses, idx, y_offset):
        """PPE (maske, yelek, gözlük, kask) durumlarını çizer."""

        status = statuses[idx] if idx < len(statuses) else "N/A"
        if status != "N/A":
            label = f"{detection_type}: "
            label_pos = (box[0], box[1] - y_offset)

            cv2.putText(
                frame,
                label,
                label_pos,
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

            color = (0, 255, 0) if status else (0, 0, 255)
            text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.putText(
                frame,
                str(status),
                (label_pos[0] + text_size[0], label_pos[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )
            y_offset += 20
        return y_offset


    def _draw_inactivity_result(self, frame, box, is_moving, idx, y_offset):
        """Kişinin hareket (inactivity) durumunu çizer."""

        move = is_moving[idx] if idx < len(is_moving) else None

        label = "Moving: "
        label_pos = (box[0], box[1] - y_offset)
        cv2.putText(
            frame,
            label,
            label_pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )

        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        cv2.putText(
            frame,
            str(move),
            (label_pos[0] + text_size[0], label_pos[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (0, 255, 0) if move else (0, 0, 255),
            2,
        )
        y_offset += 20
        return y_offset

    def _draw_zone_result(self, frame, box, zone_type, y_offset):
        """Kişinin içinde olduğu zone bilgisini çizer."""
        
        label = "Zone: "
        label_pos = (box[0], box[1] - y_offset)
        cv2.putText(
            frame,
            label,
            label_pos,
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            2,
        )

        text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
        zone_text = f"{zone_type}" if zone_type else "None"

        # Zone rengi
        color = (255, 255, 255)
        if zone_text == "yellow":
            color = (0, 255, 255)
        elif zone_text == "red":
            color = (0, 0, 255)
        elif zone_text == "green":
            color = (0, 255, 0)

        cv2.putText(
            frame,
            zone_text,
            (label_pos[0] + text_size[0], label_pos[1]),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            2,
        )
        y_offset += 20
        return y_offset
    
    def _draw_zones(self, frame):
        """
        Dışardan girilen zone bilgilerini çizer.
        """
        if self.input_zone_infos is None:
            return

        for zone in self.input_zone_infos:
            coordinates = zone['coordinates']
            name = zone['name']
            zone_type = zone['type']
            line_color = zone['line_color']
            text_color = zone['text_color']
            scale = zone['scale']
            thickness = zone['thickness']

            pts = np.array(coordinates, np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [pts], isClosed=True, color=line_color, thickness=2)
            cv2.putText(
                frame,
                f"{name} ({zone_type})",
                tuple(pts[0][0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                scale,
                text_color,
                thickness
                )

    def _draw_danger(self, frame, danger_result):

        if not danger_result:
            return
            
        overall_danger_level=danger_result["overall_danger_level"]
        amount_of_danger=danger_result["amount_of_danger"]

        if overall_danger_level=="green":
            color= (0,255,0)

        elif overall_danger_level=="yellow":
            color= (0,255,255)    

        elif overall_danger_level=="red":   
            color=(0,0,255)

        h, w, _ = frame.shape
        x_pos = int(w * 0.8)
        y_pos = int(h * 0.05)
        cv2.putText(
            frame,
            f"Danger Level: {overall_danger_level}",
            (x_pos, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
            )
        
        cv2.putText(
            frame,
            f"Number of Danger: {amount_of_danger}",
            (x_pos, y_pos+60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            color,
            2,
            )

    def visualize(self, frame, analysis_results=[], person_detection=[], danger_result={}):
        """
        Analiz sonuçlarını ekrana çizdirir.

            Args:
                frame (np.ndarray): BGR formatında görüntü.
                analysis_results (list): Kare içerisinde tespit edilen analizlerin sonuçlarını tutan liste.
                person_detection (list): Kişi tespit sonuçları.
                danger_result (dict): Genel tehlike seviyesi, tehlike sayısı ve detayları içeren sözlük.
            
            Returns:
                frame (np.ndarray): İşlenmiş görüntü.

        """
        
        self._draw_environmental_det_res(frame, analysis_results)
        self._draw_person_results(frame, analysis_results, person_detection)
        self._draw_danger(frame,danger_result)
        self._draw_zones(frame)
        
        return frame
