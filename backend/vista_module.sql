--EN ESTE ARCHIVO SE MUESTRA EL CODIGO QUE SE UTILIZO PARA LAS VISTAS \


--Obtener los pagos de un clienten especifico
def get_fact_revenues_by_customer_id(DIM_CustomerId: str, serviceName: str, service_type: str) -> tuple[int, list[dict]]:
    """
    Funcion para obtener los pagos que se realizaron en un solo anio para una persona, basado en el tipo de s
    servicio que se esta ingresando. se tienen que ingresar tanto su service name el nombre del servicio y tambien
    el tipo de servicio
    """
    handler_conexion = Conexion()
    handler_vista = VistaModel()
    query_base = f"""
        SELECT
        vw.CustomerName,
        vw.CustomerMiddleName,
        vw.CustomerLastName,
        vw.CustomerSecondLastName,
        vw.StatusFactura,
        vw.amount,
        vw.FACT_RevenueId,
		vw.DIM_DateId,
        DIM_AccountId
		from VISTA_PAGOS_[tabla] as vw
		where DIM_CustomerId = ? AND
        vw.ServiceDetailesType = ?
        """
    try:
        quwery_base = query_base.replace("[tabla]", serviceName.upper())
        values = (DIM_CustomerId, service_type, )



--Obtener los pagos de todos los clientes relacionados con el servicio de agua

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
        sum(vw.amount) as amount,
        vw.YearPay,
        vw.DIM_AccountId,
        vw.DIM_CustomerId
        FROM [tabla] as vw

        [filtros]

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
        vw.DIM_CustomerId"""

        self.agua = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_AGUA")
        self.feria = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_FERIA")
        self.panteon = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_PANTEON")
        self.delegacion = self.__Query_base.replace("[tabla]", "VISTA_PAGOS_DELEGACION")
