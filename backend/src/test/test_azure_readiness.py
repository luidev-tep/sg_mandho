from src.utils.conexion import _build_odbc_connection_string
from src.dim_dates.dim_date import generar_anio_real


def test_sql_auth_and_odbc_escape(monkeypatch):
    for name in ('DB_ENCRYPT', 'DB_TRUST_CERT', 'DB_TRUSTED_CONNECTION'):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv('DB_USER', 'demo')
    monkeypatch.setenv('DB_PASSWORD', 'Pa;ss}word!')
    result = _build_odbc_connection_string()
    assert 'UID=demo;PWD={Pa;ss}}word!};' in result
    assert 'Trusted_Connection=yes' not in result
    assert 'Encrypt=yes;' in result and 'TrustServerCertificate=no;' in result


def test_calendar_leap_year():
    rows = generar_anio_real(2028)
    assert len(rows) == 366 and any(row[0] == 20280229 for row in rows)
