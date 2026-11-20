import os

from src.security.security import  SecurityUsers                

def test_get_admin_account():
    hanlder = SecurityUsers()
    data = {
        'name':"demo_comitiva",
        'manzana': 'yhonda',
        'role': 'comitiva',
        'password': os.environ.get("TEST_DEMO_PASSWORD", "ChangeMe123!")
    }
    
    status, mensaje, data = hanlder.authenticate_user(data )
    print(f"Se esta impriemitno el {status} el mesnaje: {mensaje}, y lps datos: {data}")
