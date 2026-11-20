"""Herramienta heredada para preparar fixtures locales de SQL Server.

Actualiza cuentas de prueba nombradas en la base de datos configurada. Requiere
DEV_TEST_PASSWORD; no ejecutar contra producción o datos no desechables.
"""
import os
import sys
sys.path.insert(0, 'backend')
from src.utils.conexion import Conexion
from werkzeug.security import generate_password_hash
from src.security.security import SecurityUsers

dev_test_password = os.environ.get("DEV_TEST_PASSWORD")
if not dev_test_password:
    raise SystemExit("Define DEV_TEST_PASSWORD antes de preparar las cuentas de prueba")

dim_pwd = generate_password_hash(dev_test_password, method="scrypt")

with Conexion() as c:
    c.cursor.execute("""
        UPDATE DIM_ServiceOwners
        SET StartDate = '2026-01-01', EndDate = '2026-12-31'
    """)
    
    c.cursor.execute("""
        UPDATE DIM_Customer
        SET [password] = ?
        WHERE username IN ('luisTorres', 'Arcov', 'monseLopez', 'Arely12345', 'miriamComitiva', 'Isabel12345', 'noriel1')
    """, (dim_pwd,))

    c.cursor.execute("""
        UPDATE DIM_Account
        SET StartDate = '2026-01-01', EndDate = '2026-12-31'
        WHERE DIM_StatusId = 'status1'
          AND DIM_CustomerId IN (SELECT DIM_CustomerId FROM DIM_Customer WHERE username IN ('luisTorres', 'Arcov', 'monseLopez'))
    """)
    c.save_changes()
    print("Database credentials and validity updated successfully!")

from scripts.seed_services_and_payments_2026 import seed_services_and_payments
seed_services_and_payments()

sec = SecurityUsers()

test_cases = [
    {"name": "luisTorres", "role": "delegado", "manzana": "tepetate", "password": dev_test_password},
    {"name": "Arcov", "role": "comitiva", "manzana": "tepetate", "password": dev_test_password},
    {"name": "monseLopez", "role": "subdelegado", "manzana": "garambullo", "password": dev_test_password}
]

for tc in test_cases:
    code, msg, user = sec.authenticate_user(tc)
    print(f"User: {tc['name']} ({tc['role']}) -> Code: {code}, Msg: {msg}")
    if user:
        print(f"  Fullname: {user.get('fullname')}, Service: {user.get('ServiceName')}, Manzana: {user.get('CustomerFraction')}")
