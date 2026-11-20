import concurrent.futures
from src.utils.conexion import Conexion, get_pool_status
from src.accounts.services.validate import validate_account, has_active_account
from src.payments.services.validate_payment import ValidatePayment
from src.payments.repository.read_payments import ReadPayment
from src.dim_serviceonwers.repository.show import get_ServiceOnwers_by_name
from src.dim_dates.dim_date import DIM_DATE
from src.users.repository.show import get_all_users, get_users_with_filters
from src.accounts.repository.show import show_account
from src.analytics_reports.repository.PaymentProcesor import PaymentProcessor


def test_connection_connects_to_sqlserver_engine():
    """Valida la conexión directa al motor SQL Server y la base de datos configurada."""
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT @@VERSION, DB_NAME()")
        row = cur.fetchone()
        assert row is not None
        assert "Microsoft SQL Server" in row[0]
        assert row[1].lower() == "sg_mandho"
    finally:
        conn.close_conexion()


def test_pool_reuses_physical_connection_and_checks_in():
    """Verifica que conexiones secuenciales reutilicen el SPID físico del pool y hagan check-in."""
    spids = []
    for _ in range(10):
        conn = Conexion()
        try:
            _, cur = conn.conexion()
            cur.execute("SELECT @@SPID")
            spid = cur.fetchone()[0]
            spids.append(spid)
            assert get_pool_status()["checkedout"] == 1
        finally:
            conn.close_conexion()
        assert get_pool_status()["checkedout"] == 0

    # Al reutilizar conexiones en el pool, el SPID físico debe mantenerse constante
    assert len(set(spids)) == 1, f"Se esperaban SPIDs reutilizados pero se obtuvieron: {set(spids)}"


def test_pool_does_not_exhaust_after_sequential_repository_calls():
    """Ejecuta llamadas a las funciones donde se corrigieron fugas y valida checkedout == 0."""
    vp = ValidatePayment()
    rp = ReadPayment()
    dd = DIM_DATE()
    proc = PaymentProcessor()

    # Obtener un usuario y fecha existentes para pruebas
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT TOP 1 DIM_CustomerId, DIM_DateId FROM DIM_Customer")
        cust_row = cur.fetchone()
        sample_cust_id = cust_row[0] if cust_row else "non_existent"
        sample_date_id = cust_row[1] if cust_row and cust_row[1] else 20260101
    finally:
        conn.close_conexion()

    # Ejecutar 20 iteraciones de las funciones que anteriormente tenían fugas de conexión
    for _ in range(20):
        validate_account(sample_cust_id)
        has_active_account(sample_cust_id)
        vp.is_account_active(sample_cust_id)
        rp.get_validation_payment(sample_cust_id, "agua", "2025")
        get_ServiceOnwers_by_name(sample_cust_id)
        dd.get_by_id(sample_date_id)
        get_all_users()
        get_users_with_filters({"CustomerEndDate": False, "CustomerFraction": []})
        show_account({"id_account": "", "filters": {}})
        proc.get_all_data_payments(sample_cust_id)

        # Tras cada ciclo, el pool DEBE tener cero conexiones tomadas
        status = get_pool_status()
        assert status["checkedout"] == 0, f"Fuga detectada durante iteraciones de repositorio: {status}"


def test_pool_concurrent_threads_stress():
    """Prueba 25 hilos concurrentes compitiendo por un pool de tamaño 5 + 10 overflow sin timeouts."""
    def worker(worker_id: int):
        conn = Conexion()
        try:
            _, cur = conn.conexion()
            cur.execute(f"SELECT COUNT(*), {worker_id} FROM DIM_Customer")
            result = cur.fetchone()
            assert result[0] >= 0
            return result[1]
        finally:
            conn.close_conexion()

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = [executor.submit(worker, i) for i in range(25)]
        results = [f.result(timeout=15) for f in concurrent.futures.as_completed(futures)]

    assert len(results) == 25
    assert get_pool_status()["checkedout"] == 0


def test_uncommitted_changes_rollback_on_close_conexion():
    """Verifica que operaciones no confirmadas con save_changes() se reviertan al llamar a close_conexion()."""
    test_id = "e2e_cust_rollback_test"
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, CustomerName, CustomerLastName,
                CustomerDateBirth, CustomerStartDate
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (test_id, "NombreRollback", "ApellidoRollback", "1990-01-01", "2026-01-01")
        )
        # Omitimos deliberadamente conn.save_changes()
    finally:
        conn.close_conexion()

    # Abrir una nueva conexión y verificar que el registro NO fue insertado
    check_conn = Conexion()
    try:
        _, check_cur = check_conn.conexion()
        check_cur.execute("SELECT COUNT(*) FROM DIM_Customer WHERE DIM_CustomerId = ?", (test_id,))
        count = check_cur.fetchone()[0]
        assert count == 0, "El registro no comiteado debió ser revertido (rollback) automáticamente."
    finally:
        check_conn.close_conexion()
