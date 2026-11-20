from src.utils.conexion import Conexion
from src.security.repository.user_info import insert_onwer_info
from src.payments.repository.cash_cut_querys import create_cash_cut_register
from src.payments.model.pending_paid import CashCutModel
from src.fact_revenues.repository.insert import insert_many_fact_revenues
from src.fact_revenues.Fact_revenue import factRevenueCrud
from src.fact_revenues.models.fact_revenue import FACT_Revenue
from src.dim_dates.dim_date import DIM_DATE


def test_insert_onwer_info_atomic_rollback_on_step3_failure():
    """
    Verifica que si insert_service_owner_info falla (paso 3),
    la cuenta creada y la actualización de credenciales del cliente
    sufran un ROLLBACK real en SQL Server (cero datos huérfanos).
    """
    cust_id = "e2e_cust_atomic_rollback"
    # 1. Crear cliente base para la prueba
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, CustomerName, CustomerLastName,
                CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction, username, password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (cust_id, "Pedro", "Rollback", "1985-05-15", "2026-01-01", "s/n", "centro", "pedro_orig", "pass_orig")
        )
        conn.save_changes()
    finally:
        conn.close_conexion()

    # 2. Intentar dar de alta como owner con un ServiceId INVÁLIDO para que falle el paso 3 (FK)
    data = {
        "DIM_CustomerId": cust_id,
        "CustomerFraction": "centro",
        "username": "pedro_nuevo_user",
        "password": "PasswordModerna123!",
        "RoleName": "comitiva",
        "serviceName": "servicio_inexistente_fk_fail",
        "StartDate": "2026-01-01",
        "EndDate": "2026-12-31"
    }

    status, msg = insert_onwer_info(data)
    assert status != 200, "La operación debió fallar por servicio inexistente"

    # 3. Comprobar que en la BD hubo ROLLBACK real:
    check_conn = Conexion()
    try:
        _, check_cur = check_conn.conexion()
        check_cur.execute("SELECT username, password FROM DIM_Customer WHERE DIM_CustomerId = ?", (cust_id,))
        cust_row = check_cur.fetchone()
        assert cust_row[0] == "pedro_orig", f"El username debió hacer rollback pero es: {cust_row[0]}"
        assert cust_row[1] == "pass_orig", "La contraseña debió hacer rollback"

        check_cur.execute("SELECT COUNT(*) FROM DIM_Account WHERE DIM_CustomerId = ?", (cust_id,))
        acc_count = check_cur.fetchone()[0]
        assert acc_count == 0, f"No debió crearse cuenta tras rollback, pero hay {acc_count}"

        check_cur.execute("SELECT COUNT(*) FROM DIM_ServiceOwners WHERE DIM_CustomerId = ?", (cust_id,))
        so_count = check_cur.fetchone()[0]
        assert so_count == 0, "No debió crearse service owner tras rollback"
    finally:
        check_conn.close_conexion()


def test_insert_onwer_info_atomic_commit_success():
    """
    Verifica que cuando todos los pasos son válidos, insert_onwer_info
    haga un COMMIT atómico persistiendo las 3 entidades coordinadas.
    """
    cust_id = "e2e_cust_atomic_commit"
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, CustomerName, CustomerLastName,
                CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction, username, password
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (cust_id, "Maria", "Commit", "1992-08-20", "2026-01-01", "s/n", "centro", "maria_orig", "pass_orig")
        )
        conn.save_changes()
    finally:
        conn.close_conexion()

    data = {
        "DIM_CustomerId": cust_id,
        "CustomerFraction": "centro",
        "username": "maria_admin",
        "password": "PasswordValida123!",
        "RoleName": "comitiva",
        "serviceName": "agua",
        "StartDate": "2026-01-01",
        "EndDate": "2026-12-31"
    }

    status, msg = insert_onwer_info(data)
    assert status == 200, f"Error al insertar owner atómicamente: {msg}"

    check_conn = Conexion()
    try:
        _, check_cur = check_conn.conexion()
        check_cur.execute("SELECT username FROM DIM_Customer WHERE DIM_CustomerId = ?", (cust_id,))
        assert check_cur.fetchone()[0] == "maria_admin"

        check_cur.execute("SELECT COUNT(*) FROM DIM_Account WHERE DIM_CustomerId = ? AND DIM_StatusId = 'status1'", (cust_id,))
        assert check_cur.fetchone()[0] == 1

        check_cur.execute("SELECT COUNT(*) FROM DIM_ServiceOwners WHERE DIM_CustomerId = ?", (cust_id,))
        assert check_cur.fetchone()[0] >= 1
    finally:
        check_conn.close_conexion()


def test_cash_cut_atomic_rollback_when_cash_cut_insert_fails():
    """
    Verifica que en el flujo transaccional de corte de caja, si la inserción
    en DIM_CashCut falla (paso 2), las facturas FACT_Revenue recién agregadas
    sufran un ROLLBACK real y no queden huérfanas en SQL Server.
    """
    dim_date = DIM_DATE()
    date_id = dim_date.dateId or 20260101

    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT TOP 1 DIM_AccountId FROM DIM_Account WHERE DIM_StatusId = 'status1'")
        acc_id = cur.fetchone()[0]
        cur.execute("SELECT TOP 1 DIM_ServiceDetailsId FROM DIM_ServiceDetails")
        sd_id = cur.fetchone()[0]
        cur.execute("SELECT TOP 1 DIM_MovementId FROM DIM_Movement WHERE LOWER(MovementName) = 'ingreso'")
        mov_id = cur.fetchone()[0]
    finally:
        conn.close_conexion()

    test_rev_id = "e2e_rev_cashcut_fail_test"
    revenue_obj = FACT_Revenue(
        FACT_RevenueId=test_rev_id,
        DIM_DateId=date_id,
        DIM_AccountId=acc_id,
        DIM_ServiceDetailsId=sd_id,
        DIM_MovementId=mov_id,
        DIM_StatusId="status4",
        amount=100.0
    )

    # Coordinar con Conexion() as tx: inserción de factura exitosa pero corte de caja fallido por FK
    with Conexion() as tx:
        ok_rev = insert_many_fact_revenues([revenue_obj], db=tx)
        assert ok_rev is True

        # Crear modelo de cash cut con DIM_ServiceOwnersId inexistente para forzar fallo FK
        bad_cut = CashCutModel(
            DIM_CashCutId="e2e_cut_fail_id",
            DIM_CountRegisters=1,
            DIM_ServiceDetailsId=sd_id,
            DIM_DateId=date_id,
            DIM_ServiceOwnersId="so_inexistente_fk_violation"
        )
        ok_cut = create_cash_cut_register(bad_cut, db=tx)
        assert ok_cut is False, "El corte debió fallar por FK inexistente"

        if not ok_cut:
            tx.rollback()

    # Verificar que el registro FACT_Revenue no existe en BD (rollback exitoso)
    check_conn = Conexion()
    try:
        _, check_cur = check_conn.conexion()
        check_cur.execute("SELECT COUNT(*) FROM FACT_Revenue WHERE FACT_RevenueId = ?", (test_rev_id,))
        count = check_cur.fetchone()[0]
        assert count == 0, "La factura debió ser revertida al fallar el registro del corte de caja."
    finally:
        check_conn.close_conexion()


def test_checklist_payments_atomic_rollback_on_status_update_failure():
    """
    Verifica que en el registro de pagos masivos (checklist), si falla el paso
    de actualización de estado en DIM_ServiceDetails, se ejecute un ROLLBACK real
    de todas las facturas FACT_Revenue recién insertadas.
    """
    fact_crud = factRevenueCrud()

    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT TOP 1 DIM_AccountId FROM DIM_Account WHERE DIM_StatusId = 'status1'")
        acc_id = cur.fetchone()[0]

        cur.execute("SELECT COUNT(*) FROM FACT_Revenue")
        count_before = cur.fetchone()[0]
    finally:
        conn.close_conexion()

    # Preparar payload de pago con un ServiceDetailsId inexistente para que falle la actualización
    invalid_sd_id = "e2e_sd_inexistente_para_rollback"
    data_format = [{
        "DIM_AccountId": acc_id,
        "amount": 250.0,
        "ServiceName": "feria"
    }]

    status, msg = fact_crud.insert_many_register(data_format, ServiceDetailesId=invalid_sd_id)
    assert status != 201, "La operación debió fallar por ID de servicio inválido"

    # Verificar que ninguna fila quedó en FACT_Revenue
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT COUNT(*) FROM FACT_Revenue")
        count_after = cur.fetchone()[0]
        assert count_after == count_before, "Las facturas no fueron revertidas ante fallo del segundo paso"
    finally:
        conn.close_conexion()
