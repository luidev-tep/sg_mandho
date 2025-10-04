from src.users.user import get_admins_home_info, get_home_info

def test_get_admins_home_info():
    """
    Test para obtener la informacion de los administradores para mostrar en la pantalla principal
    """
    status, mensaje, datos = get_home_info()
    print(f"Este es el mensaje {mensaje}, Esste es la info {datos}")
    assert status == 200
    assert mensaje == "Informacion obtenida correctamente"
    assert datos
    


def test_only_funtion():
    """
    Testear la funcionalidad sola
    """
    
    datos = get_admins_home_info()
    print(f" Esste es la info {datos}")
    assert isinstance(datos, list)
