from .base_notifier import BaseNotifier
from dotenv import load_dotenv
from telethon import TelegramClient
import os
import asyncio

class TelegramNotifier(BaseNotifier):
    """ İlgili kanala veya kişiye mesaj gönderimini yapar. """

    def __init__(self, chat_id):
        """
        Notifier'ı başlatır ve Telegram yapılandırmasını yükler.

        Args:
            chat_id (int | str): Mesaj gönderilecek hedef kanal veya kullanıcı kimliği."""
        
        self.chat_id = int(chat_id)
        self.client_lock = asyncio.Lock()  # Aynı anda erişimi engellemek için
        self._client_started = False  
        self._load_config()

    def _load_config(self):
        """
        Telegram bot yapılandırmasını ortam değişkenlerinden yükler."""
        
        load_dotenv()
        self.TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.TELEGRAM_API_ID = os.getenv("TELEGRAM_API_ID")
        self.TELEGRAM_API_HASH = os.getenv("TELEGRAM_API_HASH")
        self.client = TelegramClient("bot_session", api_id=self.TELEGRAM_API_ID, api_hash=self.TELEGRAM_API_HASH)

    async def _ensure_started(self):
        """Telegram istemcisinin başlatıldığından emin olur. Aynı anda birden fazla istemci başlatılmasının önüne geçer."""

        if not self._client_started:
            await self.client.start(bot_token=self.TELEGRAM_BOT_TOKEN)
            self._client_started = True

    async def send(self, message, **kwargs):
        """Telegram üzerinden mesaj gönderir.

            Args:
                message (str): Gönderilecek mesaj içeriği."""

        async with self.client_lock:
            await self._ensure_started()
            try:
                await self.client.send_message(self.chat_id, message)
                print(f"Message has been sent succesfully on telegram.")
    
            except Exception as e:
                print(f"An error occurred while sending message on telegram: {e}")
             
