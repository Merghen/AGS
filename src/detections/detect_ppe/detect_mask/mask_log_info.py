from ..base_ppe_info_logger import BasePPEInfoLogger

class MaskInfoLogger(BasePPEInfoLogger):
    """ Her bir karedeki tespit bilgisini anlık dönderir."""
   
    def __init__(self, detection_type="mask"):

        """ Anlık tespit bilgisini oluşturur ve sözlük olarak saklar.

        Args:
            detection_type (str, optional): Tespit edilen sınıf ismi.

        """

        super().__init__(detection_type)