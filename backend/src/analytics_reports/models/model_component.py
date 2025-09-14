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
    
    def model_get_population(self, CustomerFraction, n_customers) -> dict:
        """
        Modela los datos de población por fracción para su presentación en el frontend.

        Args:
            CustomerFraction (str): El nombre de la fracción o manzana del cliente.
            n_customers (int): La cantidad de clientes en esa fracción.

        Returns:
            dict: Un diccionario con las claves 'fraction' (nombre de la fracción)
                  y 'population' (población).
        """
        return {
            'fraction': CustomerFraction,
            'population': n_customers
        }


    def model_get_bill_payments(self, nombre: str, personas:str, pagados:int, pendientes:int, porcentaje:float) -> dict:
        """
        Modela los datos de pagos de facturas para su presentación en el frontend.

        Args:
            month (str): El mes fiscal en formato de cadena (e.g., 'M03').
            year (str): El año fiscal en formato de cadena (e.g., 'Y24').
            amount (float): El monto total de pagos de facturas para ese mes.

        Returns:
            dict: Un diccionario con las claves 'month' (mes formateado)
                  y 'amount' (pagos de facturas).
        """
        return {
            'nombre': nombre,
            'personas': personas,
            'pagados': pagados,
            'pendientes': pendientes,
            'porcentaje': porcentaje
            }