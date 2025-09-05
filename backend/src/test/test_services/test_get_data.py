from src.dim_servicedetails.repository.show import get_service_detailsID

def test_serviceDeilsID():
    resultado = get_service_detailsID('tomas', 2025, 'agua')
    assert isinstance(resultado, str)
    assert resultado == 'd8e3ce13-aef7-5594'