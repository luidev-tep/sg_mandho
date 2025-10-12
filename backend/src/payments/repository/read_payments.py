import sqlite3
from src.utils.conexion import Conexion
from src.utils.build_filters import BuildFilters
from typing import Any
from src.payments.model.vista_model import VistaModel

handler_vista = VistaModel()

class ReadPayment:
    """
    Clase para la lectura de datos de pagos.

    Esta clase maneja la lógica para consultar y recuperar registros
    de pagos desde una base de datos SQLite, utilizando diferentes
    vistas según el tipo de servicio.
    """

    def __init__(self):
        """
        Inicializa las consultas base para cada tipo de servicio de pago.

        Las vistas disponibles son:
        - VISTA_PAGOS_AGUA
        - VISTA_PAGOS_FERIA
        - VISTA_PAGOS_PANTEON
        - VISTA_PAGOS_DELEGACION


        """
        self.__Query_base = """      
        SELECT
        vw.CustomerName,
        vw.CustomerMiddleName,
        vw.CustomerLastName,
        vw.CustomerSecondLastName,
        vw.RoleName,
        vw.StatusCuenta,
        vw.StatusFactura,
        vw.ServiceDetailesType,
        amount,
        vw.YearPay,
        vw.DIM_AccountId,
        vw.DIM_CustomerId
        FROM [tabla] as vw

        [filtros]
        """

        self.agua = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_AGUA")
        self.feria = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_FERIA")
        self.panteon = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_PANTEON")
        self.delegacion = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_DELEGACION")

    def _obtener_query(self, servicename: str) -> str:
        """
        Obtiene la consulta SQL base según el nombre del servicio.

        Args:
            servicename (str): El nombre del servicio (por ejemplo, 'agua', 'feria', etc.).

        Returns:
            str: La consulta SQL base correspondiente al servicio.
                 Retorna una cadena vacía si el servicio no es reconocido.
        """
        if servicename == 'agua':
            return self.agua
        elif servicename == 'feria':
            return self.feria
        elif servicename == 'panteon':
            return self.panteon
        elif servicename == 'delegacion':
            return self.delegacion
        else:
            return ""

    def get_payments_by_service(self, service: str, filters: dict) -> tuple[int, list[dict]]:
        """
        Obtiene los pagos de un servicio específico.

        Esta función selecciona la vista de pagos adecuada según el nombre del servicio
        proporcionado y ejecuta una consulta para recuperar todos los registros
        relacionados.

        Args:
            service (str): El nombre del servicio (por ejemplo, 'agua', 'feria', etc.)
                           para el cual se quieren obtener los pagos.
            filters (dict): Un diccionario opcional con filtros, como 'DIM_CustomerId', 'ServiceDatailesType' y 'YearPay'.

        Returns:
            tuple[int, list[dict]]: Una tupla que contiene:
                                    - Un código de estado HTTP (200, 400, 500).
                                    - Una lista de diccionarios, donde cada diccionario representa
                                      un registro de pago. La lista estará vacía si ocurre un error
                                      o no se encuentra el servicio.
        """
        hanlder_conexion = Conexion()
        
        try:
            # Obtenemos la consulta SQL base
            query = self._obtener_query(service)

            if not query:
                # Si el servicio no es reconocido, retornamos un código 400 (Bad Request)
                return 400, []
            
            if filters:
                values = list()
                query_filtros = """
                    WHERE DIM_CustomerId = ?
                    and ServiceDetailesType = ?
                    and YearPay = ?"""
                
                values.append(filters['DIM_CustomerId'])
                values.append(filters['ServiceDetailesType'])
                values.append(filters['YearPay'])
                query = query.replace("[filtros]", query_filtros)

                                 # Ejecutamos la consulta
                #print(query)
                #print(values)
                hanlder_conexion.cursor.execute(query, tuple(values))
            else:
                query = query.replace("[filtros]", "")
                hanlder_conexion.cursor.execute(query)
            
            rows = hanlder_conexion.cursor.fetchall()

            # Construimos los datos utilizando el modelo de vista
            datos = [handler_vista.build_vista(*row) for row in rows if row]  # Usamos unpacking para pasar los valores

            return 200, datos

        except sqlite3.Error as e:
            # En caso de un error con la base de datos, retornamos un código 500 (Internal Server Error)
            print(f"Error de base de datos: {e}")
            return 500, []
        finally:
            # Aseguramos que la conexión se cierre
            hanlder_conexion.close_conexion()

    def get_payments_with_filters(self, service_name: str, filters: dict) -> tuple[int, list[dict]]:
        """
        Obtiene los pagos aplicando filtros específicos al servicio seleccionado.

        Este método permite filtrar los resultados de los pagos mediante un conjunto de criterios
        definidos por el usuario. Estos filtros pueden incluir el año fiscal, la fracción de cliente,
        el estado del pago, entre otros.

        Args:
            service_name (str): Nombre del servicio para determinar la vista a consultar (por ejemplo, 'agua').
            filters (dict): Diccionario con los filtros a aplicar en la consulta. Los filtros pueden
                            incluir atributos como 'DIM_Date', 'CustomerFraction', 'DIM_StatusId', etc.

        Returns:
            tuple[int, list[dict]]: Una tupla que contiene:
                                    - Un código de estado HTTP (200, 400, 500).
                                    - Una lista de diccionarios, donde cada diccionario representa
                                      un registro de pago filtrado. La lista estará vacía si ocurre
                                      un error o no se encuentran resultados.
        """
        object_conection = Conexion()
        handler_filters = BuildFilters()
        query_base = self._obtener_query(service_name)
        query_filtros = ""
        if not query_base:
            return 400, []
        
        if not filters['DIM_Date']:
            return 404, []
        # Construcción de la consulta base con JOIN
        query_filtros += """
                INNER JOIN DIM_Customer AS p 
                ON vw.DIM_CustomerId = p.DIM_CustomerId
                INNER JOIN DIM_Date AS d 
                    ON vw.DIM_DateId = d.DIM_DateId
                WHERE vw.YearPay =  ?  """  # Se agrega la tabla para buscar por filtros de manzana también
        
        values = [str(filters.get("DIM_Date"))]

        try:
            # Construcción de condiciones adicionales basadas en los filtros proporcionados
            if 'CustomerFraction' in filters and filters['CustomerFraction']:
                manzana_cond, manzana_values = handler_filters.build_manzana_condition(filters['CustomerFraction'])
                query_filtros += f" AND ({manzana_cond})"
                values.extend(manzana_values)

            # Filtro específico para el estado de la factura pendiente
            if 'DIM_StatusId' in filters and filters['DIM_StatusId']:
                query_filtros += " AND  vw.StatusFactura = 'pendiente'"
            
            
            query_base = query_base.replace("[filtros]", query_filtros)
            #print("DEBUG query_base:", query_base)
            #print("DEBUG values:", values)
            #Ejecutar la consulta con los filtros
            object_conection.cursor.execute(query_base, tuple(values))
            registros = object_conection.cursor.fetchall()

            if registros is None:
                print("No se encontraron registros con los filtros proporcionados")
                return 400, []

            # Crear los objetos con los resultados obtenidos
            # print("#"*100)
            # print([registro for registro in registros if registro])
            # print("#"*100)
            datos = [handler_vista.build_vista(*registro) for registro in registros if registro]

            return 200, datos
        
        except Exception as e:
            print(f"Error al construir los filtros: {e}")
            return 400, []
        finally:
            # Aseguramos que la conexión se cierre
            object_conection.close_conexion()
    

    def get_validation_payment(self, service_name: str, filters: str, values: tuple) -> None | list[Any]:
        """
        Valida si un pago ya ha sido realizado para un servicio específico.
        
        Esta función ejecuta una consulta SQL personalizada según el servicio proporcionado
        y aplica los filtros especificados para verificar la existencia de pagos previos.
        
        Args:
            service_name (str): Nombre del servicio para determinar la vista a consultar (ej: 'agua', 'panteon').
            filters (str): Condiciones WHERE de la consulta SQL para filtrar los resultados.
            values (tuple): Valores parámetros para la consulta parametrizada.
            
        Returns:
            None | list[Any]: 
                - Lista de registros encontrados que coinciden con los criterios de búsqueda.
                - None si no se encuentran registros o ocurre un error.
                
        Raises:
            Exception: Captura y muestra errores durante la ejecución de la consulta SQL.
            
        Example:
            >>> resultado = obj.get_validation_payment(
            ...     service_name='agua',
            ...     filters='anio_pago = ? AND customer_id = ?',
            ...     values=(2025, 'customer_123')
            ... )
        """
        hanlder_conexion = Conexion()
        
        try:
            # Obtenemos la consulta SQL base
            query = self._obtener_query(service_name)

            if not query:
                # Si el servicio no es reconocido, retornamos un código 400 (Bad Request)
                return None
            query = query.replace("[filtros]", filters)
            # Ejecutamos la consulta
            hanlder_conexion.cursor.execute(query, values)

            registros = hanlder_conexion.cursor.fetchall()

            if registros is None:
                print("No se encontraron registros con los filtros proporcionados")
                return None

            # Crear los objetos con los resultados obtenidos
            # print("#"*100)
            # print([registro for registro in registros if registro])
            # print("#"*100)
            #print('Se encontraron registro en el servicio: ', service_name, ' con estos filtros: ', filters, 'y estos valores: ', values)
            return registros
        except Exception as e:
            print(f"Error al construir los filtros: {e}")
            return None
        finally:
            # La conexión no se cierra aqui por que se vuelve a utilizar en el servicio que la llama
            # hanlder_conexion.close_conexion()
            pass
            

    def update_payment_view(self, service_name: str, customer_id: str, year_payment: str, service_type: str) -> tuple[int, list[dict]] | None:
        """
        Actualiza la vista de pagos pendientes de un cliente.

        Esta función se utiliza para obtener los datos de pagos de un cliente
        específico para un servicio y año determinados, generalmente después
        de una actualización.

        Args:
            service_name (str): Nombre del servicio para el que se busca la información.
            customer_id (str): ID del cliente.
            year_payment (str): Año del pago.

        Returns:
            tuple[int, list[dict]] | None: 
                - Una tupla con un código de estado y una lista de diccionarios con los datos de pago.
                - None si no se encuentran los pagos o hay un error.
        """
        filters = {
            'DIM_CustomerId': customer_id,
            'YearPay': year_payment,
            'ServiceDetailesType': service_type
        }
        try:
            status , datos_factura = self.get_payments_by_service(service_name,filters)
            if status != 200:
                return 404, []
            
            return status, datos_factura
        except Exception as e:
            print(f"Error al obtener el pago: {e}")
            return 500, []