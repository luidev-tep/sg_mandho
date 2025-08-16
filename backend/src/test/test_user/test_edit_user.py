from src.users.user import UserCrud

def test_edit_user() -> None:
    """Funcion para editar si es que se esta editando un usuario correctamente

    Pasooo
    """
    handler = UserCrud()
    user_json = {
        "DIM_CustomerId": "ed37cb83-f080-5e41",
        "CustomerAddress": "",
        "CustomerFraction": "garambullo",
        "CustomerNumberExt": '08'
    }
    estado, mensaje, data = handler.edit_user(user_json)
    print(f"""El estado {estado}  Mensaje: {mensaje}""")
    for key, value in data.items():
        print(f"{key}: {value}")

    assert estado == 201
    assert mensaje == "El usuario se ha actualizado correctamente"
    assert type(data) == dict

