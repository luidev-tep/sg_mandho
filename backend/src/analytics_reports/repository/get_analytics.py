from src.utils.conexion import Conexion
from src.dim_service.DIM_Service import DIM_Service
from src.analytics_reports.models.model_component import AnalythicsModels

handler_model = AnalythicsModels()

class GetAnalytics:
    """
    Clase que maneja la lógica para obtener diversos reportes y analíticas
    relacionadas con los pagos y servicios.

    Esta clase se conecta a la base de datos y ejecuta consultas SQL
    para generar datos de ingresos por año, facturas por mes, y otra
    información relevante.
    """
    def __init__(self):
        self.comitivas = ('agua', 'feria', 'panteon', 'delegacion')
        
    def get_table_by_fraction(self, comitiva: str) -> str:
        """
        Obtiene el nombre de la vista de pagos de la base de datos
        según la comitiva especificada.

        Args:
            comitiva (str): El nombre de la comitiva (por ejemplo, "agua", "feria").

        Returns:
            str: El nombre de la vista de pagos correspondiente.
                 Retorna una cadena vacía si la comitiva no es válida.
        """
        vistas_por_comitiva = {
            "agua": "VISTA_PAGOS_AGUA",
            "feria": "VISTA_PAGOS_FERIA",
            "panteon": "VISTA_PAGOS_PANTEON",
            "delegacion": "VISTA_PAGOS_DELEGACION"
        }

        if comitiva in vistas_por_comitiva:
            return vistas_por_comitiva[comitiva]
        else:
            return ""

    def get_amount_for_year(self, mes: str, comitiva: str, anio: str) -> list:
        """
        Obtiene los ingresos totales por mes para un año y comitiva dados.

        La función genera una consulta SQL dinámica para filtrar los últimos
        seis meses de datos, manejando correctamente los cambios de año.

        Args:
            mes (str): El mes actual en formato de cadena (ej. 'M03').
            comitiva (str): La comitiva para la cual se buscan los datos.
            anio (str): El año actual en formato de cadena (ej. 'Y24').

        Returns:
            list: Una lista de diccionarios con el formato
                  `[{"month": "MM-YYYY", "amount": 0}, ...]`.
                  Retorna una lista vacía en caso de error o si no hay datos.

        ESTA FUNCION FILTRA CORRECTAMENTE LOS PAGOS GENERADOS COMO TRABAJADOS
        """
        handler_service = DIM_Service()
        handler_conexion = Conexion()
        query = """
            -- Consulta con filtros de año y mes para casos que cruzan años fiscales
            -- Modificada para mostrar todos los meses con 0 cuando no hay pagos
            SELECT 
            d.FiscalYear,
            d.FiscalMonth, 
            COALESCE(SUM(revenue_servicios.amount), 0) as revenues
            FROM DIM_Date as d
            LEFT JOIN (
            -- SUBCONSULTA: Une FACT_Revenue con DIM_ServiceDetails
            SELECT 
                fac.DIM_DateId,
                fac.amount
            FROM FACT_Revenue as fac
            INNER JOIN DIM_ServiceDetails as serv 
                ON serv.DIM_ServiceDetailsId = fac.DIM_ServiceDetailsId
            WHERE serv.DIM_ServiceId = ? AND 
            fac.dim_statusId in ('status4', 'status5')  
            ) as revenue_servicios ON d.DIM_DateId = revenue_servicios.DIM_DateId
            
            WHERE
            
            [filtros]
            GROUP BY d.FiscalYear, d.FiscalMonth
            ORDER BY d.FiscalYear DESC, d.FiscalMonth DESC;
        """
        try:
            # Se obtiene el ID de la comitiva asociada
            serviceId = handler_service.get_service_id(comitiva)
            mes = int(mes[1:])  # Convierte 'M03' a 3
            meses = []
            meses2 = []
            mes_actual = mes
            valores = []
            valores.append(serviceId)

            if mes_actual <= 5:
                # Lógica para cuando se necesita combinar año actual y anterior
                # Generar meses del año actual (desde Enero hasta mes actual)
                parametros = []
                for i in range(1, mes_actual + 1):
                    meses.append(f'M{i:02d}')
                    parametros.append("?")
                
                # Agregar año actual y sus meses a valores
                valores.append(anio)
                valores.extend(meses)
                
                # Calcular año anterior
                anio_pasado = f'Y{str(int(anio[1:]) - 1)}'
                valores.append(anio_pasado)

                # Calcular meses del año anterior necesarios para completar 6 meses
                meses_restantes_count = 6 - mes_actual
                parametros2 = []
                for i in range(12 - meses_restantes_count + 1, 13):
                    meses2.append(f'M{i:02d}')
                    parametros2.append("?")
                
                # Agregar meses del año anterior a valores
                valores.extend(meses2)
                meses.extend(meses2)
                
                # Construir cláusula WHERE dinámica
                filtros = f"""
                
                (d.FiscalYear = ? AND d.FiscalMonth IN ({','.join(parametros)}))
                OR (d.FiscalYear = ? AND d.FiscalMonth IN ({','.join(parametros2)}))
                """
            else:
                parametros = []
                inicio = mes_actual - 5  # Los últimos 6 meses, incluyendo el actual
                for i in range(inicio, inicio + 6):
                    meses.append(f'M{i:02d}')
                    parametros.append("?")
                
                # Agregar año actual y sus meses a valores
                valores.append(anio)
                valores.extend(meses)
                
                # Construir cláusula WHERE dinámica
                filtros = f"""(d.FiscalYear = ? AND d.FiscalMonth IN ({','.join(parametros)}))"""

            query = query.replace("[filtros]", filtros)

            handler_conexion.cursor.execute(query, tuple(valores))
            result = handler_conexion.cursor.fetchall()
            
            if not result:
                return []
            else:
                # Transforma los resultados de la base de datos al formato del modelo
                return [handler_model.model_get_revenues_per_month(row[0], row[1], row[2]) for row in result]
        
        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return []
        finally:
            handler_conexion.close_conexion()

    def get_bills_by_month(self, mes: str, comitiva: str, anio: str) -> list:
        """
        Obtiene el total de ingresos por fracción para un mes y año específicos.

        Args:
            mes (str): El mes en formato de cadena (ej. 'M03').
            comitiva (str): La comitiva para la cual se buscan los datos.
            anio (str): El año en formato de cadena (ej. 'Y24').

        Returns:
            list: Una lista de diccionarios con el formato
                  `[{"fraction": "Manzana A", "revenue": 15000}, ...]`.
                  Retorna una lista vacía en caso de error o si no hay datos.
                  
        ESTA QUERY AUN NO ES FUNCIONAL, YA QUE LA VISTA EN LA QUE SE BASA NO ES FUNCIONAL, YA QUE NO FILTRA POR LOS PAGOS PENDIENTES
        Y HECHOS PERO FICTICIOS AL SER SALTABLES
        """
        query = """
            -- FUNCIONAL
            SELECT 
                cus.CustomerFraction,
                ISNULL(SUM(vw.amount), 0) as revenue 
            FROM DIM_Customer as cus 
            LEFT JOIN (
                SELECT 
                    c.DIM_CustomerId,
                    a.DIM_AccountId,
                    f.DIM_DateId,
                    s.ServiceName, --Se agrego este campo para validar rapidamnete si el servicio que se espera
                    f.amount  -- Necesitas incluir el campo amount en la subconsulta
                FROM DIM_Account as a
                JOIN DIM_Customer as c ON 
                    a.DIM_CustomerId = c.DIM_CustomerId
                JOIN FACT_Revenue as f ON
                    a.DIM_AccountId = f.DIM_AccountId
                JOIN DIM_ServiceDetails as sv ON 
                    sv.DIM_ServiceDetailsId = f.DIM_ServiceDetailsId
                JOIN DIM_Service as s ON
                    s.DIM_ServiceId = sv.DIM_ServiceId  -- Corregido: era 'SV' en mayúsculas
                    AND s.ServiceName = ?
                -- GROUP BY removido de la subconsulta para permitir la suma correcta
                join  DIM_Status as status on
                    f.DIM_StatusId = status.DIM_StatusId
                    AND StatusName in ('completo', 'pendiente')
            ) as vw 
                ON vw.DIM_CustomerId = cus.DIM_CustomerId 
            LEFT JOIN DIM_Date as dat 
                ON vw.DIM_DateId = dat.DIM_DateId 
            WHERE (dat.FiscalMonth = ? OR dat.FiscalMonth IS NULL)
                AND (dat.FiscalYear = ? OR dat.FiscalYear IS NULL)
                -- Removido el AND colgante
            GROUP BY cus.CustomerFraction
            ORDER BY cus.CustomerFraction;
        """
        handler_conexion = Conexion()
        try:
            tabla_vista = self.get_table_by_fraction(comitiva)
            if not tabla_vista:
                return []
            
            #query = query.replace("[tabla]", tabla_vista)

            handler_conexion.cursor.execute(query, (comitiva,mes, anio))
            result = handler_conexion.cursor.fetchall()
            
            if not result:
                return []
            else:
                return [handler_model.model_get_amount_per_fraction(row[0], row[1]) for row in result]
        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return []
        finally:
            handler_conexion.close_conexion()
    
    def get_data_payments(self, comitiva:str, anio:str ) -> list | dict[str, list]:
        """
        Obtiene un resumen del estado de pagos por manzana para un mes y comitiva.

        Esta función aún no está implementada y se usa como marcador de posición.
        Se espera que devuelva datos como el total de personas, pagados,
        pendientes y un porcentaje de pago por manzana.

        Args:
            mes (str): El mes de referencia.
            comitiva (str): La comitiva de la cual se obtendrán los datos.
            debe enviar informacion en este formato:     "manzanas": [
      {
        "id": 1,
        "nombre": "Manzana A",
        "color": "#4F46E5",
        "personas": 150,
        "pagados": 120,
        "pendientes": 30,
        "porcentaje": 80
      },

        Returns:
            list: Una lista de diccionarios con la información de pagos por manzana.
        """
        table_name = self.get_table_by_fraction(comitiva)
        if not table_name:
            return []
        
        estados = ('completo', 'pendiente')
        query = """
            SELECT
                cus.CustomerFraction,
                COUNT(dat.DIM_DateId) AS pendientes
            FROM
                DIM_Customer AS cus
            LEFT JOIN [tabla] AS v1 ON
                cus.DIM_CustomerId = v1.DIM_CustomerId
                AND v1.StatusFactura = ?
                AND v1.YearPay = ?
            LEFT JOIN DIM_Date AS dat ON
                v1.DIM_DateId = dat.DIM_DateId
            GROUP BY
                cus.CustomerFraction;  
        """
        query = query.replace("[tabla]", table_name)
        

        handler_conexion = Conexion()
        # se obtien eel anio en formato esperado
        get_year = anio[1:]
        year = f"20{get_year}"
        manzanas = {
            'buenavista': [],
            'centro': [],
            'cerritos': [],
            'garambullo': [],
            'tepetate': [],
            'yhonda': []
                }
        try:
            for estado in estados:
                # print(query)
                # print(estado, year)
                handler_conexion.cursor.execute(query, (estado, year))
                data = handler_conexion.cursor.fetchall()
                
                for row in data:
                    #print(row)

                    manzanas[row[0]].append(row[1])

            #obtener el porcentaje de pagos 
            for manzana in manzanas:
                porcentaje = 0
                #print(f'Se esta imprimiento la informacionde cad amanzana: {manzana}')
                total = sum(manzanas[manzana])
                if manzanas[manzana][0] != 0:
                    porcentaje = (manzanas[manzana][0] / total) * 100
                    porcentaje = round(porcentaje, 2)
                manzanas[manzana].append(porcentaje)
                manzanas[manzana].insert(0, total) 

            return [handler_model.model_get_bill_payments(name,*values) for name, values in manzanas.items()]

        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return []
        finally:
            handler_conexion.close_conexion()
    
    def get_population_by_manzana(self) -> list[dict] | list:
        """
        Obtiene el total de personas por manzana para un mes y comitiva específicos.

        Esta función aún no está implementada y se usa como marcador de posición.
        Se espera que devuelva una lista de diccionarios con el nombre de la
        manzana y el total de personas asociadas.

        Args:

        Returns:
            list: Una lista de diccionarios con la población por manzana.
        """
        query = """
        SELECT CustomerFraction , count(DIM_CustomerId) as n_customers from DIM_Customer
        where CustomerEndDate = 's/n'
        GROUP BY CustomerFraction
        """
        handler_conexion = None
        try:
            handler_conexion = Conexion()
            handler_conexion.cursor.execute(query)
            result = handler_conexion.cursor.fetchall()
            return [handler_model.model_get_population(*row) for row in result]
        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return []
        finally:
            if handler_conexion:
                handler_conexion.close_conexion()
    
    def get_admins_data(self, comitiva):
        """
        Obtiene la información de los administradores de una comitiva.

        Esta función aún no está implementada y se usa como marcador de posición.
        Se espera que devuelva una lista de diccionarios con los detalles
        de los administradores de la comitiva.

        Args:
            comitiva (str): La comitiva para la cual se buscan los administradores.

        Returns:
            list: Una lista de diccionarios con los datos de los administradores.
        """
        query = """
            SELECT 
                fullname,
                RoleName,
                StartDate,
                EndDate
            FROM
                SecurityUsers 
                WHERE ServiceName = ? 
        """
        handler_conexion = None
        try:
            handler_conexion = Conexion()
            handler_conexion.cursor.execute(query, (comitiva,))
            result = handler_conexion.cursor.fetchall()
            if result is None:
                return []
            
            return [handler_model.model_get_admins_data(*row) for row in result]
        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return []
        finally:
            if handler_conexion:
                handler_conexion.close_conexion()
