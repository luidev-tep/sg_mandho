import sqlite3
from src.dim_dates.dim_date import DIM_DATE
from src.utils.conexion import Conexion


def set_defuncion(DIM_CustomerId) :
    """Funcion la cual se encarga de hacer la actualizacion de la informacion de la persona
    escribiendo una fecha de defuncion en la base de datos
    
    Argsd:
        DIM_CustomerId (str): Identificador unico del usuario
    """
    hander_date = DIM_DATE()
    hancer_coencction = Conexion()
    try:
        fecha_defuncion = hander_date.get_end_date()

        query = """UPDATE DIM_Customer 
        SET CustomerEndDate = ? 
        WHERE DIM_CustomerId = ?"""
        hancer_coencction.cursor.execute(query, (fecha_defuncion, DIM_CustomerId))
        hancer_coencction.save_changes()
    except sqlite3.Error as e:
        print(f"Error al actualizar la informacion de la persona: {e}")
    finally:
        hancer_coencction.close_conexion()


def defuncion_validation(DIM_CustomerId) -> bool: 
    """Funcion la cual verifica si el ususario que se esta ingresando sea valido para marcar como defuncion

    Args:
        DIM_CustomerId (str): Identificador unico del usuario

    Returns:
        bool: retorna true si el ususario es valido para marcar como defuncion, si no retorna false
    """
    handler_coencction = Conexion()
    try:
        query = f"SELECT CustomerEndDate FROM DIM_Customer WHERE DIM_CustomerId = ?"

        handler_coencction.cursor.execute(query, (DIM_CustomerId,))
        result = handler_coencction.cursor.fetchone()
        
        if result[0] == "s/n" or result is None:
            # print("El usuario es valido para marcar como defuncion")
            # print(result[0])
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Error al verificar la informacion de la persona: {e}")
        return False
    finally:
        handler_coencction.close_conexion()



def is_admin(DIM_CustomerId) -> bool:
    """Funcion la cual se encarga de verificar si el usuario a marcqr como fallecido es administrador"""
    handler_connection = Conexion()
    try:
        query = """SELECT r.RoleType 
            from DIM_Role as r
            JOIN DIM_Account as a on	
            r.DIM_RoleId = a.DIM_RoleId
            JOIN DIM_Status as st on
            st.DIM_StatusId = a.DIM_StatusId
            and st.StatusName = 'activo'
            WHERE  a.DIM_CustomerId = ?
            """
        
        handler_connection.cursor.execute(query, (DIM_CustomerId,))
        tipo_rol = handler_connection.cursor.fetchone()

        if tipo_rol is None:
            print("No se encontro informacion en la consulta")
            return False
        elif tipo_rol[0] == "administrador":
            return True
        else:
            return False
    except sqlite3.Error as e:
        print(f"Error al verificar la informacion de la persona: {e}")
        return False
    finally:
        handler_connection.close_conexion()
