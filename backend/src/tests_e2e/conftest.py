import os
import sys
import pytest
from pathlib import Path

# Asegurar backend en sys.path
backend_path = Path(__file__).resolve().parent.parent.parent
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app import app
from src.utils.conexion import Conexion, get_pool_status, DatabaseError


@pytest.fixture(scope="session", autouse=True)
def verify_real_sqlserver_connection():
    """Verifica que los tests E2E se ejecuten exclusivamente contra una instancia real de SQL Server."""
    conn = Conexion()
    try:
        _, cursor = conn.conexion()
        cursor.execute("SELECT @@VERSION, DB_NAME()")
        version, db_name = cursor.fetchone()
        assert any(name in version for name in ("Microsoft SQL Server", "Microsoft SQL Azure")), f"Motor SQL inesperado: {version}"
        print(f"\n[E2E SETUP] Conectado exitosamente a SQL Server real: {db_name}")
    finally:
        conn.close_conexion()


@pytest.fixture(autouse=True)
def assert_no_pool_leaks():
    """Garantiza que ninguna prueba deje conexiones huérfanas tomadas del QueuePool."""
    # Pre-test check
    initial_status = get_pool_status()
    assert initial_status["checkedout"] == 0, f"Pool leak antes del test: {initial_status}"
    
    yield
    
    # Post-test check
    final_status = get_pool_status()
    assert final_status["checkedout"] == 0, f"Pool leak después del test: {final_status}"


@pytest.fixture(autouse=True)
def clean_e2e_data():
    """Limpia cualquier dato creado con prefijo e2e_ en orden inverso de FKs."""
    def _clean():
        conn = Conexion()
        try:
            _, cur = conn.conexion()
            cur.execute("DELETE FROM DIM_CashCut WHERE DIM_CashCutId LIKE 'e2e_%'")
            cur.execute("DELETE FROM FACT_Revenue WHERE FACT_RevenueId LIKE 'e2e_%' OR DIM_AccountId IN (SELECT DIM_AccountId FROM DIM_Account WHERE DIM_CustomerId LIKE 'e2e_%')")
            cur.execute("DELETE FROM DIM_ServiceOwners WHERE DIM_ServiceOwnersId LIKE 'e2e_%' OR DIM_CustomerId LIKE 'e2e_%'")
            cur.execute("DELETE FROM DIM_ServiceDetails WHERE DIM_ServiceDetailsId LIKE 'e2e_%'")
            cur.execute("DELETE FROM DIM_Account WHERE DIM_AccountId LIKE 'e2e_%' OR DIM_CustomerId LIKE 'e2e_%'")
            cur.execute("DELETE FROM DIM_Customer WHERE DIM_CustomerId LIKE 'e2e_%'")
            conn.save_changes()
        finally:
            conn.close_conexion()

    _clean()
    yield
    _clean()


@pytest.fixture
def client():
    """Cliente de pruebas de Flask configurado para modo testing."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client
