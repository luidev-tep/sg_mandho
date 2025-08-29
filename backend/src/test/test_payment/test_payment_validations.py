from src.payments.services.validate_payment import ValidatePayment

def test_validate_Is_payment_in_year():
    


    validate_payment = ValidatePayment()
    AnioPago = 2025
    ServiceName = 'panteon'
    input = ''
    serviceDetailsType = 'faenap'
    DIM_CustomerId = '319e42c1-148c-552b'

    result = validate_payment.is_another_payment_in_year(DIM_CustomerId, AnioPago, ServiceName, input, serviceDetailsType)
    print("*"*50)
    print(result)
    print("*"*50)
    assert result[0] == True




"""
Validaciones 1 para casos como agua La paso
    ServiceName = 'agua'
    serviceDetailsType = 'tomas'
    
    AnioPago = 2025
    DIM_CustomerId = '319e42c1-148c-552b'

"""