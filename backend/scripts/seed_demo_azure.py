"""Datos sintéticos idempotentes para una base de demostración ya migrada."""
import os
import sys
from datetime import datetime
from pathlib import Path
import pytz

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
load_dotenv(BACKEND / '.env')
from src.dim_dates.dim_date import generar_anio_real
from src.utils.conexion import Conexion

ADMINS = [('demo_delegado', 'delegado', 'delegado', 'centro'),
          ('demo_agua', 'comitiva', 'agua', 'tepetate'),
          ('demo_feria', 'comitiva', 'feria', 'garambullo'),
          ('demo_panteon', 'comitiva', 'panteon', 'yhonda'),
          ('demo_delegacion', 'comitiva', 'delegacion', 'centro'),
          ('demo_subdelegado', 'subdelegado', 'personas', 'cerritos')]
FRACTIONS = ('centro', 'tepetate', 'cerritos', 'garambullo', 'yhonda', 'buenavista')
ROLES = ('vecino', 'pequeño propietario', 'ranchero', 'estudiante', 'residente', 'vecino exento')
SERVICES = ('agua', 'feria', 'panteon', 'delegacion')


def insert_once(cur, table, key, columns, values):
    # All SQL identifiers here are fixed literals supplied by this script.
    names = ', '.join(f'[{name}]' for name in columns)
    marks = ', '.join('?' for _ in values)
    cur.execute(f'IF NOT EXISTS (SELECT 1 FROM [{table}] WHERE [{columns[0]}] = ?) '
                f'INSERT INTO [{table}] ({names}) VALUES ({marks})', (key, *values))


def main():
    password = os.environ.get('DEMO_ADMIN_PASSWORD', '')
    if len(password) < 8:
        raise SystemExit('DEMO_ADMIN_PASSWORD es obligatorio y debe tener al menos 8 caracteres')
    with Conexion() as db:
        cur = db.cursor
        for year in range(2025, 2029):
            existing = {r[0] for r in cur.execute('SELECT DIM_DateId FROM DIM_Date WHERE [Year]=?', year)}
            rows = [row for row in generar_anio_real(year) if row[0] not in existing]
            if rows:
                cur.executemany('INSERT INTO DIM_Date (DIM_DateId,FiscalYear,FiscalMonth,FiscalQuarter,FiscalWeek,FiscalDay,[Year],[Month],[Week],[Day]) VALUES (?,?,?,?,?,?,?,?,?,?)', rows)
        roles = {r[1]: r[0] for r in cur.execute('SELECT DIM_RoleId,RoleName FROM DIM_Role')}
        services = {r[1]: r[0] for r in cur.execute('SELECT DIM_ServiceId,ServiceName FROM DIM_Service')}
        for i, (user, role, service, fraction) in enumerate(ADMINS):
            cid = 'demo_admin_' + str(i)
            insert_once(cur, 'DIM_Customer', cid, ('DIM_CustomerId','DIM_DateId','CustomerName','CustomerLastName','CustomerDateBirth','CustomerStartDate','CustomerFraction','username','password'), (cid, 20260101, 'Demo', 'Administrador'+str(i), '1980-01-01', '2026-01-01', fraction, user, generate_password_hash(password, method='scrypt')))
            aid = 'demo_admin_account_' + str(i)
            insert_once(cur, 'DIM_Account', aid, ('DIM_AccountId','DIM_DateId','DIM_CustomerId','DIM_RoleId','DIM_StatusId','StartDate','EndDate'), (aid, 20260101, cid, roles[role], 'status1', '2026-01-01', '2026-12-31'))
            oid = 'demo_owner_' + str(i)
            insert_once(cur, 'DIM_ServiceOwners', oid, ('DIM_ServiceOwnersId','DIM_DateId','DIM_ServiceId','DIM_CustomerId','StartDate','EndDate'), (oid, 20260101, services[service], cid, '2026-01-01', '2026-12-31'))
        for i in range(20):
            cid, aid = f'demo_neighbor_{i}', f'demo_account_{i}'
            insert_once(cur, 'DIM_Customer', cid, ('DIM_CustomerId','DIM_DateId','CustomerName','CustomerLastName','CustomerDateBirth','CustomerStartDate','CustomerFraction'), (cid, 20250101, f'PersonaFicticia{i}', 'Ejemplo', '1985-01-01', '2025-01-01', FRACTIONS[i % 6]))
            insert_once(cur, 'DIM_Account', aid, ('DIM_AccountId','DIM_DateId','DIM_CustomerId','DIM_RoleId','DIM_StatusId','StartDate','EndDate'), (aid, 20250101, cid, roles[ROLES[i % 6]], 'status1', '2025-01-01', 's/n'))
        current = datetime.now(pytz.timezone('America/Mexico_City'))
        for year in (2025, 2026):
            for j, service in enumerate(SERVICES):
                sid = f'demo_service_{year}_{service}'
                cost = 200 + j * 100
                insert_once(cur, 'DIM_ServiceDetails', sid, ('DIM_ServiceDetailsId','DIM_DateId','DIM_ServiceId','ServiceDetailesType','amount','DIM_StatusId','StartDate','EndDate'), (sid, year*10000+101, services[service], 'anual', cost, 'status6', f'{year}-01-01', f'{year}-12-31'))
                for i in range(20):
                    month = current.month if year == current.year and i == 0 else i % 12 + 1
                    date_id = year * 10000 + month * 100 + 1
                    rid = f'demo_revenue_{year}_{service}_{i}'
                    complete = i % 2 == 0
                    insert_once(cur, 'FACT_Revenue', rid, ('FACT_RevenueId','DIM_DateId','DIM_AccountId','DIM_ServiceDetailsId','DIM_MovementId','DIM_StatusId','amount'), (rid, date_id, f'demo_account_{i}', sid, 'd3e7d32b-d440-5048', 'status4' if complete else 'status5', cost if complete else cost / 2))
        db.save_changes()
    print('Datos demo aplicados correctamente')


if __name__ == '__main__':
    main()
