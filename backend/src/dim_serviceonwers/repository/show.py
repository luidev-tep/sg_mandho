from src.utils.conexion import Conexion, DatabaseError

def get_ServiceOnwers_by_name(customer_id: str) -> tuple:
    """
    Retrieve service owner information by customer ID.

    Args:
        customer_id (str): The ID of the customer.

    Returns:
        serviceOnwersId (str): The ID of the service owner. It will return a string, or empty string if not found.
    """
    object_conecction = Conexion()
    try:
        query = "SELECT DIM_ServiceOwnersId FROM DIM_ServiceOwners WHERE DIM_CustomerId = ?"
        object_conecction.cursor.execute(query, (customer_id,))

        result = object_conecction.cursor.fetchone()
        if result is not None:
            return result[0]
        else:
            return ""  # Return empty string if no record found
    except DatabaseError as e:
        print(f"Error retrieving service owner by name: {str(e)}")
        return ""
    finally:
        object_conecction.close_conexion()
