import sqlite3
from src.utils.conexion import Conexion

from src.security.model import SecurytyModel, VistaModel

def get_user_info(username: str, RoleName: str, manzana: str, StartDate: str, EndDate: str)-> dict[str, str] | dict:
    """ 
    Funcion para optener la informacion de un usuario en especifico
    Args:
        username (str, optional): Id del usuario. Defaults to None.
    Returns:
        list: Con el registro encontrado o error en caso contrario
    """
    handlers = Conexion()
    query = """SELECT 
            *
            FROM
                SecurityUsers 
            WHERE  username = ? AND CustomerFraction = ? AND RoleName = ? AND StartDate = ? AND EndDate = ?"""
    try:
        handlers.cursor.execute(query, (username, manzana, RoleName,  StartDate, EndDate))
        user_info = handlers.cursor.fetchone()

        if user_info is None:
            return None
        
        user_format = VistaModel(*user_info).to_dict()
        
        return user_format
    except sqlite3.Error as e:
        print(f"Error al obtener la informacion del usuario: {e}")
        raise
    finally:
        handlers.close_conexion()


def insert_user_info(data_user: SecurytyModel)-> None:
    """
    FUNCION NO FUNCIONAL 
    Funcion para insertar la informacion de un usuario en especifico
    Args:
        id_user (str, optional): Id del usuario. Defaults to None.
    Returns:
        list: Con el registro encontrado o error en caso contrario
    """
    handlers = Conexion()

    query = """INSERT INTO SecurityUsers
    (
        SecurityUsersId,
         DIM_serviceOnwersId,
         username,
         password,
         Fraction,
         DIM_AccountId,
         StartDate,
         EndDate
    )
    VALUES
    (
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?,
        ?
    )"""
    values = (
        data_user.SecurityUsersId,
        data_user.DIM_serviceOnwersId,
        data_user.username,
        data_user.password,
        data_user.Fraction,
        data_user.DIM_AccountId,
        data_user.StartDate,
        data_user.EndDate
    )
    try:
        handlers.cursor.execute(query, (values))
        handlers.conn.commit()
        
    except sqlite3.Error as e:
        print(f"Error al insertar la informacion del usuario: {e}")
        raise
    finally:
        handlers.close_conexion()
