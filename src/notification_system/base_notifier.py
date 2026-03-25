class BaseNotifier:
    """
    Tüm bildirim kanalları için temel arayüz (interface) sınıfıdır.
    
    Bu sınıf doğrudan kullanılmaz. Bunun yerine her bir bildirim kanalı (email,sms,telegram vb.)
    bu sınıfı kalıtım alarak kendi 'send' metodunu yazmalıdır.
    """
    def send(self, **kwargs):
        raise NotImplementedError("Her bildirim sınıfı kendi send metodunu yazmalı.")