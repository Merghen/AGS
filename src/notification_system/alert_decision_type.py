class AlertDecisionEngine:
    """
    Tehlike analiz sonuçlarını karşılaştırarak hangi durumda bildirim yapılacağını belirler.
    """

    def __init__(self,
                 inform_when_dangerCount_change=False,
                 inform_when_danger_level_change=False,
                 inform_when_newDanger_occured=False):
        self.inform_when_dangerCount_changed = inform_when_dangerCount_change
        self.inform_when_danger_level_changed = inform_when_danger_level_change
        self.inform_when_newDanger_occured = inform_when_newDanger_occured


    def evaluate(self, previous_result, current_result):
        """
        Yeni sonuçları değerlendirir ve gönderilmesi gereken mesajları döndürür.

        Args:
            previous_result(dict): Bir önceki frame tehlike bilgilerini tutar.
            current_result(dict): Güncel frame tehlike bilgilerini tutar.

        Returns:
            list[str]: Bildirim mesajları listesi (boşsa bildirim gerekmez)
        """
        # İlk analiz durumu
        if not previous_result:
            return self._check_first_analysis(current_result)

        data = self._extract_comparison_data(previous_result, current_result)
    
        messages = []
        # default olarak mesaj gönderilecek durumlar
        messages += self._check_normalization(data["prev_level"], data["curr_level"])
        messages += self._check_new_danger_start(data["prev_level"], data["curr_level"])

        # isteğe bağlı olarak mesaj gönderilecek durumlar
        messages += self._check_level_change(data["prev_level"], data["curr_level"])
        messages += self._check_count_change(data["prev_count"], data["curr_count"])
        messages += self._check_new_danger_type(data["prev_level"], data["prev_reasons"], data["curr_reasons"])

        return messages

    def _extract_comparison_data(self, previous_result, current_result):
        """ Verileri çeker ve sözlük yardımıyla dönderir. """

        return {
            "prev_level": previous_result.get("overall_danger_level"),
            "curr_level": current_result.get("overall_danger_level"),
            "prev_count": previous_result.get("amount_of_danger", 0),
            "curr_count": current_result.get("amount_of_danger", 0),
            "prev_reasons": set(previous_result.get("danger_reason", [])),
            "curr_reasons": set(current_result.get("danger_reason", [])),
        }

    def _check_first_analysis(self, current_result):
        """İlk analizde tehlike varsa mesaj döndürür. 
        (previsous_result None olduğu için ekstra bu kontrole ihtiyaç duyar)"""

        if current_result.get("overall_danger_level") != "green":
            return ["⚠️ Tehlike Tespit Edildi!"]
        return []

    def _check_normalization(self, prev_level, curr_level):
        """Sistem tehlikeden normale döndüyse bildir."""

        if prev_level != "green" and curr_level == "green":
            return [f"✅ Mevcut Tehlike(ler) Giderildi."]
        return []

    def _check_new_danger_start(self, prev_level, curr_level):
        """Yeşilden tehlikeye geçiş varsa bildir."""

        if prev_level == "green" and curr_level != "green":
            return [f"⚠️ Tehlike Tespit Edildi!"]
        return []

    def _check_level_change(self, prev_level, curr_level):
        """
        Tehlike seviyesi değiştiyse bildir.
        (green -> X veya X-> green durumları geçerli değil. Bu durumlar başka koşulda ele alınıyor.)"""
        
        if (
            self.inform_when_danger_level_changed
            and curr_level != prev_level
            and prev_level != "green"
            and curr_level != "green"
        ):    
            prev_level_tr="Kırmızı" if prev_level =="Red" else "Sarı" if prev_level=="yellow" else "Yeşil"
            curr_level_tr="Kırmızı" if curr_level =="Red" else "Sarı" if curr_level=="yellow" else "Yeşil"
            return [f"⚠️ Tehlike Seviyesinde Değişim Mevcut. {prev_level_tr} → {curr_level_tr}"]
        return []

    def _check_count_change(self, prev_count, curr_count):
        """
        Tehlike miktarında artış veya azalış varsa bildir.
        (0 → X veya X → 0 durumları hariç tutulur, çünkü onlar başka koşullarda ele alınıyor.)"""

        if (
            self.inform_when_dangerCount_changed
            and curr_count != prev_count
            and curr_count != 0
            and prev_count != 0
        ):
        
            direction = "Artış" if curr_count > prev_count else "Azalış"
            return [f"⚠️ Tehlike Miktarında {direction} Tespit edildi."]
        return []

    def _check_new_danger_type(self, prev_level, prev_reasons, curr_reasons):
        """Yeni bir tehlike türü ortaya çıktıysa bildir. 
        (Tehlike hali hazırda mevcut ve yeni bir tehlike türü tespit edildiğinde bildirir.)"""
 
        if (
            self.inform_when_newDanger_occured
            and not curr_reasons.issubset(prev_reasons)
            and prev_level != "green"
        ):
            new_dangers = ", ".join(curr_reasons - prev_reasons)
            return [f"⚠️ Yeni Tehlike Türü Tespit Edildi: ({new_dangers})"]
        return []
