from src.utils.conexion import Conexion, DatabaseError
from src.users.models.user import User
from src.utils.id_generator import create_id


class Create():
    def insert_user(self, data: User) -> bool:
        """Método responsable de insertar un usuario a la base de datos
        
        Tabla: Table DIM_Customer {
            DIM_CustomerId uuid [pk]
            DIM_DateId uuid
            CustomerName varchar(50)
            CustomerMiddleName varchar(50)
            CustomerLastName varchar(50)
            CustomerSecondLastName varchar(50)
            CustomerAdress varchar(100)
            CustomerFraction varchar(50)
            CustomerPhone varchar(12)
            CustomerStartDate date
            CustomerEndDate date
            timestamp timestamp
        }

        Args:
            data (object): Instancia de la clase persona con los datos a insertar
            
        Returns:
            bool: True si se insertó correctamente, False si hubo error
        """
        object_conecction = Conexion()
        try:
            # Consulta con columnas explícitas (ajustadas al número correcto de parámetros)
            query = """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, 
                DIM_DateId, 
                CustomerName, 
                CustomerMiddleName,
                CustomerLastName, 
                CustomerSecondLastName, 
                CustomerDateBirth,
                CustomerStartDate, 
                CustomerEndDate, 
                CustomerFraction, 
                CustomerAddress, 
                CustomerNumberExt,
                username,   --Se agregaron los nuevos campos aqui.
                password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            #Se agregra el usuario y contrasenia de formaautomatica desde
            #aqui se debe dejar en cuenta que aqui se agregara esta parte
            #Para que en modificacione sposteriores se modifique aqui 

            passwonrd = create_id([data.CustomerDateBirth])  #Para el cumpleanios que sea su fecha haseada
            username = data.CustomerName
            values = (
                str(data.DIM_CustomerId),
                int(data.DIM_DateId),
                data.CustomerName,
                data.CustomerMiddleName,
                data.CustomerLastName,
                data.CustomerSecondLastName,
                data.CustomerDateBirth, 
                data.CustomerStartDate,
                data.CustomerEndDate,
                data.CustomerFraction,
                data.CustomerAddress,
                data.CustomerNumberExt,  # Agregado este campo que faltaba
                username,
                passwonrd
            )
            #print(f"Los valores que se agregaran a la base de datos son {values}")
            object_conecction.cursor.execute(query, values)
            
            object_conecction.save_changes()  # Comentado según lo indicado
            
            return True
        except DatabaseError as e:
            print(f"Error al insertar la persona: {e}")
            return False
        finally:
            object_conecction.close_conexion()
