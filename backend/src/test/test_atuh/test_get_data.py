from src.security.security import  SecurityUsers                

def test_get_admin_account():
    hanlder = SecurityUsers()
    data = {
        'name':"miriamComitiva",
        'manzana': 'yhonda',
        'role': 'comitiva',
        'password': 'TacosHola!8'
    }
    
    status, mensaje, data = hanlder.authenticate_user(data )
    print(f"Se esta impriemitno el {status} el mesnaje: {mensaje}, y lps datos: {data}")