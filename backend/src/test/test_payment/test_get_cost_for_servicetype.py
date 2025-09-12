from src.payments.payment import PaymentCrud

from src.payments.repository.get_pending_pays import get_pending_pays

def test_get_cost():
    payment_handler = PaymentCrud()
    data = {
        "service_type": "tomas", 
        "Year": 2025
        }
    code, message, response = payment_handler.get_cost_by_payment_year(data)
    print(f"code: {code}, message: {message}, response: {response}")
    assert code == 200
    assert isinstance(response, float)



def test_get_pending_pays():
    
    service_id = '9154e0f2-1f5f-5f2d'
    serviceName = "agua"

    data = get_pending_pays(service_id, serviceName)

    print(data)
    assert isinstance(data, list)