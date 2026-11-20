from typing import Any


class VistaModel:
    """
    Modelo de datos utilizado para representar un registro completo de la vista
    de seguridad (`SecurityUsers` view) en la base de datos.

    Esta clase actúa como un objeto de transferencia de datos (DTO) y es esencial
    para la autenticación, autorización y visualización de la información de los
    usuarios administradores (Delegados, Comitivas, Subdelegados) en el sistema.

    Cada instancia mapea las columnas del resultado de una consulta SQL,
    proporcionando acceso tipado y estructurado a los detalles del usuario
    y sus permisos de vigencia.

    Atributos:
        fullname (str): Nombre completo del administrador.
        username (str): Nombre de usuario utilizado para el inicio de sesión.
        password (str): Contraseña (generalmente hasheada) del usuario.
        RoleName (str): Rol o cargo asignado (ej. 'delegado', 'comitiva', 'subdelegado').
        ServiceName (str): Nombre del servicio/módulo asociado al rol (si aplica).
        CustomerFraction (str): Fracción o manzana del cliente (para roles como 'subdelegado').
        StatusName (str): Estado actual de la cuenta (ej. 'activo', 'inactivo').
        StartDate (str): Fecha de inicio de la vigencia del rol (YYYY-MM-DD).
        EndDate (str): Fecha de fin de la vigencia del rol (YYYY-MM-DD).
        DIM_ServiceOwnersId (str): ID único del registro del propietario de servicio.
        DIM_CustomerId (str): ID único del cliente maestro.
        DIM_AccountId (str): ID único de la cuenta de servicio (para control de acceso).
    """
    def __init__(self, 
        fullname: str,
        username: str,
        password: str,
        RoleName: str,
        ServiceName: str,
        CustomerFraction: str,
        StatusName: str,
        StartDate: str,
        EndDate: str,
        DIM_ServiceOwnersId: str,
        DIM_CustomerId: str,
        DIM_AccountId: str
    ) -> None:
        self.fullname = fullname
        self.username = username
        self.password = password
        self.RoleName = RoleName
        self.ServiceName = ServiceName
        self.CustomerFraction = CustomerFraction
        self.StatusName = StatusName        
        self.StartDate = StartDate
        self.EndDate = EndDate        
        self.DIM_ServiceOwnersId = DIM_ServiceOwnersId
        self.DIM_CustomerId = DIM_CustomerId
        self.DIM_AccountId = DIM_AccountId
    
    def to_dict(self) -> dict[str, str | Any]:
        return {
            "fullname": self.fullname,
            "username": self.username,
            "password": self.password, 
            "RoleName": self.RoleName,
            "ServiceName": self.ServiceName,
            "CustomerFraction": self.CustomerFraction,
            "StatusName": self.StatusName,
            "StartDate": self.StartDate,        
            "EndDate": self.EndDate,        
            "DIM_ServiceOwnersId": self.DIM_ServiceOwnersId,
            "DIM_CustomerId": self.DIM_CustomerId,
            "DIM_AccountId": self.DIM_AccountId
        }
