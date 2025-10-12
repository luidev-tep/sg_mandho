from src.dim_dates.dim_date import DIM_DATE

class VistaModel:
    
    def build_vista(self, 
                CustomerName: str,
                CustomerMiddleName: str, 
                CustomerLastName: str, 
                CustomerSecondLastName: str,
                RoleName: str,
                StatusCuenta: str,
                StatusFactura: str,
                ServiceDetailesType: str,
                amount: float,
                YearPay: int,
                DIM_AccountId: str,
                DIM_CustomerId: str) -> bool:
        """
        Crea una vista específica para un tipo de servicio con todas las columnas necesarias.
        
        Args:
            CustomerName (str): Nombre del cliente
            CustomerMiddleName (str): Segundo nombre del cliente
            CustomerLastName (str): Apellido paterno del cliente
            CustomerSecondLastName (str): Apellido materno del cliente
            RoleName (str): Nombre del rol del usuario
            ServiceDetailesType (str): Tipo de detalle del servicio (Se espeficia que tipo de servicio esta pagando),
            StatusCuenta (str): Estado de la cuenta
            StatusFactura (str): Estado de la factura
            ServiceDetailesType (str): Tipo de detalle del servicio
            amount (float): Monto del pago
            DIM_DateId (int): ID de la fecha
            FACT_RevenueId (str): ID de la factura de revenue
            DIM_AccountId(str): ID de la cuenta Asociada
        
        Returns:
            dict: Se retornada un diccionario con la informacion formateada
        """
        #creamos el diccionario faormateado
        datos = {
            "CustomerName": CustomerName,
            "CustomerMiddleName": CustomerMiddleName,
            "CustomerLastName": CustomerLastName,
            "CustomerSecondLastName": CustomerSecondLastName,
            "RoleName": RoleName,
            "StatusCuenta": StatusCuenta,
            "StatusFactura": StatusFactura,
            "ServiceDetailesType": ServiceDetailesType,
            "amount": amount,
            "YearPay": YearPay,
            "DIM_CustomerId": DIM_CustomerId,
            "DIM_AccountId": DIM_AccountId
        }

        return datos

    def get_date(self, DIM_DateId: int) -> str:
        handler_date = DIM_DATE()

        fecha = handler_date.get_by_id(DIM_DateId)

        
        if not fecha:
            return "sin fecha proporcionada"
        return f"{fecha.Day}/{fecha.Month}/{fecha.Year}"
    
    def Buid_vista_by_customer(self,
                CustomerName: str,
                CustomerMiddleName: str, 
                CustomerLastName: str, 
                CustomerSecondLastName: str,
                StatusFactura: str,
                amount: float,
                DIM_DateId: str,
                DIM_AccountId: str,
                FACT_RevenueId: str
                ) -> dict:
        """
        Construye una vista específica para un cliente con todas las columnas necesarias.
        
        Esta función toma los parámetros del cliente y los datos de facturación para crear
        un diccionario estructurado que representa la vista del cliente con información
        completa de identificación y estado de facturación.
        
        Parameters:
            CustomerName (str): Nombre principal del cliente.
            CustomerMiddleName (str): Segundo nombre del cliente.
            CustomerLastName (str): Apellido paterno del cliente.
            CustomerSecondLastName (str): Apellido materno del cliente.
            StatusFactura (str): Estado actual de la factura (ej: Pagada, Pendiente, Vencida).
            amount (float): Monto total del pago asociado a la factura.
            FACT_RevenueId (str): Identificador único de la factura de revenue.
            DDIM_DateId (str): Identificador único de la fecha en la dimensión de fechas.
        
        Returns:
            dict: Diccionario estructurado con toda la información del cliente y facturación,
                utilizando los mismos nombres de parámetros como claves.
        
        Example:
            >>> Buid_vista_by_customer(
            ...     "Juan", "Carlos", "Pérez", "Gómez", 
            ...     "Pagada", 1500.0, "cust_123", "rev_456", "date_789"
            ... )
            {
                'CustomerName': 'Juan',
                'CustomerMiddleName': 'Carlos',
                'CustomerLastName': 'Pérez',
                'CustomerSecondLastName': 'Gómez',
                'StatusFactura': 'Pagada',
                'amount': 1500.0,
                'FACT_RevenueId': 'rev_456',
                'DIM_DateId': 'date_789'
            }
        """
        
        # Creamos el diccionario formateado con los mismos nombres de parámetros
        datos = {
            "CustomerName": CustomerName,
            "CustomerMiddleName": CustomerMiddleName,
            "CustomerLastName": CustomerLastName,
            "CustomerSecondLastName": CustomerSecondLastName,
            "StatusFactura": StatusFactura,
            "amount": amount,
            "FACT_RevenueId": FACT_RevenueId,
            "DIM_DateId": self.get_date(DIM_DateId) ,# Vienen como 2023/04/12
            "DIM_AccountId": DIM_AccountId
        }
        #print(datos)

        return datos