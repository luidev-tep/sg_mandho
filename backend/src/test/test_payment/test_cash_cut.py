from src.payments.cash_cut import cashCutCrud


def test_cash_cut():
    cash_cut = cashCutCrud()
    data = {
        "DIM_ServiceDetailesType": "faena",
        "DIM_ServiceOwnersId": "0901a1e6-8779-5695",
        "DIM_service": "panteon"
    }
    #status, message, response = cash_cut.CashCut(data)
    #print(f"Status: {status}, Message: {message}, Response: {response}")
    
    


def test_get_service_chosen():
    cash_cut = cashCutCrud()
    data = {
        "DIM_ServiceDetailesType": ["faena", 'cooperacion camino', 'cooperacion'],
        "DIM_service": "panteon"
    }
    status, message = cash_cut.get_service_chosen(data)
    print(f"Status: {status}, Message: {message}")
    
    assert status == 200