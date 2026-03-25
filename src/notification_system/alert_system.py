from .telegram_notifier import TelegramNotifier
from .email_notifier import EmailNotifier
from .slack_notifier import SlackNotifier
from .alert_decision_type import AlertDecisionEngine
import asyncio
from dotenv import load_dotenv
import os

class AlertSystemManager:
    """
    Farklı bildirim kanallarını yöneten ve uygun olanı çağıran sınıf.
    """ 
    def __init__(self,
                telegram_chat_id=None,
                email_recipient=None,
                slack_channel_name=None,
                inform_when_dangerCount_change=False,
                inform_when_danger_level_change=False,
                inform_when_newDanger_occured=False
                      ):
        """ 
            Args:  
                telegram_chat_id (int): Telegram bildirimlerinin gönderileceği chat ID. 
                email_recipient (str): E-posta bildirimlerinin gönderileceği adres.
                slack_channel_name (str): Slack bildirimlerinin gönderileceği kanal ismi.
                inform_when_dangerCount_change (bool): Tehlike sayısında değişiklik olduğunda bildirim gönderir default=False
                inform_when_danger_level_change (bool), Tehlike seviyesin değişiklik olduğunda bildirim gönderir default=False 
                inform_when_newDanger_occured (bool), Yeni tehlike algılandığında bildirim gönderilmesini sağlar. default=False
        """

        load_dotenv()
        self.notifiers = {
            "telegram": TelegramNotifier(chat_id=telegram_chat_id or os.getenv("TELEGRAM_CHAT_ID")),
            "email":EmailNotifier(recipient=email_recipient or os.getenv("EMAIL_RECIPIENT")),
            "slack":SlackNotifier(channel_name=slack_channel_name or os.getenv("SLACK_CHANNEL_NAME"))
        }

        # Karar motoru
        self.decision_engine = AlertDecisionEngine(
            inform_when_dangerCount_change=inform_when_dangerCount_change,
            inform_when_danger_level_change=inform_when_danger_level_change,
            inform_when_newDanger_occured=inform_when_newDanger_occured

        )
        self.previous_result = None

    async def evaluate_and_notify(self, result, selected_notifiers=None):
        """
        Tehlike analiz sonucunu değerlendirir ve ilgili kanalları çalıştırır..

        Args:
            result (dict): tehlike analiz sonucu
            selected_notifiers (list[str] | None): kullanılacak bildirim kanalları (örn. ['email', 'telegram','slack'])
                Eğer None veya boşsa tüm bildirim kanalları çalışır.
        """

        detail_messages = self.decision_engine.evaluate(self.previous_result, result)

        message=self._configure_notification_message(detail_messages,result)

        if len(detail_messages)>0:
            if not selected_notifiers:
                await self.send_alert("all", message)
            else:
                for notifier_type in selected_notifiers:
                    await self.send_alert(notifier_type, message)
        else:
            # print("[INFO] Notification not send")
            pass

        # Güncel sonucu sakla
        self.previous_result = result
    
    def _configure_notification_message(self,detail_messages,result):
        """ Tehlike sonuçlarını ve detay bilgilerini birleştirerek bildiri mesajını hazır hale getirir.
            (Eğer tehlike giderilmişse frame sonucu elde edilen analiz gönderilmemektedir.)
         
            Args:
                detail_messages(list): Güncel tehlikedeki değişimlerin bilgilerini tutar.
                result (dict): Frame sonucunda elde edilen tehlike analiz sonucu
            
            Return
                final_output(str): Hazır hale getirilmiş bildiri mesajı.

           """
        
        detailed_message = '\n'.join(f'{eleman}' for eleman in detail_messages)
        final_output=detailed_message

        if(result["amount_of_danger"]!=0):
            detailed_result=self._format_frame_result(result)
            final_output = f"{detailed_message}\n\n{detailed_result}"
        return final_output
    
    def _format_frame_result(self,result):
        """
        Frame'den gelen tehlike analiz sonucunu düzenli ve okunabilir bir mesaj haline getirir.

        Args:
            result (dict): Analiz sonuç sözlüğü

        Returns:
            str: Kullanıcıya gönderilecek biçimlendirilmiş mesaj.
        """
        
        levels = result.get("danger_level", [])
        reasons = result.get("danger_reason", [])

        overall_level = result.get("overall_danger_level", "").lower()
        # yeşil durumda detailed frame sonucunu göndermediğimiz için o durumu kontrol etmeye gerek yok.
        if overall_level =="red":
            emoji = "🔴"
        else:
            emoji = "🟡"
        danger_level_en=result.get('overall_danger_level', 'Bilinmiyor')
        danger_level_tr="Kırmızı" if danger_level_en =="red" else "Sarı" if danger_level_en=="yellow" else "Bilinmiyor"
        message = (
            f"{emoji}Detaylı Tehlike Raporu{emoji}\n"
            f"-----------------------------\n"
            f"📅 Tarih: {result.get('time', 'unknown')}\n"
            f"🔥 Genel Tehlike Seviyesi: {danger_level_tr}\n"
            f"🚨 Toplam Tehlike Miktarı: {result.get('amount_of_danger', 0)}\n\n"
            f"📊 *Tehlike Detayları:*\n"
        )

        for level, reason in zip(levels, reasons):
            level="Kırmızı" if level =="red" else "Sarı" if level=="yellow" else "Bilinmiyor"
            message += f"• Tehlike Sebebi: {reason} ({level} kod)\n"

        return message
    
    async def send_alert(self, notifier_type, message):
        """
        Belirtilen bildirim kanalına göre bildiri mesajını gönderir.

            Args:
                notifier_type(str): dışardan belirlenen bildirim türü("email","telegram","all")
                message(str): Gönderilecek mesaj içeriği
        """

        if notifier_type == "all":
            for notifier in self.notifiers.values():
                await notifier.send(message)
            return

        notifier = self.notifiers.get(notifier_type)
        if not notifier:
            raise ValueError(f"Böyle bir bildirim türü bulunamadı: {notifier_type} \n Mevcut bildiri türleri: telegram, email, slack")

        await notifier.send(message)

        
# test
if __name__ == "__main__":

    async def main():

        from create_dummy_danger import DummyDangerGenerator
        alert=AlertSystemManager()

        generator = DummyDangerGenerator(frame_length=30, repeat_limit=5,selected_reasons=[[],['smoke'],['helmet','vest'],[],[],['fire']])
        danger_results = generator.create_log()

        for danger_result in danger_results:
            await alert.evaluate_and_notify(danger_result,selected_notifiers=['telegram',"email","slack"])
        
    asyncio.run(main())