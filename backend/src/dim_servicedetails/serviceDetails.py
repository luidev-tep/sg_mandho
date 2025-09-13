from src.dim_servicedetails.models.DIM_ServiceDetails import DIM_Details

from src.dim_dates.dim_date import DIM_DATE

from src.dim_service.DIM_Service import DIM_Service

from src.utils.id_generator import create_id

from src.dim_servicedetails.repository.show import get_amount_by_service_and_date

from src.utils.validate_data import validate_data

from src.dim_servicedetails.services.validate_servicedatil import valide_service_details

from src.dim_servicedetails.repository.create import insertar_registro


#Si esta clase se hace predefinida, se esta logica no sera tan utils hasta que la clase sea creada
# y se cree en la interfaz un metodo para poder interactusl con ella
class ServiceDetailsCrud:
    """Class to handle CRUD operations for service details."""


    def insert_service_details(self, service_details_json: dict) -> tuple:
        """
        Insert a new service details record if the provided data is valid.

        Args:
            service_details_json (dict): A dictionary containing service details information.

        Returns:
            tuple: A tuple containing the status code and a message.
        """
        float(service_details_json["amount"])
        campos = ["ServiceName", "serviceDetailesType", "amount", "year"]
        tipo_campos = [str, str, float, int]
        is_valid = validate_data(service_details_json, campos, tipo_campos, "service details")
        if not is_valid:
            return 400, "Datos invalidos"
        
        handler_date = DIM_DATE()
        handler_service = DIM_Service()
        try:
            service_id = handler_service.get_service_id(service_details_json['ServiceName'])

            if not service_id:
                return 404, "Servicio no encontrado"
            
            #validar si el anio es el actual
            year , month, day = handler_date.full_date
            
            if not year == service_details_json["year"]:
                return 400, "Esta mal la fecha proporcionada"
            

            StartDate = f'{service_details_json["year"]}-01-01'
            EndDate = f'{service_details_json["year"]}-12-31'

            #validar que el tipo de serviicio no este repetido
            has_Similar_service = valide_service_details(service_details_json)
            if has_Similar_service:
                return 400, "Ya existe un servicio similar en el anio actual"

            
            #servicio, detalle[0], starDate[1:7]
            startDate = str(handler_date.dateId)
            data_format = {
                "DIM_ServiceDetailsId": create_id([service_details_json['ServiceName'], service_details_json['serviceDetailesType'], startDate[2:7]]), #Testeado para que no de error
                "DIM_DateId": handler_date.dateId,
                "DIM_ServiceId": service_id,
                "serviceDetailesType": service_details_json["serviceDetailesType"],
                "amount": service_details_json["amount"] ,
                #Modificar desde aquiiii
                "StartDate": StartDate, # Estos aun no existen
                "EndDate": EndDate # ni este sajsvnfk
            }
            print(f"Data format for service details: {data_format}")
            service_details = DIM_Details(**data_format)
            

            #insertar_registro(service_details)
            
            return 201, data_format["DIM_ServiceDetailsId"]
        
        except Exception as e:
            return 500, f"Error creating service details: {e}"
    

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
        
    
