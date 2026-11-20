# Importaciones generale sobre la parte de cuentas
from src.utils.conexion import Conexion
from src.utils.validate_data import validate_data
from src.dim_dates.dim_date import DIM_DATE
from src.utils.id_generator import create_id

# importaciones espeficias de insert_account
from src.accounts.repository.insert import insert
from src.accounts.services.validate import (
    validate_account,
    descativar_otra_cuenta,
    convertir_a_formato_legible,
    validate_status,
    has_active_account,
)
from src.accounts.models.DIM_account import DIM_Account
from src.dim_status.status import DIM_status

#Importaciones de mostrar o leer ceuntas
from src.accounts.repository.show import show_account

#importacion de roles 
from src.dim_roles.role import Role

#importacion de validaciones para saber si es administrador o usuario eliminado
from src.users.repository.delete import is_admin, defuncion_validation

#Validaciones de pagos se llaman aqui
from src.analytics_reports.Analitycs import Analitycs

#Manejadro de los roles para cuenta, ya que es a donde esta asociado
handler_role = Role()

class AccountCrud(): 
    """
    Clase la cual sera el metodo principal de la parte de cuentas
    contara con todas las funcionalides principales, ya sea crear, actualizar, leer, eliminar

    AUN SE DEBEN CORREGIR VARIOS ERRORES RELACIONADOS CON LA CUENTA Y LOS USUARIOS
    """
    def insert_account(self, account_json: dict, db: Conexion | None = None) -> tuple: 
        """
        Funcion la cual se encarga de la opcion create 
        Tiene todo lo nesesario, hace las validaciones, y si toda la informacion esta bien retorna 
        un 200 y mensaje de exito aqui se deben hacer 2 particones principales , primera es para poder crear el estado, el cual 
        se eligira por el usuario 

        Args:
            account_json (dict): Un diccionario que contiene la información del usuario.
            db (Conexion | None, optional): Conexión opcional para transacciones compartidas.

        Returns:
            int: Se retorna un codigo de error o exito
            str: Se retorna un string de error o exito especifico de que falto o si esta bien
        """
        
        # Validamos si el estatus es ativo
        campos = ["status", "customer_id", "start_date", "end_date"]
        tipo_campos = [str, str, str, str]
        
        resultado, mensaje = validate_data(account_json,campos, tipo_campos, "account")
        
        if not resultado:
            return 400, mensaje
        
        #SE 
        if is_admin(account_json["customer_id"]):
            return 403, "No se pueden editar los datos de un administrador"
        
        if not defuncion_validation(account_json["customer_id"]): #Para verificar si el usuario ya esta marcado como defuncion
            return 403, "No se pueden editar los datos de un usuario fallecido"
        
        
        valido = validate_account(account_json["customer_id"])
        #Asi se pued emanejar el caos de cuando una cuenta es creada por primera veez, se tienen que hacer todas las pruebas para verificar si una cuenta, puede
        #se cambiada cuando se pasan los filtro de validaciones
        if valido == 0:
            #print("Se hizo la priemra opcion")
            valido = True
        elif valido is False:
            #print("Se hizo la segunda opcion")
            return 404, "Este usuario ha sobrepasado el limite de cuentas"
        else:
            #print("Se hizo la tercera opcion")
            valido = True
            
            hanlder_analitycs = Analitycs()
            status, mensaje , pagos_gechoss = hanlder_analitycs.get_analytics_per_customer({'Dim_customerId':  account_json['customer_id']})
            #print(pagos_gechos_pendientes)
            if status != 200:
                return status, mensaje #No se pudo obtener la informaci
            
            #print(pagos_gechoss)
            pendientes = ''
            pagos_gechos_pendientes = pagos_gechoss['pendientes']

            if pagos_gechos_pendientes:
                claves = pagos_gechos_pendientes.keys()
                for comitiva in claves:

                    if pagos_gechos_pendientes[comitiva] == []:
                            continue
                    
                    for servicio in pagos_gechos_pendientes[comitiva]:
                        year = servicio['Year']
                        service_ype = servicio['ServiceDetailesType']
                        amount = servicio['amount']
                        fila = f'Año {year}:  \n'
                            
                            # Formato más legible y amigable
                        fila += f'  Servicio de {comitiva} - Tipo: {service_ype} - Debe: $ {amount}\n'
                        pendientes += fila
                if any(pagos_gechos_pendientes):
                    return 409, f"El usuario aun tiene pagos pendientes Antes de poder cambiarse de cuenta: \n {pendientes}"
        #return 200, "Esta prueba fue satisfactoria y "  

        #Creamos la instancia de clases que se ingresaran a la bd
        dim_date = DIM_DATE()
        
        # Se crea el rol asociado y se obtiene el id
        valid, dim_role_id, message = handler_role.insert_role(account_json) #Se manda todo el diccionario pero solo se utilizan algunos campos
        
        if not valid:
            print("Termino porque no era valido al insertr el rol")
            return 501, message
        
        #asi se desactivan las cuentas anteriores correctamente 
        if has_active_account(account_json["customer_id"]):
            descativar_otra_cuenta(account_json["customer_id"], db=db)
        
        #Estatus sera para ver si el pago ya esta pendiente o pagado, los roles seran los que tomaran la fucniona ctual de estatus
        estado = DIM_status()
        
        #Validaciones para ver si la cuenta debe ser activa u inactiva
        DIM_status_id = estado.get_status_id("","account")
        
        is_active, Status, EndDate = validate_status(account_json["status"])  
        #Si el estado que se ingresa es inactivo, se asigna el id del estado inactivo

        #En caso de no ser activas las variables se asignan como desactivadas
        if not is_active:
            status_id = Status
            account_json["end_date"] = EndDate
        else:
            status_id = DIM_status_id

        if estado and dim_date and valido:
            #Formatear el dim date para que la informacion sea correcta
            date = str(dim_date.dateId)[4:]
            account_data = {
                "DIM_AccountId": create_id([dim_role_id, account_json["customer_id"], date]),
                "DIM_DateId": dim_date.dateId, 
                "DIM_CustomerId": account_json["customer_id"],
                "DIM_RoleId": dim_role_id,
                "DIM_StatusId":  status_id, 
                "StartDate": account_json["start_date"],
                "EndDate": account_json["end_date"]
            }
            
            # Ingresar los datos a la base de datos 
            cuenta = DIM_Account(**account_data)
            
            request, message = insert(cuenta, db=db)
            # request, message = (True, 'Prueba de testeo para crear usuarios')
            
            if request:
                mensaje = "Cuenta creada con exito"
                return 200, mensaje
            else:
                return 501, f"Error inesperado: {message}"
        else:
            mensaje = "Termino por que estado no es activo, o dim_date no correcto o no es valido"
            print(mensaje)
            return 501, mensaje

        
        
    def read_account(self, persona_id: str = None) -> tuple[int, str, list]:
        """
        Esta función retorna información de cuentas. Puede manejar tres escenarios:
        1. Cuando no se proporciona ID (None) - Retorna todas las cuentas
        2. Cuando se proporciona un ID vacío ("") - Retorna todas las cuentas
        3. Cuando se proporciona un ID válido - Retorna información específica de esa cuenta

        La información se retorna en un formato legible para el cliente, donde los IDs
        son reemplazados por información descriptiva cuando es necesario.

        Args:
            persona_id (str, optional): El id de la cuenta que se desea mostrar. 
                                    Si es None o vacío (""), retorna todas las cuentas.
                                    Defaults to None.

        Returns:
            tuple: Contiene tres elementos:
                - int: Código de estado (200 para éxito, 400 para error)
                - str: Mensaje descriptivo del resultado
                - list: Lista de diccionarios con información de las cuentas, 
                        cada diccionario contiene:
                        {
                            "DIM_AccountId": str,  # ID de la cuenta
                            "DIM_DateId": str,     # Información legible de fecha
                            "customer_id": str,    # ID del cliente
                            "DIM_RoleId": str,     # Rol legible (ej: "Admin", "Usuario")
                            "DIM_StatusId": str,  # Estado legible (ej: "Activo", "Inactivo")
                            "startDate": str,      # Fecha de inicio en formato YYYY-MM-DD
                            "endDate": str,        # Fecha de fin en formato YYYY-MM-DD
                        }
                        
                        Si no se encuentran cuentas, retorna lista vacía []

        Ejemplo de retorno exitoso:
            (200, "Datos obtenidos correctamente", [
                {
                    "DIM_AccountId": "1qwger$whtwefa",
                    "DIM_DateId": "Enero 2022 - Diciembre 2022",
                    "customer_id": "weargsrheynbFGTGFHTWRg",
                    "DIM_RoleId": "Administrador",
                    "DIM_StatusId": "Activo",
                    "startDate": "2022-01-01", 
                    "endDate": "2022-12-31",
                }
                # ... más registros
            ])

        Ejemplo de error:
            (400, "No se encontraron cuentas", [])
        """
        campos_requeridos = ["id_user"]
        tipo_campos = [str]
        esvalido, mensaje = validate_data(persona_id, campos_requeridos, tipo_campos, "account")

        if esvalido:
            if persona_id['id_user']:
                # Caso: Mostrar cuenta específica
                
                datos = show_account(persona_id['id_user'])
                if datos:
                    # Aquí se transformarían los IDs a información legible
                    datos_legibles = convertir_a_formato_legible(datos)
                    #print("datos legibles", datos_legibles)
                    return 200, "Cuenta obtenida correctamente", datos_legibles
                else:
                    mensaje = "No se encontró la cuenta especificada"
                    return 404, mensaje, []
        else:
            return 400, mensaje, []
        
    
    def desactivate_account(self, persona_id: str, db: Conexion | None = None) -> None:
        """
        Esta función desactiva una cuenta en la base de datos.

        Args:
            persona_id (str): El id de la persona que se desea desactivar.
            db (Conexion | None, optional): Conexión de base de datos opcional para transacciones compartidas.

        Returns:
            None (NoneType): No responde nada solo hace una accion

        """
        descativar_otra_cuenta(persona_id, db=db)
