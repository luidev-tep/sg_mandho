class CheckListModel:
    """
    Modelo de datos para representar la información de un cliente en el sistema de check list.
    
    Esta clase define la estructura de datos para almacenar y manipular la información
    personal del cliente y sus identificadores únicos en el sistema.
    
    Attributes:
        CustomerName (str): Primer nombre del cliente.
        CustomerMiddleName (str): Segundo nombre del cliente.
        CustomerLastName (str): Primer apellido del cliente.
        CustomerSecondLastName (str): Segundo apellido del cliente.
        RoleName (str): Nombre del rol o perfil del cliente en el sistema.
        DIM_AccountId (str): Identificador único de la cuenta del cliente en la dimensión correspondiente.
        DIM_CustomerId (str): Identificador único del cliente en la dimensión correspondiente.
    
    Methods:
        to_dict(): Convierte la instancia del modelo a un diccionario para serialización.
    """
    
    def __init__(self, CustomerName: str, 
                 CustomerMiddleName: str, 
                 CustomerLastName: str, 
                 CustomerSecondLastName: str,
                 RoleName: str, 
                 DIM_AccountId: str,
                 DIM_CustomerId: str):
        """
        Inicializa una nueva instancia del modelo CheckListModel.
        
        Args:
            CustomerName (str): Primer nombre del cliente.
            CustomerMiddleName (str): Segundo nombre del cliente.
            CustomerLastName (str): Primer apellido del cliente.
            CustomerSecondLastName (str): Segundo apellido del cliente.
            RoleName (str): Nombre del rol o perfil del cliente.
            DIM_AccountId (str): Identificador único de la cuenta del cliente.
            DIM_CustomerId (str): Identificador único del cliente.
        """
        self.CustomerName = CustomerName
        self.CustomerMiddleName = CustomerMiddleName
        self.CustomerLastName = CustomerLastName
        self.CustomerSecondLastName = CustomerSecondLastName
        self.RoleName = RoleName
        self.DIM_AccountId = DIM_AccountId
        self.DIM_CustomerId = DIM_CustomerId
        
    def to_dict(self):
        """
        Convierte la instancia del modelo a un diccionario serializable.
        
        Returns:
            dict: Diccionario con todos los atributos del modelo como pares clave-valor.
                  Útil para conversión a JSON o para almacenamiento en bases de datos.
        
        Example:
            >>> cliente = CheckListModel("Juan", "Carlos", "Pérez", "Gómez", "Admin", "ACC123", "CUST456")
            >>> cliente.to_dict()
            {
                'CustomerName': 'Juan',
                'CustomerMiddleName': 'Carlos',
                'CustomerLastName': 'Pérez',
                'CustomerSecondLastName': 'Gómez',
                'RoleName': 'Admin',
                'DIM_AccountId': 'ACC123',
                'DIM_CustomerId': 'CUST456'
            }
        """
        return {
            "CustomerName": self.CustomerName,
            "CustomerMiddleName": self.CustomerMiddleName,
            "CustomerLastName": self.CustomerLastName,
            "CustomerSecondLastName": self.CustomerSecondLastName,
            "RoleName": self.RoleName,
            "DIM_AccountId": self.DIM_AccountId,
            "DIM_CustomerId": self.DIM_CustomerId
        }