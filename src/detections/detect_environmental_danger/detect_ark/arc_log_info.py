from ...base_detection_info_logger import BaseInfoLogger

class ArcInfoLogger(BaseInfoLogger):
    """ Her bir karedeki tespit bilgisini anlık dönderir."""
   
    def __init__(self, detection_type="ark"):

        """ Anlık tespit bilgisini oluşturur ve sözlük olarak saklar.

        Args:
            detection_type (str, optional): Tespit edilen sınıf türü (maske,duman,ark vs). Varsayılan None.

        """
        
        super().__init__(detection_type)

    
