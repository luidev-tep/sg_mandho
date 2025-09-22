from src.fact_revenues.Fact_revenue import factRevenueCrud
from src.dim_servicedetails.serviceDetails import ServiceDetailsCrud

def test_check_payment():
    hadler_revuene = factRevenueCrud()
    
    data = [
    {
        "AnioPago": 2025,
        "DIM_AccountId": "c11e7477-1f05-591e",
        "DIM_CustomerId": "9154e0f2-1f5f-5f2d",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 0,
        "ServiceName": "panteon",
        "amount": 0,
        "entrada": "check_list",
        "movementName": "ingreso",
        "serviceDetailsType": "cooperacion camino"
    },
    {
        "AnioPago": 2025,
        "DIM_AccountId": "2f5174db-0aab-5a1d",
        "DIM_CustomerId": "4ea7de6c-c997-506d",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 0,
        "ServiceName": "panteon",
        "amount": 0,
        "entrada": "check_list",
        "movementName": "ingreso",
        "serviceDetailsType": "cooperacion camino"
    },
    {
        "AnioPago": 2025,
        "DIM_AccountId": "db3a176e-1885-589e",
        "DIM_CustomerId": "b65208f5-1984-5282",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 0,
        "ServiceName": "panteon",
        "amount": 0,
        "entrada": "check_list",
        "movementName": "ingreso",
        "serviceDetailsType": "cooperacion camino"
    },
    {
        "AnioPago": 2025,
        "DIM_AccountId": "deb9ec6f-32c2-5f32",
        "DIM_CustomerId": "bfde17a9-c42f-5e40",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 0,
        "ServiceName": "panteon",
        "amount": 0,
        "entrada": "check_list",
        "movementName": "ingreso",
        "serviceDetailsType": "cooperacion camino"
    },
    {
        "AnioPago": 2025,
        "DIM_AccountId": "2994feb4-3b04-544b",
        "DIM_CustomerId": "8516da1e-1b8a-52cf",
        "DIM_OnwerCustomerId": "ed37cb83-f080-5e41",
        "FactAmount": 0,
        "ServiceName": "panteon",
        "amount": 0,
        "entrada": "check_list",
        "movementName": "ingreso",
        "serviceDetailsType": "cooperacion camino"
    }
    ]
    status, message = hadler_revuene.insert_many_register(data)
    
    print(f"Status: {status}, Message: {message}")
    assert status == 201
    
#Se Testeara la funcion para actualizar el estado ya que no se esta actualziando  correctamente
"""

hanlder_service_details = ServiceDetailsCrud()
def test_update_service_details():
    status, message = hanlder_service_details.Update_dim_service_details("ba355905-5d59-50c9", "status8")
    print(f"Status: {status}, Message: {message}")
    assert status == 200
    
    """