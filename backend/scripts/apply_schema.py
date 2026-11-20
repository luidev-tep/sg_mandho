"""Bootstrap a fresh database for local demos; production migrations use Flyway."""
import re
import sys
from pathlib import Path

import pyodbc
from dotenv import load_dotenv

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
load_dotenv(BACKEND / '.env')
from src.utils.conexion import _build_odbc_connection_string

MIGRATIONS = ('V1__initial_schema.sql', 'V2__seed_core_catalogs.sql',
              'V3__harden_revenue_and_utc_defaults.sql',
              'R__views_security_and_clients.sql', 'R__views_payments.sql')


def main():
    # This bootstrap does not create Flyway history. Never run on an existing
    # partially populated schema: only a complete V1 schema can be reused.
    conn = pyodbc.connect(_build_odbc_connection_string(), autocommit=False)
    try:
        cursor = conn.cursor()
        exists = cursor.execute("SELECT OBJECT_ID('dbo.DIM_Role', 'U')").fetchval() is not None
        if exists:
            count = cursor.execute("SELECT COUNT(*) FROM sys.tables WHERE name IN ('DIM_Role','DIM_Status','DIM_Date','DIM_Customer','DIM_Account','DIM_Service','DIM_ServiceDetails','DIM_ServiceOwners','DIM_Movement','FACT_Revenue','DIM_CashCut')").fetchval()
            if count != 11:
                raise RuntimeError('Esquema incompleto: use Flyway o una base vacía')
        for filename in MIGRATIONS:
            if exists and filename.startswith('V1__'):
                continue
            sql = (BACKEND / 'db' / 'migrations' / filename).read_text(encoding='utf-8')
            for batch in re.split(r'^\s*GO\s*(?:--.*)?$', sql, flags=re.I | re.M):
                if batch.strip():
                    cursor.execute(batch)
            print(f'Aplicado: {filename}')
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    main()
