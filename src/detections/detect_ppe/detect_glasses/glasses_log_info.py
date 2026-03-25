from ..base_ppe_info_logger import BasePPEInfoLogger

class GlassesInfoLogger(BasePPEInfoLogger):
    """ Her bir karedeki tespit bilgisini anlık dönderir."""
   
    def __init__(self, detection_type="glasses"):

        """ Anlık tespit bilgisini oluşturur ve sözlük olarak saklar.

        Args:
            detection_type (str, optional): Tespit edilen sınıf ismi.

        """
        super().__init__(detection_type)

