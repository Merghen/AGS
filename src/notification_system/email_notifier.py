from .base_notifier import BaseNotifier
import aiosmtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

class EmailNotifier (BaseNotifier):
    """ EmailNotifier sınıfı, verilen alıcıya e-posta gönderimi yapmak için kullanılır.
        Gmail SMTP sunucusu üzerinden e-posta gönderir. """

    def __init__(self, recipient:str):
        """
        EmailNotifier nesnesini başlatır ve konfigürasyon işlemlerini yükler.

        Args:
            recipient (str): E-posta alıcısının adresi
        """

        self.recipient=recipient
        self._load_config()
        
    def _load_config(self):
        """
        e-posta konfigürasyonunu sağlar.
        """

        load_dotenv()
        self.SMTP_SERVER = "smtp.gmail.com"
        self.SMTP_PORT = os.getenv("EMAIL_SMTP_PORT")
        self.EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
        self.EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    async def send(self,message:str, **kwargs):
        """
        Verilen mesajı alıcıya e-posta olarak gönderir.

        Args:
            message (str): Gönderilecek mesajın içeriği
        """

        email_message = self._create_email(message)

        try:
            await aiosmtplib.send(
                email_message,
                hostname=self.SMTP_SERVER,
                port=self.SMTP_PORT,
                start_tls=True,
                username=self.EMAIL_ADDRESS,
                password=self.EMAIL_PASSWORD,
            )
            print("Mail has been sent succesfully.")
        except Exception as e:
            print(f"An error occurred while sending mail: {e}")
            
    def _create_email(self, message: str):
        """
        MIME formatında e-posta mesajı oluşturur.

        Args:
            message (str): Mesajın içeriği

        Returns:
            MIMEMultipart: Gönderime hazır e-posta mesajı
        """

        email_message = MIMEMultipart()
        email_message['From'] = self.EMAIL_ADDRESS
        email_message['To'] = self.recipient
        email_message['Subject'] = 'Smart Security Systems Danger Notification'
        email_message.attach(MIMEText(message, 'plain'))
        return email_message

    


