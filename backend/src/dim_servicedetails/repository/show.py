import sqlite3
from src.utils.conexion import Conexion
from src.dim_service.DIM_Service import DIM_Service

def get_amount_by_id(serviceDetails_id: str) -> float:
    """
    Retrieves the amount of a service by its Service Details ID.
    
    This function queries the database to find the amount associated with a 
    specific service details identifier. If the ID is not found or an error 
    occurs during the database operation, the function returns 0.0.
    
    Parameters:
        serviceDetails_id (str): The unique identifier of the service details.
    
    Returns:
        float: The amount associated with the service details ID as a floating 
               point number. Returns 0.0 if the ID doesn't exist or if an error occurs.
    
    Example:
        >>> get_amount_by_id("4942db5a-04b2-57b2")
        1500.0
    """
    object_conecttion = Conexion()
    try:
        query = "SELECT amount FROM DIM_ServiceDetails WHERE DIM_ServiceDetailsId = ?"
        object_conecttion.cursor.execute(query, (serviceDetails_id,))
        result = object_conecttion.cursor.fetchone()
        
        if result is not None:
            return result[0]
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error retrieving amount: {str(e)}")
        return 0.0
    finally:
        object_conecttion.close_conexion()


def get_service_detailsID(serviceType: str, Year: int, service : str) -> str:
    """
    Regresea el id del servicio basado en ciertos parametros como lo son, el aio el tipo de servicio y tambien el tipo de servicio
    ya es completamente funcional 
    
    Parameters:
        serviceType (str): The type of service to search for.
    
    Returns:
        str: The service details identifier if found. Returns an empty string 
             if no matching service type is found or if an error occurs.
    
    Example:
        >>> get_service_detailsIS_by_ServiceType("Ranchero")
        "4942db5a-04b2-57b2"
    """
    object_conecttion = Conexion()
    handler_serve = DIM_Service()
    try:
        serviceId = handler_serve.get_service_id(service)
        endDate = f"{Year}-12-31"
        stardDate =  f"{Year}-01-01"
        query = """
            SELECT DIM_ServiceDetailsId FROM DIM_ServiceDetails
            WHERE ServiceDetailesType = ? AND 
            DIM_ServiceId = ?
            and StartDate = ? and EndDate = ?
            """
        object_conecttion.cursor.execute(query, (serviceType, serviceId, stardDate , endDate))
        result = object_conecttion.cursor.fetchone()
        
        if result is not None:
            return result[0]
        else:
            return ""
            
    except Exception as e:
        print(f"Error retrieving service details: {str(e)}")
        return ""
    finally:
        object_conecttion.close_conexion()


def get_service_detailsId_by_ServiceId(ServiceId: str) -> list:
    """
    Retrieves all Service Details IDs associated with a specific Service ID.
    
    This function queries the database to find all service details identifiers 
    that are linked to the given service ID. The function returns a list of 
    these identifiers. If no records are found or an error occurs, an empty 
    list is returned.
    
    Parameters:
        ServiceId (str): The unique identifier of the service.
    
    Returns:
        list: A list of service details identifiers associated with the service ID. 
              Returns an empty list if no records are found or if an error occurs.
    
    Example:
        >>> get_service_detailsId_by_ServiceId("service_123")
        ["4942db5a-04b2-57b2", "d8e3ce13-aef7-5594"]
    """
    object_conecttion = Conexion()
    try:
        query = "SELECT DIM_ServiceDetailsId FROM DIM_ServiceDetails WHERE DIM_ServiceId = ?"
        object_conecttion.cursor.execute(query, (ServiceId,))
        result = object_conecttion.cursor.fetchall()
        
        if result is not None:
            return [row[0] for row in result]
        else:
            return []
            
    except Exception as e:
        print(f"Error retrieving service details: {str(e)}")
        return []
    finally:
        object_conecttion.close_conexion()


def get_amount_by_service_and_date(serviceType: str, date: str) -> float:
    """
    Retrieves the cost of a service for a specific date.
    
    This function calculates the amount of a service type for a particular date, 
    taking into account that service costs may vary over time. It joins the 
    service details with the date dimension to find the appropriate cost for 
    the specified fiscal year.
    
    Parameters:
        serviceType (str): The type of service to search for.
        date (str): The target date in 'YYYY-MM-DD' format for which the amount 
                    should be retrieved. The function uses the fiscal year from this date.
    
    Returns:
        float: The amount of the service for the specified date. Returns 0.0 if 
               no matching record is found or if an error occurs.
    
    Example:
        >>> get_amount_by_service_and_date("Ranchero", "Y25")
        1200.0
    """
    object_conecttion = Conexion()
    try:
        query = """
        SELECT ds.amount
        FROM DIM_ServiceDetails AS ds
        JOIN DIM_Date AS dd ON ds.DIM_DateId = dd.DIM_DateId
        WHERE ds.ServiceDetailesType = ? AND dd.FiscalYear = ?
        """
        object_conecttion.cursor.execute(query, (serviceType, date))
        result = object_conecttion.cursor.fetchone()
        
        if result is not None:
            return result[0]
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error retrieving amount by service and date: {str(e)}")
        return 0.0
    finally:
        object_conecttion.close_conexion()


def get_count_servicetypes_by_service(ServiceId: str, starDate: str, endDate: str) -> int:
    """
    Counts the number of service types associated with a specific service ID within a date range.

    This function is designed to count how many distinct service types are linked 
    to a given service ID within a specified period defined by start and end dates. 
    It's useful for scenarios like counting the number of services billed for a 
    specific module (e.g., "water") within a given year.

    Parameters:
        ServiceId (str): The unique identifier of the service.
        starDate (str): The start date of the period in 'YYYY-MM-DD' format.
        endDate (str): The end date of the period in 'YYYY-MM-DD' format.

    Returns:
        int: The number of service types found. Returns 0 if no records are found 
             or if an error occurs during the database operation.
    
    Example:
        >>> get_count_servicetypes_by_service("water_module_1", "2023-01-01", "2023-12-31")
        5
    """
    object_conecttion = Conexion()
    try:
        query = """
        SELECT COUNT(ServiceDetailesType) FROM DIM_ServiceDetails 
        WHERE DIM_ServiceId = ? 
        AND StartDate <= ? 
        AND EndDate >= ?
        """
        object_conecttion.cursor.execute(query, (ServiceId, starDate, endDate))
        result = object_conecttion.cursor.fetchone()
        
        if result is not None:
            return result[0]
        else:
            return 0
            
    except Exception as e:
        print(f"Error retrieving service types count by service: {str(e)}")
        return 0
    finally:
        object_conecttion.close_conexion()