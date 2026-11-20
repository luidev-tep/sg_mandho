from src.analytics_reports.repository.get_analytics import GetAnalytics
from src.utils.conexion import Conexion
from src.payments.model.vista_model import VistaModel


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

        SI EL ESTAD DE PAGO CAMBIA SE DEBE AGREGAR COMO ESTADO COMPLETO O TRABAJADO. sE SUPONE QUE ES DE UNA VISTA
        POR LO QUE NO DEBERIA ESTAR ESTE PROBELMA

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
        query = f"""
            SELECT
                vw.CustomerName,
                vw.CustomerMiddleName,
                vw.CustomerLastName,
                vw.CustomerSecondLastName,
                vw.RoleName,
                vw.StatusCuenta,
                vw.StatusFactura,
                vw.ServiceDetailesType,
                (sd.amount - vw.amount) as amount, -- Restar el amount de la vista del amount de la subconsulta
                vw.YearPay,
                vw.DIM_AccountId,
                vw.DIM_CustomerId
            FROM [tabla] as vw
            JOIN (
                SELECT 
                    CAST(d.Year AS NVARCHAR(10)) as Year,
                    ServiceDetailesType,
                    amount
                FROM DIM_ServiceDetails -- Asumiendo que esta es la tabla correcta
                JOIN DIM_Service as s on
                DIM_ServiceDetails.DIM_ServiceId = s.DIM_ServiceId 
                AND ServiceName = ?
                JOIN DIM_Date as d on
                DIM_ServiceDetails.DIM_DateId = d.DIM_DateId 
            ) as sd ON
                sd.ServiceDetailesType = vw.ServiceDetailesType AND
                vw.YearPay = sd.Year
            WHERE vw.DIM_CustomerId = ?
        """
        
        pagos_completos = []
        pagos_pendientes = []
        
        try:
            for comitiva in list(self.comitivas):
                tabla = self.get_table_by_fraction(comitiva)
                if not tabla:  # Saltar comitivas no válidas
                    continue
                    
                current_query = query.replace("[tabla]", tabla)
                service = self.select_service(tabla)
                handler_conexion.cursor.execute(current_query, (service, dim_customerId))
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
                    if pago['StatusFactura'] == 'completo' or pago['StatusFactura'] == 'trabajado':
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
        finally:
            handler_conexion.close_conexion()
    
    def select_service(self, view_name: str) -> str | None:
        """
        Selecciona la comitiva correspondiente según el nombre de la vista.

        Args:
            view_name (str): Nombre de la vista (e.g., 'VISTA_PAGOS_AGUA').

        Returns:
            str | None: Nombre de la comitiva ('agua', 'feria', 'panteon', 'delegacion').
                        Retorna None si la comitiva no es reconocida.

        Example:
            view_name = 'VISTA_PAGOS_AGUA'
            output = self.select_service(view_name) # Retorna 'agua'
        """
        view_name_lower = view_name.lower()
        if "agua" in view_name_lower:
            return "agua"
        elif "feria" in view_name_lower:
            return "feria"
        elif "panteon" in view_name_lower:
            return "panteon"
        elif "delegacion" in view_name_lower:
            return "delegacion"
        return None

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