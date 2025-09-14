class PendingPaidModel:
    """
    Modelo de datos para representar un pago pendiente.

    Esta clase se utiliza para estructurar la información de pagos pendientes,
    incluyendo el año fiscal, el tipo de servicio y el monto.
    """

    def __init__(self, FiscalYear: str, ServiceDetailesType: str, amount: float) -> None:
        """
        Inicializa una nueva instancia de PendingPaidModel.

        Args:
            FiscalYear (str): El año fiscal del pago, en un formato como 'F24'.
            ServiceDetailesType (str): El tipo de servicio asociado al pago.
            amount (float): El monto del pago pendiente.
        """
        self.FiscalYear = FiscalYear
        self.ServiceDetailesType = ServiceDetailesType
        self.amount = amount

    def to_dict(self) -> dict[str, str | float]:
        """
        Convierte la instancia del modelo a un diccionario.

        Este método formatea el año fiscal de 'F24' a '2024' y retorna
        un diccionario con los datos del pago.

        Returns:
            dict[str, str | float]: Un diccionario con las claves "year", "serviceType"
                                    y "amount".
        """
        # Extrae los últimos dos dígitos del año fiscal (ej. '24' de 'F24').
        anio = self.FiscalYear[1:]

        # Concatena '20' para formar el año completo (ej. '2024').
        setting_year = f'20{anio}'
        return {
            "year": int(setting_year),
            "serviceType": self.ServiceDetailesType,
            "amount": self.amount
        }
    

class PendingPaidModel2:
    """
    Modelo de datos para representar un pago pendiente.

    Esta clase se utiliza para estructurar la información de pagos pendientes,
    incluyendo el año fiscal, el tipo de servicio y el monto.
    """

    def __init__(self, FiscalYear: str, ServiceName:str, ServiceDetailesType: str, amount: float) -> None:
        """
        Inicializa una nueva instancia de PendingPaidModel.

        Args:
            FiscalYear (str): El año fiscal del pago, en un formato como 'F24'.
            ServiceDetailesType (str): El tipo de servicio asociado al pago.
            amount (float): El monto del pago pendiente.
        """
        self.FiscalYear = FiscalYear
        self.ServiceName = ServiceName
        self.ServiceDetailesType = ServiceDetailesType
        self.amount = amount

    def to_dict(self) -> dict[str, str | float]:
        """
        Convierte la instancia del modelo a un diccionario.

        Este método formatea el año fiscal de 'F24' a '2024' y retorna
        un diccionario con los datos del pago.

        Returns:
            dict[str, str | float]: Un diccionario con las claves "year", "serviceType"
            y "amount".
        """
        # Extrae los últimos dos dígitos del año fiscal (ej. '24' de 'F24').
        anio = self.FiscalYear[1:]

        # Concatena '20' para formar el año completo (ej. '2024').
        setting_year = f'20{anio}'
        return {
            "year": int(setting_year),
            'ServiceName': self.ServiceName,
            "serviceType": self.ServiceDetailesType,
            "amount": self.amount
        }