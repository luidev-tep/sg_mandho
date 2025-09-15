from src.analytics_reports.repository.get_analytics import GetAnalytics
from src.utils.conexion import Conexion
from src.payments.model.vista_model import VistaModel

from src.payments.repository.get_pending_pays import get_all_payments_pending


class PaymentProcessor(GetAnalytics):
    """
    Clase especializada en el procesamiento y gestión de pagos de usuarios.
    Hereda de GetAnalytics y extiende su funcionalidad para manejar específicamente
    la obtención, formateo y filtrado de datos de pagos.
    """

    def get_all_data_payments(self, dim_customerId: str) -> dict:
        """
        Obtiene todos los datos de pagos de un usuario, agrupados por estado
        (completos/pendientes) y por comitiva.

        Esta función ejecuta consultas SQL para cada comitiva (agua, feria, panteon, delegación)
        y procesa los resultados para clasificarlos según su estado de factura.

        Args:
            dim_customerId (str): El ID del cliente para el cual se buscan los datos.

        Returns:
            dict: Diccionario con dos claves:
                - 'completos': Diccionario de pagos completos agrupados por comitiva
                - 'pendientes': Diccionario de pagos pendientes agrupados por comitiva

        Example:
            >>> resultado = processor.get_all_data_payments("12345")
            >>> print(resultado['completos']['agua'])
            [{'Year': 2024, 'ServiceDetailesType': 'tomas', 'amount': 150.0}]
        """
        handler_conexion = Conexion()
        handler_vista = VistaModel()
        query = """
        SELECT
        vw.CustomerName,
        vw.CustomerMiddleName,
        vw.CustomerLastName,
        vw.CustomerSecondLastName,
        vw.RoleName,
        vw.StatusCuenta,
        vw.StatusFactura,
        vw.ServiceDetailesType,
        sum(vw.amount) as amount,
        vw.YearPay,
        vw.DIM_AccountId,
        vw.DIM_CustomerId
        FROM [tabla] as vw
        WHERE DIM_CustomerId = ?
        GROUP BY 
        vw.CustomerName,
        vw.CustomerMiddleName,
        vw.CustomerLastName,
        vw.CustomerSecondLastName,
        vw.RoleName,
        vw.StatusCuenta,
        vw.StatusFactura,
        vw.ServiceDetailesType,
        vw.YearPay,
        vw.DIM_AccountId,
        vw.DIM_CustomerId
        ORDER by YearPay
        """
        
        pagos_completos = []
        pagos_pendientes = []
        
        for comitiva in list(self.comitivas):
            tabla = self.get_table_by_fraction(comitiva)
            if not tabla:  # Saltar comitivas no válidas
                continue
                
            current_query = query.replace("[tabla]", tabla)
            handler_conexion.cursor.execute(current_query, (dim_customerId,))
            result = handler_conexion.cursor.fetchall()
            
            # print(f"Se está ejecutando la tabla {tabla}")
            # print(f'Número de resultados: {len(result)}')
            
            if not result:
                continue
                
            pagos_crudo = [handler_vista.build_vista(*row) for row in result]
            
            # Clasificar pagos según estado de factura
            completos_count = 0
            pendientes_count = 0
            for pago in pagos_crudo:
                pago_formateado = self._formatear_pago(pago, "get_all_data_payments")
                if pago['StatusFactura'] == 'completo':
                    pagos_completos.append((comitiva, pago_formateado))
                    completos_count += 1
                elif pago['StatusFactura'] == 'pendiente':
                    pagos_pendientes.append((comitiva, pago_formateado))
                    pendientes_count += 1
            # print(f'Número de pagos completos: {completos_count}')
            # print(f'Número de pagos pendientes: {pendientes_count}')
            # print(f'Es igual a {(completos_count + pendientes_count) == len(pagos_crudo)}')
        # Formatear resultados finales
        new_pagos_completos = self.__format_to_dict(pagos_completos)
        new_pagos_pendientes = self.__format_to_dict(pagos_pendientes)
            
        return {'completos': new_pagos_completos, 'pendientes': new_pagos_pendientes}

    def get_all_pending_payments(self, DIM_customerId: int) -> dict:
        """
        Obtiene todos los pagos pendientes de un usuario, aplicando reglas de negocio
        específicas para el servicio de agua.

        Filtra los pagos pendientes según la regla de negocio que requiere que los servicios
        de agua deben tener ambos tipos ('tomas' y 'consumo') para el mismo año, de lo
        contrario se eliminan todos los servicios de agua de ese año.

        Args:
            DIM_customerId (int): El ID del usuario.

        Returns:
            dict: Diccionario donde las claves son las comitivas y los valores son listas
                  de pagos pendientes formateados y filtrados según las reglas de negocio.

        Example:
            >>> pendientes = processor.get_all_pending_payments(12345)
            >>> print(pendientes['agua'])
            [{'Year': 2024, 'ServiceDetailesType': 'tomas', 'amount': 150.0}]
        """
        # Obtener todos los pagos pendientes (esta función debe estar definida en otra parte)
        pagos_fatantes = get_all_payments_pending(DIM_customerId, "get_all_payments_pending")
        
        if not pagos_fatantes:
            return {}

        # print('Total de pago pendientes')
        # i = 0
        # for pago in pagos_fatantes:
        #     if pago['ServiceName'] == 'delegacion':
        #         i += 1
        # print('Total de pagos de delegacion', i)
        # 1. Agrupar todos los pagos por año para facilitar la validación
        grouped_by_year = {}
        for pago in pagos_fatantes:
            year = pago['year']
            if year not in grouped_by_year:
                grouped_by_year[year] = []
            grouped_by_year[year].append(pago)

        # 2. Aplicar la lógica de filtrado para el servicio de agua
        for year, services_in_year in grouped_by_year.items():
            # Identificar los servicios de agua de este año
            water_services = [s for s in services_in_year if s['ServiceName'] == 'agua']
            
            if not water_services:
                continue
                
            # Obtener los tipos de servicio de agua presentes
            water_types_present = {s['serviceType'] for s in water_services}
            
            # Regla de negocio: deben estar AMBOS, 'tomas' y 'consumo'
            if water_types_present != {'tomas', 'consumo'}:
                # Eliminar todos los servicios de 'agua' para este año
                grouped_by_year[year] = [s for s in services_in_year if s['ServiceName'] != 'agua']
            
            

        # 3. Reconstruir la lista de pagos filtrados
        pagos_filtrados = []
        for year_data in grouped_by_year.values():
            pagos_filtrados.extend(year_data)

        # 4. Formatear la información final agrupada por comitiva
        pagos_fatantes_crudo = {}
        for comitiva in self.comitivas:
            pagos_coincidentes = []
            for pago in pagos_filtrados:
                if pago['ServiceName'] == comitiva:
                    pagos_coincidentes.append(
                        self._formatear_pago(pago, "get_all_payments_pending")
                    )
            
            if pagos_coincidentes:
                pagos_fatantes_crudo[comitiva] = pagos_coincidentes
        
        # print ('Pafos por comitiva')
        # for comitiva, pagos in pagos_fatantes_crudo.items():
        #     print(f"Comitiva: {comitiva} | Pagos: {len(pagos)}")
        
        return pagos_fatantes_crudo
        
    def _formatear_pago(self, pago: dict, from_message: str) -> dict:
        """
        Formatea los datos de pago según el contexto de llamada.

        Args:
            pago (dict): Diccionario con los datos del pago. Debe contener:
                - Para 'get_all_data_payments': 'YearPay', 'ServiceDetailesType', 'amount'
                - Para 'get_all_payments_pending': 'year', 'serviceType', 'amount'
            from_message (str): Contexto de llamada que determina el formato:
                - "get_all_data_payments": Formato para datos completos de pagos
                - "get_all_payments_pending": Formato para pagos pendientes

        Returns:
            dict: Pago formateado con las claves 'Year', 'ServiceDetailesType', 'amount'

        Raises:
            ValueError: Si el contexto de llamada no es reconocido
        """
        if from_message == "get_all_data_payments":
            return {
                'Year': int(pago['YearPay']),
                'ServiceDetailesType': pago['ServiceDetailesType'],
                'amount': pago['amount']
            }
        elif from_message == "get_all_payments_pending":
            return {
                'Year': pago['year'],
                'ServiceDetailesType': pago['serviceType'],
                'amount': pago['amount']
            }
        else:
            raise ValueError(f"Contexto no reconocido: {from_message}")
    
    def __format_to_dict(self, pagos_lista: list) -> dict:
        """
        Método privado para agrupar pagos por comitiva.

        Convierte una lista de tuplas (comitiva, pago) en un diccionario
        donde cada clave es una comitiva y el valor es una lista de todos
        los pagos asociados a esa comitiva.

        Args:
            pagos_lista (list): Lista de tuplas en formato (comitiva, pago)

        Returns:
            dict: Diccionario agrupado por comitiva con listas de pagos
        """
        resultado = {}
        for comitiva, pago in pagos_lista:
            if comitiva not in resultado:
                resultado[comitiva] = []
            resultado[comitiva].append(pago)
        return resultado