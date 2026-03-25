from .base_notifier import BaseNotifier
from slack_sdk import WebClient
import os
from dotenv import load_dotenv

class SlackNotifier (BaseNotifier):
    """
    Slack üzerinden belirli bir kanala mesaj gönderir.
    """
    
    def __init__(self,channel_name):
        """
        SlackNotifier nesnesini başlatır ve konfigürasyon işlemlerini yükler.

        Args:
            channel_name (str): Mesaj gönderilecek Slack kanalı adı (örn. '#general').
                                (mesaj gönderilecek kanalda bot'un eklenmesi gerekmekte.)
        """
      
        load_dotenv()
        self.SLACK_TOKEN = os.getenv("SLACK_TOKEN")
        self.channel_name = channel_name

    async def send(self,message:str, **kwargs):
        """
        Verilen mesajı Slack kanalına gönderir.

        Args:
            message (str): Gönderilecek mesajın içeriği."""

        client = WebClient(token=self.SLACK_TOKEN)
        try:
            client.chat_postMessage(channel=self.channel_name, text=message, **kwargs)
            print(f"Message has been sent succesfully on slack")
        except Exception as e:
            print(f"An error occurred while sending message on slack: {e}")
            

        
    


