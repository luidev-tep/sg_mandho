from src.utils.validate_data import validate_data
from src.analytics_reports.repository.get_analytics import GetAnalytics
from src.analytics_reports.repository.PaymentProcesor import PaymentProcessor

class Analitycs:
    """
    Clase que maneja la lógica de negocio para los reportes de analíticas.

    Se encarga de procesar los datos de entrada, validarlos y hacer las llamadas
    correspondientes a la capa de repositorio para obtener la información
    de la base de datos y generar los reportes.
    """
    def __init__(self):
        """
        Inicializa la clase y crea una instancia de GetAnalytics.

        Attributes:
            get_analytics (GetAnalytics): Instancia de la clase GetAnalytics
                                          para interactuar con el repositorio de datos.
        """
        self.get_analytics = GetAnalytics()
        self.payment_processor = PaymentProcessor()


    def get_analytics_per_month(self, data_json: dict) -> tuple[int, str, dict]:
        """ 
        Obtiene los datos de analíticas por mes, incluyendo ingresos y
        fracciones facturadas.

        Valida los datos de entrada y, si son correctos, realiza las peticiones
        al repositorio para obtener los ingresos del año y las facturas del mes.

        Args:
            data_json (dict): Un diccionario con los filtros de búsqueda.
                              Debe contener las claves "comitiva", "mes",
                              "usuario" y "anio".

        Returns:
            tuple[int, str, dict]: Una tupla que contiene:
                                   - El código de estado HTTP (200 si es exitoso, 400 o 500 en caso de error).
                                   - Un mensaje descriptivo del resultado.
                                   - Un diccionario con los datos de analíticas,
                                     o un diccionario vacío en caso de error.
        """
        campos = ["comitiva", "mes", "usuario", "anio"]
        tipo_campos = [str, str, str, str]
        is_valid, message = validate_data(data_json, campos, tipo_campos, "analitycs")
        if not is_valid:
            return 400, message, {}
        
        data_analythics = dict()
        try:
            print(f"Obteniendo la informacion de la comitiva: {data_json['comitiva']}, mes: {data_json['mes']}, anio: {data_json['anio']}")
            
            # Obtiene el monto total de ingresos para el año de la comitiva especificada
            data_analythics['dataIncomes'] = self.get_analytics.get_amount_for_year(data_json['mes'], data_json['comitiva'], data_json['anio'])

            # Obtiene las facturas por mes y comitiva
            data_analythics['dataFractions'] = self.get_analytics.get_bills_by_month(data_json['mes'], data_json['comitiva'], data_json['anio'])

            data_analythics['dataCountUsers'] = {'manzanas': self.get_analytics.get_population_by_manzana()}

            data_analythics['dataUserBills'] = {'manzanas': self.get_analytics.get_data_payments(data_json['comitiva'], data_json['anio'])}
            
            return 200, 'Datos obtenidos correctamente', data_analythics
        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return 500, "Ocurrió un error al obtener los datos.", {}
        
        
    def get_analytics_per_customer(self, data_json: dict) -> tuple[int, str, dict]:
        """
        Obtiene el historial de pagos de un usuario.

        Esta función recupera los pagos de un usuario, clasificados en tres categorías:
        - Pagos completos: Pagos que han sido realizados y facturados.
        - Pagos pendientes: Pagos que han sido realizados pero aún no han sido facturados.
        - Pagos pendientes sin facturar: Deudas de años anteriores que aún no han sido cubiertas.

        Args:
            data_json (dict): Un diccionario que debe contener la clave "Dim_customerId"
                              con el ID del cliente.

        Returns:
            tuple[int, str, dict]: Una tupla que contiene:
                - El código de estado HTTP (200 si es exitoso, 400 o 500 en caso de error).
                - Un mensaje descriptivo del resultado.
                - Un diccionario con los datos de analíticas en el siguiente formato,
                  o un diccionario vacío en caso de error:
                  {
                    "completos": {
                      "agua": {"Year": 2025, "ServiceDetailesType": "tomas", "amount": 360.0},
                      "feria": {"Year": 2025, "ServiceDetailesType": "tomas", "amount": 360.0}
                    },
                    "pendientes": {
                      "agua": {"Year": 2024, "ServiceDetailesType": "tomas", "amount": 165.0}
                    },
                    "pendientes_sin_facturar": {
                      "agua": [
                        {"Year": 2021, "ServiceDetailesType": "consumo", "amount": 360.0}
                      ]
                    }
                  }
        """
        campos = ["Dim_customerId"]
        tipo_campos = [str]
        is_valid, message = validate_data(data_json, campos, tipo_campos, "analitycs")
        if not is_valid:
            return 400, message, {}
        try:
            
            pagos_hechos = self.payment_processor.get_all_data_payments(data_json['Dim_customerId'])
            
            pagos_pendientes = self.payment_processor.get_all_pending_payments(data_json['Dim_customerId'])
            
            
            data_format = {'completos': pagos_hechos['completos'], 'pendientes': pagos_hechos['pendientes'], 'pendientes_sin_facturar': pagos_pendientes}
            
            return 200, 'Datos obtenidos correctamente', data_format
        except Exception as e:
            print(f"Error al obtener la informacion de la comitiva: {e}")
            return 500, "Ocurrió un error al obtener los datos.", {}