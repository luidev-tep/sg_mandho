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
                DIM_DateId: int,
                FACT_RevenueId: int,
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
            "DIM_DateId": self.get_date(DIM_DateId),
            "FACT_RevenueId": FACT_RevenueId,
            "DIM_AccountId": DIM_AccountId
        }

        return datos

    def get_date(self, DIM_DateId: int) -> str:
        handler_date = DIM_DATE()

        fecha = handler_date.get_by_id(DIM_DateId)

        
        if not fecha:
            return "sin fecha proporcionada"
        return f"{fecha.Day}/{fecha.Month}/{fecha.Year}"


