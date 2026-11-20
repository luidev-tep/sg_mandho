import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pyodbc

from src.utils.conexion import _build_odbc_connection_string, get_pool_status

BACKEND_DIR = Path(__file__).resolve().parents[2]
TEMP_DB_NAME = "sg_mandho_demo_test_" + uuid4().hex[:12]


def _connect_master():
    env_copy = {**os.environ, "DB_NAME": "master"}
    with patch.dict(os.environ, env_copy, clear=True):
        conn_str = _build_odbc_connection_string()
    return pyodbc.connect(conn_str, autocommit=True)


def _drop_temp_db(conn) -> None:
    cur = conn.cursor()
    cur.execute(
        f"""
        IF DB_ID(N'{TEMP_DB_NAME}') IS NOT NULL
        BEGIN
            ALTER DATABASE [{TEMP_DB_NAME}] SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
            DROP DATABASE [{TEMP_DB_NAME}];
        END
        """
    )
    cur.close()


def test_health_endpoint_returns_200_and_zero_checkedout(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert data["database"] == "up"
    assert data["pool"]["checkedout"] == 0
    assert get_pool_status()["checkedout"] == 0


def test_build_odbc_connection_string_azure_credentials_and_escaping():
    azure_env = {
        "DB_DRIVER": "ODBC Driver 18 for SQL Server",
        "DB_SERVER": "demo.database.windows.net,1433",
        "DB_NAME": "sg_mandho",
        "DB_USER": "sqladmin",
        "DB_PASSWORD": "Pa;ss}word!",
    }
    with patch.dict(os.environ, azure_env, clear=True):
        conn_str = _build_odbc_connection_string()

    assert "UID=sqladmin;PWD={Pa;ss}}word!};" in conn_str
    assert "Trusted_Connection=yes" not in conn_str
    assert "Encrypt=yes;" in conn_str
    assert "TrustServerCertificate=no;" in conn_str


def test_cors_allows_origin_when_url_frontend_has_trailing_slash():
    env = {
        **os.environ,
        "URL_FRONTEND": "http://localhost:5173/",
        "SECRET_KEY": os.environ.get("SECRET_KEY", "e2e-test-secret"),
    }
    code = (
        "from app import app; "
        "c = app.test_client(); "
        "r = c.options('/health', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'GET'}); "
        "assert r.headers.get('Access-Control-Allow-Origin') == 'http://localhost:5173', dict(r.headers); "
        "r2 = c.get('/health', headers={'Origin': 'http://localhost:5173'}); "
        "assert r2.status_code == 200; "
        "assert r2.headers.get('Access-Control-Allow-Origin') == 'http://localhost:5173', dict(r2.headers)"
    )
    res = subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(BACKEND_DIR),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert res.returncode == 0, f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"


def test_apply_schema_and_seed_demo_azure_idempotent_on_temp_db():
    demo_pwd = "DemoCongress2026!"
    master_conn = _connect_master()
    created = False
    try:
        cur = master_conn.cursor()
        cur.execute(f"CREATE DATABASE [{TEMP_DB_NAME}]")
        created = True
        cur.close()

        sub_env = {
            **os.environ,
            "DB_NAME": TEMP_DB_NAME,
            "DEMO_ADMIN_PASSWORD": demo_pwd,
            "RECAPTCHA_ENABLED": "false",
            "SECRET_KEY": os.environ.get("SECRET_KEY", "e2e-temp-db-secret"),
        }

        # 1a y 2a ejecución consecutiva de apply_schema.py + seed_demo_azure.py
        for attempt in (1, 2):
            res_schema = subprocess.run(
                [sys.executable, str(BACKEND_DIR / "scripts" / "apply_schema.py")],
                cwd=str(BACKEND_DIR),
                env=sub_env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert res_schema.returncode == 0, (
                f"apply_schema falló en intento {attempt}:\n{res_schema.stdout}\n{res_schema.stderr}"
            )

            res_seed = subprocess.run(
                [sys.executable, str(BACKEND_DIR / "scripts" / "seed_demo_azure.py")],
                cwd=str(BACKEND_DIR),
                env=sub_env,
                capture_output=True,
                text=True,
                check=False,
            )
            assert res_seed.returncode == 0, (
                f"seed_demo_azure falló en intento {attempt}:\n{res_seed.stdout}\n{res_seed.stderr}"
            )

            if attempt == 1:
                counts_first = _fetch_temp_db_counts(sub_env)
            else:
                counts_second = _fetch_temp_db_counts(sub_env)
                assert counts_second == counts_first, (
                    f"La segunda ejecución duplicó o alteró filas: {counts_first} vs {counts_second}"
                )

        # Verificar login real de demo_delegado, demo_agua y demo_subdelegado sobre sg_mandho_demo_test
        verify_code = f"""
import os
from app import app
from src.utils.conexion import get_pool_status

client = app.test_client()
accounts = [
    ("demo_delegado", "delegado", "centro"),
    ("demo_agua", "comitiva", "tepetate"),
    ("demo_subdelegado", "subdelegado", "cerritos"),
]
for username, role, manzana in accounts:
    resp = client.post("/api/security/login/", json={{
        "name": username,
        "password": "{demo_pwd}",
        "role": role,
        "manzana": manzana,
    }})
    assert resp.status_code == 200, f"Login fallo para {{username}}: {{resp.status_code}} {{resp.get_data(as_text=True)}}"
    payload = resp.get_json()
    assert payload["body"]["tokens"]["access_token"]
assert get_pool_status()["checkedout"] == 0
"""
        res_login = subprocess.run(
            [sys.executable, "-c", verify_code],
            cwd=str(BACKEND_DIR),
            env=sub_env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert res_login.returncode == 0, f"Login demo falló:\n{res_login.stdout}\n{res_login.stderr}"
    finally:
        if created:
            _drop_temp_db(master_conn)
        master_conn.close()


def _fetch_temp_db_counts(sub_env: dict) -> dict[str, int]:
    with patch.dict(os.environ, sub_env, clear=True):
        conn_str = _build_odbc_connection_string()
    conn = pyodbc.connect(conn_str, autocommit=True)
    try:
        cur = conn.cursor()
        tables = (
            "DIM_Date",
            "DIM_Customer",
            "DIM_Account",
            "DIM_ServiceOwners",
            "DIM_ServiceDetails",
            "FACT_Revenue",
        )
        return {
            table: cur.execute(f"SELECT COUNT(*) FROM [{table}]").fetchval()
            for table in tables
        }
    finally:
        conn.close()
