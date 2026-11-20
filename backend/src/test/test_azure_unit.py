import importlib
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

BACKEND = Path(__file__).resolve().parents[2]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from src.dim_dates.dim_date import generar_anio_real
from src.utils.conexion import _build_odbc_connection_string


def test_build_odbc_connection_string_escapes_password_and_disables_trusted_conn():
    env = {
        "DB_DRIVER": "ODBC Driver 18 for SQL Server",
        "DB_SERVER": "myserver.database.windows.net,1433",
        "DB_NAME": "sg_mandho",
        "DB_USER": "azureadmin",
        "DB_PASSWORD": "Pa;ss}word!",
    }
    with patch.dict(os.environ, env, clear=True):
        conn_str = _build_odbc_connection_string()

    assert "UID=azureadmin;" in conn_str
    assert "PWD={Pa;ss}}word!};" in conn_str
    assert "Trusted_Connection=yes" not in conn_str
    assert "Encrypt=yes;" in conn_str
    assert "TrustServerCertificate=no;" in conn_str


def test_build_odbc_connection_string_local_trusted_defaults():
    env = {
        "DB_DRIVER": "ODBC Driver 17 for SQL Server",
        "DB_SERVER": r"localhost\SQLEXPRESS",
        "DB_NAME": "sg_mandho",
    }
    with patch.dict(os.environ, env, clear=True):
        conn_str = _build_odbc_connection_string()

    assert "Trusted_Connection=yes;" in conn_str
    assert "UID=" not in conn_str
    assert "Encrypt=no;" in conn_str
    assert "TrustServerCertificate=yes;" in conn_str


def test_build_odbc_connection_string_explicit_trusted_false_uses_credentials():
    env = {
        "DB_USER": "sa",
        "DB_PASSWORD": "MandhoDev2026!",
        "DB_ENCRYPT": "no",
        "DB_TRUST_CERT": "yes",
        "DB_TRUSTED_CONNECTION": "false",
    }
    with patch.dict(os.environ, env, clear=True):
        conn_str = _build_odbc_connection_string()

    assert "UID=sa;" in conn_str
    assert "PWD={MandhoDev2026!};" in conn_str
    assert "Trusted_Connection=yes" not in conn_str
    assert "Encrypt=no;" in conn_str
    assert "TrustServerCertificate=yes;" in conn_str


def test_explicit_trusted_false_without_user_does_not_enable_integrated_auth():
    with patch.dict(os.environ, {"DB_TRUSTED_CONNECTION": "false"}, clear=True):
        conn_str = _build_odbc_connection_string()
    assert "Trusted_Connection=yes" not in conn_str


def test_managed_identity_uses_secure_odbc_options():
    with patch.dict(os.environ, {"DB_AUTHENTICATION": "ActiveDirectoryMsi"}, clear=True):
        conn_str = _build_odbc_connection_string()
    assert "Authentication=ActiveDirectoryMsi;" in conn_str
    assert "Encrypt=yes;" in conn_str
    assert "TrustServerCertificate=no;" in conn_str
    assert "Trusted_Connection=yes" not in conn_str and "UID=" not in conn_str


def test_user_assigned_identity_provides_fresh_sql_access_token(monkeypatch):
    import struct
    from types import SimpleNamespace
    from src.utils import conexion
    from azure import identity

    tokens = iter(["first-token", "second-token"])
    calls = []

    class FakeCredential:
        def __init__(self, client_id):
            assert client_id == "identity-client-id"

        def get_token(self, scope):
            calls.append(scope)
            return SimpleNamespace(token=next(tokens))

    monkeypatch.setattr(identity, "ManagedIdentityCredential", FakeCredential)
    monkeypatch.setenv("DB_AUTHENTICATION", "ManagedIdentity")
    monkeypatch.setenv("AZURE_CLIENT_ID", "identity-client-id")
    conexion.dispose_engine()
    try:
        engine = conexion._get_engine()
        for expected in ("first-token", "second-token"):
            args = ["DRIVER={test};Trusted_Connection=Yes"]
            params = {}
            for listener in engine.dialect.dispatch.do_connect:
                listener(engine.dialect, None, args, params)
            assert "Trusted_Connection" not in args[0]
            token_data = params["attrs_before"][1256]
            size = struct.unpack_from("<I", token_data)[0]
            assert token_data[4:4 + size].decode("utf-16-le") == expected
        assert calls == ["https://database.windows.net/.default"] * 2
    finally:
        conexion.dispose_engine()


def test_generar_anio_real_leap_and_standard_years():
    days_2026 = generar_anio_real(2026)
    days_2028 = generar_anio_real(2028)
    assert len(days_2026) == 365
    assert len(days_2028) == 366
    assert any(row[0] == 20280229 for row in days_2028)


def test_health_endpoint_ok_and_degraded_without_db():
    import app as app_module

    mock_db = MagicMock()
    mock_db.__enter__.return_value = mock_db
    mock_db.__exit__.return_value = False

    with patch.object(app_module, "Conexion", return_value=mock_db), patch.object(
        app_module,
        "get_pool_status",
        return_value={"size": 5, "checkedin": 1, "checkedout": 0, "overflow": 0},
    ):
        client = app_module.app.test_client()
        resp = client.get("/health")
        assert resp.status_code == 200
        body = resp.get_json()
        assert body["status"] == "ok"
        assert body["database"] == "up"
        assert body["pool"]["checkedout"] == 0

    with patch.object(app_module, "Conexion", side_effect=RuntimeError("db unreachable")):
        client = app_module.app.test_client()
        resp = client.get("/health")
        assert resp.status_code == 503
        body = resp.get_json()
        assert body == {"status": "degraded", "database": "down"}


def test_cors_strips_trailing_slash_from_url_frontend():
    import app as app_module

    saved_url = os.environ.get("URL_FRONTEND")
    os.environ["URL_FRONTEND"] = "http://localhost:5173/"
    try:
        reloaded = importlib.reload(app_module)
        client = reloaded.app.test_client()
        resp = client.options(
            "/health",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        assert resp.headers.get("Access-Control-Allow-Origin") == "http://localhost:5173"
    finally:
        if saved_url is None:
            os.environ.pop("URL_FRONTEND", None)
        else:
            os.environ["URL_FRONTEND"] = saved_url
        importlib.reload(app_module)
