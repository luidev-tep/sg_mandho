from flask_jwt_extended import create_access_token
from app import app
from src.utils.conexion import Conexion
from src.analytics_reports.repository.PaymentProcesor import PaymentProcessor
from src.users.repository.home_info import get_admins_home_info
from src.users.repository.show import get_users_with_filters
from src.analytics_reports.repository.get_analytics import GetAnalytics


def test_all_10_views_execute_without_tsql_errors():
    """Ejecuta una consulta real sobre cada una de las 10 vistas creadas en SQL Server."""
    views = [
        "SecurityUsers",
        "VISTA_CLIENTES_ACTIVOS",
        "VISTA_PAGOS_AGUA",
        "VISTA_PAGOS_DELEGACION",
        "VISTA_PAGOS_FERIA",
        "VISTA_PAGOS_PANTEON",
        "VISTA_PAGOS_DETALLADO_AGUA",
        "VISTA_PAGOS_DETALLADO_DELEGACION",
        "VISTA_PAGOS_DETALLADO_FERIA",
        "VISTA_PAGOS_DETALLADO_PANTEON"
    ]

    conn = Conexion()
    try:
        _, cur = conn.conexion()
        for view_name in views:
            cur.execute(f"SELECT TOP 5 * FROM {view_name}")
            rows = cur.fetchall()
            assert rows is not None, f"La vista {view_name} no retornó resultado"
            # Verificar que las columnas tengan nombres asignados (sin fallos de alias)
            col_names = [col[0] for col in cur.description]
            assert len(col_names) > 0, f"La vista {view_name} no tiene columnas"
            assert None not in col_names, f"La vista {view_name} tiene columnas sin nombre"
    finally:
        conn.close_conexion()


def test_payment_processor_year_cast_join_works_in_sqlserver():
    """Valida la ejecución real de PaymentProcessor con CAST(d.Year AS NVARCHAR(10))."""
    proc = PaymentProcessor()
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT TOP 1 DIM_CustomerId FROM DIM_Customer WHERE CustomerEndDate = 's/n'")
        row = cur.fetchone()
        cust_id = row[0] if row else "non_existent"
    finally:
        conn.close_conexion()

    resultado = proc.get_all_data_payments(cust_id)
    assert isinstance(resultado, dict)
    assert "completos" in resultado
    assert "pendientes" in resultado


def test_home_info_concat_and_users_filter_not_equal_sn():
    """Valida la consulta de home_info con CONCAT(...) y el filtro SQL Server <> 's/n'."""
    # 1. Probar CONCAT en home_info
    data = get_admins_home_info()
    assert isinstance(data, list)

    # 2. Probar filtro <> 's/n' en get_users_with_filters
    filtros = {
        "CustomerEndDate": True, # Exige <> 's/n'
        "CustomerFraction": []
    }
    data_filter = get_users_with_filters(filtros)
    assert isinstance(data_filter, list)


def test_realtime_search_top_50_and_case_insensitive(client):
    """Prueba la búsqueda en tiempo real usando SELECT TOP 50 a través de la API con token JWT."""
    with app.app_context():
        token = create_access_token(identity="e2e_tester", additional_claims={"role": "delegado", "service": "general", "fraction": "centro"})
    
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/search/search_client/?q=mar", headers=headers)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data["status"] == "success"
    assert "results" in json_data
    assert len(json_data["results"]) <= 50


def test_analytics_isnull_and_cross_year_queries():
    """Valida que la consulta de ingresos por mes use ISNULL(...) en lugar de IFNULL(...) sin error T-SQL."""
    analytics = GetAnalytics()
    # Ejecuta consulta de facturas por mes que contiene ISNULL(SUM(vw.amount), 0)
    resultado = analytics.get_bills_by_month("M01", "panteon", "Y25")
    assert isinstance(resultado, list)
    for mes_data in resultado:
        assert "revenue" in mes_data
        assert isinstance(mes_data["revenue"], (int, float))
