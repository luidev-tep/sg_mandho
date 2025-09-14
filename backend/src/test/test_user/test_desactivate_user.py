from src.users.user import UserCrud

def test_descativate_user() -> None:
    """Esta funcion ha pasado satisfactoriamente
    """
    user_options = UserCrud()
    data = { "DIM_CustomerId": "ab8c820a-8364-5860"}
    estado , mensaje, informacion = user_options.defuncion_user(data)

    print(f"""El estado {estado}  Mensaje: {mensaje}, la informacion {informacion}""")
    assert estado == 403
