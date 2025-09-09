class AnalythicsModels:
    """
    Clase que contiene modelos de datos para formatear la información
    obtenida de la base de datos de manera que sea compatible con
    los requisitos del frontend.
    """
    def model_get_revenues_per_month(self, year: str, month: str, revenues: float) -> dict:
        """
        Modela los datos de ingresos mensuales para su presentación en el frontend.

        Formatea los valores de año y mes para generar una cadena con el formato
        'MM-YYYY' y asocia el monto de ingresos correspondiente.

        Args:
            year (str): El año fiscal en formato de cadena (e.g., 'Y24').
            month (str): El mes fiscal en formato de cadena (e.g., 'M03').
            revenues (float): El monto total de ingresos para ese mes.

        Returns:
            dict: Un diccionario con las claves 'month' (mes formateado)
                  y 'amount' (ingresos).
        """
        return {
            'month': f'{month[-2:]}-20{year[-2:]}',
            'amount': revenues
        }
    
    def model_get_amount_per_fraction(self, CustomerFraction: str, revenue: float) -> dict:
        """
        Modela los datos de ingresos por fracción para su presentación en el frontend.

        Args:
            CustomerFraction (str): El nombre de la fracción o manzana del cliente.
            revenue (float): El monto total de ingresos para esa fracción.

        Returns:
            dict: Un diccionario con las claves 'fraction' (nombre de la fracción)
                  y 'revenue' (ingresos).
        """
        return {
            'fraction': CustomerFraction,
            'revenue': revenue
        }