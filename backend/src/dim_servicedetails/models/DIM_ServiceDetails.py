class DIM_Details:
    """
    Clase encargada de manejar los detalles del servicio.

    Esta clase define la estructura de un objeto que representa los detalles de un servicio,
    incluyendo su identificador, fechas, tipo, monto y el ID del servicio asociado.
    """
    
    def __init__(self, DIM_ServiceDetailsId: str, DIM_DateId: int, DIM_ServiceId: str, serviceDetailesType: str, amount: float, StartDate: str, EndDate: str) -> None:
        """
        Constructor de la clase DIM_Details.

        Args:
            DIM_ServiceDetailsId (str): El identificador unico del detalle del servicio.
            DIM_DateId (int): El identificador de la fecha.
            DIM_ServiceId (str): El identificador del servicio asociado.
            serviceDetailesType (str): El tipo de detalle del servicio.
            amount (float): El monto asociado al detalle del servicio.
            StartDate (str): La fecha de inicio del servicio en formato de cadena (por ejemplo, 'YYYY-MM-DD').
            EndDate (str): La fecha de finalizacion del servicio en formato de cadena (por ejemplo, 'YYYY-MM-DD').
        """
        self.DIM_ServiceDetailsId = DIM_ServiceDetailsId
        self.DIM_DateId = DIM_DateId
        self.DIM_ServiceId = DIM_ServiceId        
        self.serviceDetailesType = serviceDetailesType
        self.amount = amount
        self.StartDate = StartDate
        self.EndDate = EndDate
        
    def to_dict(self) -> dict[str, str | float]:
        """
        Convierte el objeto a un diccionario.

        Returns:
            dict[str, str | float]: Un diccionario que contiene todos los atributos del objeto.
        """
        return {
            "DIM_ServiceDetailsId": self.DIM_ServiceDetailsId,
            "DIM_DateId": self.DIM_DateId,
            "DIM_ServiceId": self.DIM_ServiceId,
            "serviceDetailesType": self.serviceDetailesType,
            "amount": self.amount,
            "StartDate": self.StartDate,
            "EndDate": self.EndDate
        }