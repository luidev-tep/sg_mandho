from src.security.security import  SecurityUsers                

def test_get_admin_account():
    hanlder = SecurityUsers()
    data = {
        'username':"monseLopez",
        'manzana': 'garambullo',
        'RoleName': 'subdelegado',
        'password': '2006-11-01'
    }
    
    status, mensaje, data = hanlder.authenticate_user(data )
    print(f"Se esta impriemitno el {status} el mesnaje: {mensaje}, y lps datos: {data}")