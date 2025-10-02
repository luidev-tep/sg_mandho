from typing import Any
import re


from src.dim_dates.dim_date import DIM_DATE    
from src.utils.id_generator import create_id

from functools import wraps
from flask import abort
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request

#Validacione spara ver si es correcto elegir al ussuario 
from src.utils.validate_data import validate_data, is_field_empty


#importaciones de eliminar 
from src.users.repository.delete import defuncion_validation, is_admin

from src.analytics_reports.Analitycs import Analitycs
hanlder_analitycs = Analitycs()

# Módulo de seguridad y permisos
from src.security.repository.user_info import (
    # Funciones de validación
    validate_user_admin,
    validate_user_module,
    validate_user_sub_admin,
    
    # Funciones de gestión de datos
    get_user_info,
    insert_onwer_info
)
from src.accounts.account import AccountCrud

hanlder_account = AccountCrud()

class SecurityUsers:
    def authenticate_user(self, data_user: dict[str, str]) -> tuple[int, str, dict | None]:
            """
            Metodo que funge de manejador de informacion, valida las credenciales del usuario.
            Compara las contraseñas hasheadas y retorna la informacion del usuario
            en caso de que sea correcta.

            Args:
                data_user (dict[str, str]): Diccionario con la informacion del usuario (username, password, etc.).

            Returns:
                tuple[int, str, dict | None]: Una tupla con (código_estado, mensaje, datos_del_usuario).
                
                IMPORTANTE lA CONTRASENIA QUE SE COMPARA ESTA HASHEADA, POR LO QUE SE TIENE QUE HASHEAR LA CONTRASENIA QUE SE ENVIA 
            """
            # CORRECCIÓN: Cambié el nombre de la variable 'fileds' a 'fields' (buena práctica).
            hanlder_date = DIM_DATE()
            fields = ['name', 'manzana', 'role', 'password']
            type_fields = [str, str, str, str]

            is_valid, message = validate_data(data_user, fields, type_fields, "security")
            if not is_valid:
                # NOTA: La función original retornaba 3 valores, mantenemos esa estructura.
                return 400, message, None
            
            try:
                #Siempre se buscaran registros del year Actual
                year, month, day = hanlder_date.full_date
                StartDate = f"{year}-01-01"
                EndDate = f"{year}-12-31"
                
                # print('Year: ', year)
                # print('Month: ', month)
                # print('Day: ', day)
                user = get_user_info(data_user['name'], data_user['role'], data_user['manzana'], StartDate, EndDate)
                
                
                if user is None:
                    print('User is None')
                    # Usamos un código 401 (Unauthorized) que es más apropiado para credenciales incorrectas.
                    return 401, "Datos incorrectos", None
                
                passwordDB = user['password']
                hash_password = create_id([data_user['password']]) # Suponiendo que create_id hashea la contraseña
                validacion1 = hash_password == passwordDB
                validacion2 = data_user['name'] == user['username']
                validacion4 = data_user['role'] == user['RoleName']
                if validacion1 and validacion2 and validacion4:
                    # Se remueve la contraseña del objeto que se retorna por seguridad.
                    del user['password']
                    del user['username']
                    del user['DIM_AccountId']
                    del user['DIM_CustomerId']
                    del user['StartDate']
                    del user['EndDate']
                    del user['StatusName']
                    return 200, "Usuario validado correctamente", user
                else:
                    return 401, "Datos incorrectos", None
                
            except Exception as e:
                print(e)
                return 500, str(e), None
            
    def insert_new_Onwer(self, data_json: dict[str, str]) -> tuple[int, str]:
        """
        Función principal de flujo de trabajo para la creación y asignación de un nuevo
        usuario administrador (Propietario/Owner) en el sistema.

        Este proceso es **transaccional** y crítico para la seguridad. Debe ser protegido
        fuertemente, ya que maneja la creación de cuentas con altos privilegios.

        ### Flujo de Tareas:

        1.  **Validación de Formato de Entrada:**
            Asegura que todos los campos requeridos (`DIM_CustomerId`, `CustomerFraction`,
            `username`, `password`, `RoleName`, `serviceName`) existan y sean del tipo correcto (`str`).

        2.  **Validación de Elegibilidad del Cliente (`validate_user_chosen`):**
            Verifica que el cliente seleccionado (por `DIM_CustomerId`) cumpla con todos
            los requisitos de elegibilidad:
            -   **No ser Administrador** activo actualmente.
            -   **No estar marcado como defunción.**
            -   **No tener pagos o adeudos pendientes** de servicios.

        3.  **Validación de Coherencia y Unicidad del Rol (`validate_user_post`):**
            Verifica que el rol (`RoleName`) y su contexto (`CustomerFraction`/`serviceName`)
            sean válidos y que no exista ya un administrador activo para ese rol/área,
            según las reglas de negocio (ej. solo un delegado por año, uno por comitiva/servicio, etc.).

        4.  **Validación de Robustez de Contraseña (`validate_password_with_feedback`):**
            Aplica validaciones estrictas (longitud, complejidad, caracteres especiales) a
            la contraseña proporcionada por el usuario.

        5.  **Proceso de Transacción (Creación de Cuenta):**
            -   **Hasheo:** La contraseña se hashea antes de su almacenamiento para garantizar la seguridad.
            -   **Fechas de Vigencia:** La cuenta del nuevo administrador se crea con una
                fecha de inicio (`StartDate`) y una fecha de fin (`EndDate`) definidas,
                establecidas para el año actual (ej. 01-01 al 12-31 del año en curso).
            -   **Registro:** Inserta el nuevo registro en la tabla de Propietarios/Owners,
                lo que lo hace visible para la vista de seguridad y le permite iniciar sesión
                en el sistema con el rol asignado (`RoleName`).
            -   **Desactivación (Pendiente):** La lógica requiere que la cuenta anterior
                del cliente se desactive (si aplica), aunque el código está comentado
                (`hanlder_account.desactivate_account`).
            -   **Rollback:** Si cualquier paso dentro del `try...except` falla, la transacción
                debe deshacerse para prevenir estados parciales e inconsistentes en la base de datos.

        Args:
            data_json (dict[str, str]): Diccionario que contiene los datos necesarios para la creación
                                        del administrador.

        Returns:
            tuple[int, str]: Una tupla con el código de estado HTTP y un mensaje:
                - (201, message): Si el nuevo administrador se insertó correctamente.
                - (400, message): Si fallan las validaciones de datos o de contraseña.
                - (409, message): Si falla la validación de elegibilidad o unicidad del rol.
                - (500, message): Si ocurre un error inesperado durante la transacción de la base de datos.
        """
        fields = ['DIM_CustomerId', 'CustomerFraction', 'username', 'password', 'RoleName', 'serviceName']
        type_fields = [str, str, str, str, str, str]
        is_valid, message = validate_data(data_json, fields, type_fields, "security")
        if not is_valid:
            # NOTA: La función original retornaba 3 valores, mantenemos esa estructura.
            return 400, message
        
        #Validar al usuario primero
        status, mensaje = self.validate_user_chosen(data_json['DIM_CustomerId'])

        if status != 200:
            return status, mensaje
        is_valid, mensaje = is_field_empty(data_json)
        if not is_valid:
            return 400, mensaje
        
        #Validar el rol que se intenta Agregar
        data_for_post = {'RoleName': data_json['RoleName'], 'CustomerFraction': data_json['CustomerFraction'], 'serviceName': data_json['serviceName']}
        status, mensaje = self.validate_user_post(data_for_post)
        print(f"Paso la validacion de puesto")
        if status != 200:
            return status, mensaje
        
        #Cuando ya se hayan pasado todas las validaciones ahora si se puede hacer la transaccion para agregar el nuevo ususario al sistema
        hanlder_date = DIM_DATE()

        #Hashear la contrasenia
        is_valid, message = self.validate_password_with_feedback(data_json['password'])

        if not is_valid:
            print(f"La constrasenia fallo por {message}")
            return 400, message
        
        hash_password = create_id([data_json['password']]) # Suponiendo que create

        year, month, day = hanlder_date.full_date
        StartDate = f"{year}-01-01"
        EndDate = f"{year}-12-31"
        
        try:
            #Desactivar la cuenta actual para agregar la cuenta de Propietario
            #hanlder_account.desactivate_account(data_json['DIM_CustomerId'])
            data_to_insert = {
                'DIM_CustomerId': data_json['DIM_CustomerId'],
                'CustomerFraction': data_json['CustomerFraction'],
                'username': data_json['username'],
                'password': hash_password,
                'RoleName': data_json['RoleName'],
                'serviceName': data_json['serviceName'],
                'StartDate': StartDate,
                'EndDate': EndDate
            }
            estado, mensaje = insert_onwer_info(data_to_insert)
            if estado != 200:
                return estado, mensaje
            #Activar la cuenta de Propietario
            return 201, "Usuario Propietario insertado correctamente y cuenta."
        except Exception as e:           
            print(e)
            return 500, str(e)
        
    def validate_user_chosen(self, dim_customerId: str):  # -> tuple[Literal[400], Any] | tuple[Literal[403], Literal['N...:
        """
        Aplica un conjunto de validaciones de negocio y estado antes de que un cliente
        pueda ser seleccionado y propuesto como un nuevo usuario administrador (Admin).

        Esta función asegura la **elegibilidad** del candidato basada en:
        1.  **Formato de Entrada:** Valida que el `dim_customerId` sea un string válido.
        2.  **Unicidad de Administrador:** Verifica que el cliente **no sea ya un administrador** activo en el sistema (`is_admin()`).
        3.  **Estado de Defunción:** Confirma que el cliente no esté marcado como fallecido en los registros (`defuncion_validation()`).
        4.  **Estado de Pagos:** Consulta los servicios pendientes de pago del cliente a través del módulo de analíticas. Un cliente **no puede ser seleccionado** si tiene pagos o adeudos pendientes.

        Esta validación es crítica para mantener la integridad de los datos de administración
        y la elegibilidad de los líderes seleccionados.

        Args:
            dim_customerId (str): Identificador único del cliente (Customer ID) a validar.

        Returns:
            tuple[int, str]: Una tupla con el código de estado HTTP y un mensaje descriptivo:
                - (200, "Usuario completamente elegible"): Si el cliente pasa todas las validaciones.
                - (400, message): Si el formato del `dim_customerId` es incorrecto.
                - (403, "No se agregar a un administrador dos veces !"): Si el cliente ya es administrador.
                - (403, "No se pueden agregar a un administrador fallecido"): Si el cliente está marcado como defunción.
                - (404, message): Si no se puede recuperar la información analítica del usuario (ej. usuario no existe).
                - (409, message): Si el cliente tiene pagos pendientes, listando los servicios adeudados.
        """
        fields = ['DIM_CustomerId']
        type_fields = [str]
        data_format = {'DIM_CustomerId':dim_customerId}
        is_valid, message = validate_data(data_format, fields, type_fields, "security")
        if not is_valid:
            # NOTA: La función original retornaba 3 valores, mantenemos esa estructura.
            return 400, message
        
        if is_admin(dim_customerId):
            return 403, "No se agregar a un administrador dos veces !"
        
        if not defuncion_validation(dim_customerId): #Para verificar si el usuario ya esta marcado como defuncion
            return 403, "No se pueden agregar a un administrador fallecido"
        
        result = hanlder_analitycs.get_analytics_per_customer({"Dim_customerId": dim_customerId})
        #print(result)
        if result[0] != 200:
            return 404, 'No se pudo obtener la informacion del usuario'
        pendientes = ''
        service_name = list(result[2]['pendientes'].keys())
        pendientes_paids = result[2]['pendientes']
        for service in service_name:
            fila = f'Servicio: {service}\n'
            for registro in pendientes_paids[service]:
                year = registro['Year']
                servicesDetailesType = registro['ServiceDetailesType']
                amount = registro['amount']
                
                # Formato más legible y amigable
                fila += f'Año: {year}  Servicio de {servicesDetailesType} - Debe: $ {amount}\n'
                pendientes += fila
                fila = ''
        
        if any(pendientes):
            return 409, f"El usuario aun tiene pagos pendientes: \n {pendientes}"
        
        return 200, "Usuario completamente elegible"

    def validate_user_post(self, data_json: dict[str, Any]) -> tuple[int, str]:
        """
        Realiza la validación de negocio y de existencia para la creación de un nuevo
        usuario administrador (delegado, comitiva, subdelegado) antes de su registro
        en el sistema.

        Esta función garantiza que solo se pueda asignar un único rol/servicio/fracción
        cuando el tipo de rol lo requiera (validación de unicidad) y que la combinación
        de rol y servicio/fracción sea coherente con la lógica de negocio predefinida.

        ### Roles y Reglas de Unicidad
        La función verifica la disponibilidad del cargo para mantener la unicidad:

        1.  **'delegado'**: Solo puede existir **uno** activo en el sistema (`validate_user_admin()`).
        2.  **'comitiva'**: Solo puede existir **uno** activo por `serviceName` (`validate_user_module(service_name)`).
        3.  **'subdelegado'**: Solo puede existir **uno** activo por `CustomerFraction` (`validate_user_sub_admin(fraction)`).

        ### Validación de Coherencia de Datos
        Se valida que la estructura de `data_json` contenga y respete los siguientes campos obligatorios:
        -   `RoleName` (str): El tipo de cargo a asignar ('delegado', 'comitiva', 'subdelegado').
        -   `CustomerFraction` (str): La fracción o manzana del cliente (obligatorio para 'subdelegado').
        -   `serviceName` (str): El nombre del servicio/módulo (obligatorio para 'delegado' y 'comitiva').

        La combinación de `RoleName` y `serviceName` o `CustomerFraction` debe estar
        presente en el diccionario `validaciones` para ser considerada válida.

        Args:
            data_json (dict[str, Any]): Diccionario con los datos del nuevo usuario a crear,
                                        incluyendo 'RoleName', 'CustomerFraction', y 'serviceName'.

        Returns:
            tuple[int, str]: Una tupla con el código de estado HTTP y un mensaje:
                - (200, "Validación exitosa"): Si todos los campos son válidos y el cargo está disponible.
                - (400, message): Si falta algún campo obligatorio o hay un error de tipo de datos.
                - (409, message): Si el cargo ya está ocupado (violación de unicidad) o la combinación
                  de rol/servicio/fracción es incoherente con las reglas de negocio.
        """
        fields = ['RoleName', 'CustomerFraction', 'serviceName']
        type_fields = [str, str, str]
        is_valid, message = validate_data(data_json, fields, type_fields, "security")
        if not is_valid:
            # NOTA: La función original retornaba 3 valores, mantenemos esa estructura.
            return 400, message
        
        #Validacion si el servicio existe
        #Validacion oara que los cargos que se introduzcan sean coherentes
        validaciones = {
            'delegado': {'delegado'},
            'comitiva': {'feria', 'delegacion', 'panteon', 'agua'},
            'subdelegado': {'personas'}
        }
        role = data_json.get('RoleName', '')
        if not role:
            return 400, "El campo 'RoleName' es obligatorio y debe ser una cadena de texto."
        
        if role == 'delegado':
            if not validate_user_admin():
                return 409, "Ya existe un delegado activo en el sistema"
            if data_json['serviceName'] not in validaciones['delegado']:
                return 409, f"No se puede agregar un delegado para el servicio de  {data_json['serviceName']}"
        
        if role == 'comitiva':
            service_name = data_json['serviceName']
            if not validate_user_module(service_name):
                return 409, f"Ya existe un usuario activo en el sistema para el modulo {service_name}"
            
            if data_json['serviceName'] not in validaciones['comitiva']:
                return 409, f"No se puede agregar un comitiva para el servicio de  {data_json['serviceName']}"
        
        if role == 'subdelegado':
            fraction = data_json['CustomerFraction']
            if not validate_user_sub_admin(fraction):
                return 409, f"Ya existe un usuario activo en el sistema para la manzana de  {fraction}"
            
            if data_json['CustomerFraction'] not in validaciones['subdelegado']:
                return 409, f"No se puede agregar un subdelegado para la manzana de  {data_json['CustomerFraction']}"
        
        return 200, "Validación exitosa"
#Se ha puesto el decorador como como una funcion py no como un metodo para poder usarlo en cualquier blueprint

    def validate_password_with_feedback(self, password: str) -> dict:
        """
        Valida la robustez y formato de una contraseña proporcionada, retornando
        información detallada sobre las fallas de validación.

        Esta función está diseñada para ser utilizada en el proceso de creación o
        actualización de contraseñas de usuarios, especialmente para roles críticos
        como **Administradores (Admins)** o **Propietarios**, asegurando
        un alto nivel de seguridad.

        Las reglas de validación aplicadas son las siguientes:
        1. **No Vacía:** La contraseña no debe ser nula o una cadena vacía.
        2. **Longitud Mínima:** Debe tener al menos 8 caracteres.
        3. **Sin Espacios:** No debe contener caracteres de espacio.
        4. **Minúsculas:** Debe contener al menos una letra minúscula (`[a-z]`).
        5. **Mayúsculas:** Debe contener al menos una letra mayúscula (`[A-Z]`).
        6. **Dígito:** Debe contener al menos un número (`\d`).
        7. **Carácter Especial:** Debe contener al menos un carácter especial
           de la siguiente lista: `!@#$%^&*()_+-=[]{}|;:,.<>?`.

        Args:
            password (str): La cadena de la contraseña a validar.

        Returns:
            dict: Un diccionario con el resultado de la validación:
                - 'is_valid' (bool): `True` si la contraseña cumple con todas las reglas, `False` en caso contrario.
                - 'errors' (str): Una cadena de texto que contiene todos los mensajes de error
                  concatenados y separados por un espacio, indicando qué reglas se incumplieron.
                  Si 'is_valid' es `True`, esta cadena estará vacía.
        """
        errors = []
        
        # Validar que la contraseña no sea None o vacía
        if not password:
            errors.append("La contraseña no puede estar vacía")
            return {'is_valid': False, 'errors': errors}
        
        if len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")
        
        if ' ' in password:
            errors.append("La contraseña no puede contener espacios")
        
        if not re.search(r'[a-z]', password):
            errors.append("Debe contener al menos una letra minúscula")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Debe contener al menos una letra mayúscula")
        
        if not re.search(r'\d', password):
            errors.append("Debe contener al menos un dígito")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
            errors.append("Debe contener al menos un carácter especial (!@#$%^&* etc.)")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': ' '.join(errors)
        }

def role_required(required_role) :#-> Callable[..., _Wrapped[Callable[..., Any], Any, Callable[...:
    # Definición del decorador externo que acepta el rol requerido
    def decorator(fn):
        @wraps(fn)
        # Se asegura de que el JWT esté presente y sea válido
        @jwt_required() 
        def wrapper(*args, **kwargs):
            # Obtiene todas las claims (el payload decodificado) del token JWT actual
            verify_jwt_in_request() # Verifica la presencia del JWT [6]
            claims = get_jwt() # Obtiene las claims del token [7, 15]
            #print("Claims obtenidas del JWT:", claims) # Depuración: Muestra las claims obtenidas
            # Asume que el rol se guardó en la claim "role"
            user_role = claims.get('role', 'user') # Si no hay rol, asume 'user' [7]
            #print(f"El rol del usuario es: {user_role} se va a comparar con el rol requerido: {required_role == user_role}")
            # Lógica de verificación: ¿El rol del usuario coincide con el rol requerido?
            if user_role != required_role:
                # Si el rol no coincide, se devuelve un error 403 (Prohibido) [6, 7]
                abort(403, description="Forbidden: Insufficient privileges")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
