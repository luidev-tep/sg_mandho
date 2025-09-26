from typing import Any

from src.dim_dates.dim_date import DIM_DATE    
from src.security.repository.user_info import get_user_info
from src.utils.id_generator import create_id


from functools import wraps
from flask import abort
from flask_jwt_extended import jwt_required, get_jwt, verify_jwt_in_request


from src.utils.validate_data import validate_data
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
                
                print('Year: ', year)
                print('Month: ', month)
                print('Day: ', day)
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
            
#Se ha puesto el decorador como como una funcion py no como un metodo para poder usarlo en cualquier blueprint


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
            print("Claims obtenidas del JWT:", claims) # Depuración: Muestra las claims obtenidas
            # Asume que el rol se guardó en la claim "role"
            user_role = claims.get('role', 'user') # Si no hay rol, asume 'user' [7]
            
            # Lógica de verificación: ¿El rol del usuario coincide con el rol requerido?
            if user_role != required_role:
                # Si el rol no coincide, se devuelve un error 403 (Prohibido) [6, 7]
                abort(403, description="Forbidden: Insufficient privileges")
            return fn(*args, **kwargs)
        return wrapper
    return decorator
