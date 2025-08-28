from src.dim_servicedetails.models.DIM_ServiceDetails import DIM_Details

from src.dim_dates.dim_date import DIM_DATE

from src.dim_service.DIM_Service import DIM_Service

from src.utils.id_generator import create_id

from src.dim_servicedetails.repository.show import get_amount_by_service_and_date

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
        handler_date = DIM_DATE()
        handler_service = DIM_Service()
        try:
            service_id = handler_service.get_service_id(service_details_json['ServiceName'])

            if not service_id:
                return 404, "Service not found"
            
            data_format = {
                "DIM_ServiceDetailsId": create_id([service_details_json.get('serviceDetailsType'), service_details_json['amount']]),
                "DIM_DateId": handler_date.dateId,
                "DIM_ServiceId": service_id,
                "ServiceDetailsType": service_details_json["serviceDetailsType"],
                "amount": service_details_json["amount"] 
            }
            print(f"Data format for service details: {data_format}")
            service_details = DIM_Details(**data_format)
            
            return 201, data_format["DIM_ServiceDetailsId"]
        
        except Exception as e:
            return 500, f"Error creating service details: {e}"
    
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
        
    
