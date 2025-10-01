from src.security.security import SecurityUsers

def test_securtuty_user_chosen():
    """
    Testea la funcion de validar al usuario
    """
    handler_user = SecurityUsers()
    data = {
        'RoleName':"comitiva",
        'CustomerFraction': 'tepetate',
        'serviceName': 'agua',
    }
    status, mensaje = handler_user.validate_user_post(data)
    print(f"Se esta impriemitno el {status} el mesnaje: {mensaje}")
    assert status == 409


def test_security_inser_user():
    """
    Testea rtoda la validacion y verificar si es correcta
    """
    handler_user = SecurityUsers()
    data = {
        'DIM_CustomerId': '9154e0f2-1f5f-5f2d',
        'CustomerFraction': 'tepetate',
        'username': 'Arcov',
        'password': 'xdxd12345',
        'RoleName':"comitiva",
        'serviceName': 'agua',
    }
    status, mensaje = handler_user.insert_new_Onwer(data)
    print(f"Se esta impriemitno el {status} el mesnaje: {mensaje}")
    assert status == 200
