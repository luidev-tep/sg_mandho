from typing import Any

class SecurytyModel:
    def __init__(self, SecurityUsersId: str, DIM_serviceOnwersId: str, username: str,
    password: str,
	Fraction: str,
    DIM_AccountId: str,
    StartDate: str,
    EndDate: str
        ) -> None:
        self.SecurityUsersId = SecurityUsersId
        self.DIM_serviceOnwersId = DIM_serviceOnwersId
        self.username = username
        self.password = password
        self.Fraction = Fraction
        self.DIM_AccountId = DIM_AccountId
        self.StartDate = StartDate
        self.EndDate = EndDate
        
    def to_dict(self) -> dict[str, str | Any]:
        return {
            "SecurityUsersId": self.SecurityUsersId,
            "DIM_serviceOnwersId": self.DIM_serviceOnwersId,
            "username": self.username,
            "password": self.password,
            "Fraction": self.Fraction,
            "DIM_AccountId": self.DIM_AccountId,
            "StartDate": self.StartDate,
            "EndDate": self.EndDate
        }



#MODIFICAR AQUI CUANDO SE AGREGREGE EL USUARIO Y LA CONTRASEÑA
#aL SERVICIO
class VistaModel:
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