from src.dim_servicedetails.models.DIM_ServiceDetails import DIM_Details

from src.dim_dates.dim_date import DIM_DATE

from src.dim_service.DIM_Service import DIM_Service

from src.utils.id_generator import create_id

from src.dim_servicedetails.repository.show import get_amount_by_service_and_date

from src.utils.validate_data import validate_data

from src.dim_servicedetails.services.validate_servicedatil import valide_service_details

from src.dim_servicedetails.repository.create import insertar_registro


from src.dim_servicedetails.repository.update import update_ServiceDetails

class ServiceDetailsCrud:
    """Class to handle CRUD operations for service details."""

    def insert_service_details(self, service_details_json: dict) -> tuple:
        """
        Insert a new service details record if the provided data is valid.

        This function validates the input data, checks for existing services and duplicate entries,
        and then formats and inserts the new service details into the database.

        Args:
            service_details_json (dict): A dictionary containing service details information.
                Expected keys:
                - "ServiceName" (str): The name of the service.
                - "serviceDetailesType" (str): The type of service detail.
                - "amount" (float): The monetary amount for the service detail.
                - "year" (int): The year of the service detail.

        Returns:
            tuple: A tuple containing the status code and a message.
                - (201, str): If the record is created successfully, returns the status code 201 and the new record's ID.
                - (400, str): If the data is invalid or a similar service already exists for the year.
                - (404, str): If the specified service name is not found.
                - (500, str): If an unexpected error occurs during the process.
                
                
                {
                "ServiceName": "agua",
                "amount": 400,
                "isOptional": True,
                "serviceDetailesType": "faena cerro",
                "year": 2025
            }
        """
        float(service_details_json["amount"])
        campos = ["ServiceName", "serviceDetailesType", "amount", "year", "ServiceState", 'isOptional'] #Se debe agregar a la bd, Verificar logica de agregacion tambien
        tipo_campos = [str, str, float, int, str, bool]
        is_valid = validate_data(service_details_json, campos, tipo_campos, "service details")
        if not is_valid:
            return 400, "Datos invalidos"
        
        handler_date = DIM_DATE()
        handler_service = DIM_Service()
        try:
            service_id = handler_service.get_service_id(service_details_json['ServiceName'])

            if not service_id:
                return 404, "Servicio no encontrado"
            
            # Validar si el anio es el actual
            year, month, day = handler_date.full_date
            
            if not year == service_details_json["year"]:
                return 400, "La fecha proporcionada es incorrecta"
            
            StartDate = f'{service_details_json["year"]}-01-01'
            EndDate = f'{service_details_json["year"]}-12-31'

            # Validar que el tipo de servicio no este repetido
            has_Similar_service = valide_service_details(service_details_json)
            if has_Similar_service:
                return 400, "Ya existe un servicio similar en el anio actual"
            
            if service_details_json['isOptional'] == True :
                is_optional = 'status7'
            else:
                is_optional = 'status6'

            # servicio, detalle[0], starDate[1:7]
            startDate = str(handler_date.dateId)
            #se creara un hash para el id
            #Se hasheo para que base muchisimo la probabilidad de que los indices se encuentren.
            hash_id = create_id([service_details_json["amount"], is_optional, service_details_json["isOptional"]]) 
            data_format = {
                "DIM_ServiceDetailsId": create_id([service_details_json['ServiceName'], hash_id, startDate[2:7]]), # Testeado para que no de error
                "DIM_DateId": handler_date.dateId,
                "DIM_ServiceId": service_id,
                "serviceDetailesType": service_details_json["serviceDetailesType"],
                "amount": service_details_json["amount"],
                "isOptional": is_optional,
                "StartDate": StartDate,
                "EndDate": EndDate
            }
            print(f"Data format for service details: {data_format}")
            service_details = DIM_Details(**data_format)
            
            result = insertar_registro(service_details)
            
            if result:
                return 201, data_format["DIM_ServiceDetailsId"]
            else:
                return 500, "Error creando el servicio"
        except Exception as e:
            return 500, f"Error creando el servicio: {e}"
    

    """
    serviciosdetalles = {
    "agua": [("tomas", 360), ("consumo", 360)], # Service Id = '1fbd9d83-7a85-50ec'
    "feria": [("cooperacion", 400), ("faena", 300), ("comida", 500)], # Service Id = '17259752-21dd-5d83'
    "panteon": [("cooperacion", 300), ("faena", 500)], # Service Id = 'e2d33355-5186-597c'
    "delegacion": [("cooperacion", 100), ("faena", 250)] # Service Id = 'acf85e49-6bce-5a8b'
}
Para el anio 2020 el start date es 2020-01-01 y el end date es 2020-12-31

para el dim_dateid hazlo en este formato 20200101
    """
    def get_amount_by_date_servicetype(self,  service_type: str, year: int,) -> tuple:
        """
        Retrieve service details based on date ID and service type.

        Args:
            date_id (int): The date ID to filter by.
            service_type (str): The service type to filter by.

        Returns:
            tuple: A tuple containing the status code and the amount details or an error message.
        """
        handler_date = DIM_DATE()
        handler_service = DIM_Service()
        try:
            fiscal_year = handler_date.get_fiscal_year(year)
            
            service_id = handler_service.get_service_id(service_type)

            if not service_id:
                return 404, {}
            
            amount = get_amount_by_service_and_date(service_type, fiscal_year)

            if amount == 0.0:
                return 404, {}
            
            return 200, {"amount": amount}

        except Exception as e:
            return 500, {}
        
    
    def Update_dim_service_details(self, dim_service_details_id: str, dim_status_id: str) -> tuple:
        """
        Funcion que actualiza el unico parametro modificable de dim_service_details
        el parametro que se actualizara sera el dim_statusId, ya qi epasara no usado a usado
        
        """
        
        response = update_ServiceDetails(dim_status_id, dim_service_details_id)
        
        if not response:
            return 500, "Error actualizando el servicio"
        
        return 200, "Servicio actualizado exitosamente"
