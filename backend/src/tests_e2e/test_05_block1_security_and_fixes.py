from flask_jwt_extended import create_access_token, create_refresh_token, decode_token
from app import app
from src.utils.conexion import Conexion, get_pool_status
from src.dim_dates.dim_date import DIM_DATE, generar_anio_real
from src.payments.repository.read_payments import ReadPayment
from src.payments.payment import PaymentCrud
from src.security.security import SecurityUsers


def test_sqli_blocked_in_read_payments_by_customer_id(client):
    """Bloquea cualquier nombre de servicio fuera de allowlist en VISTA_PAGOS_DETALLADO_*."""
    with app.app_context():
        token = create_access_token(
            identity="e2e_tester",
            additional_claims={"role": "delegado", "service": "delegado", "fraction": "centro", "name": "e2e_delegado"},
        )
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.post(
        "/api/payment/read/",
        json={
            "DIM_CustomerId": "e2e_any_cust",
            "serviceName": "agua; SELECT 1--",
            "service_type": "consumo",
            "Year": "2026",
        },
        headers=headers,
    )
    assert resp.status_code == 400, f"Se esperaba 400 ante SQLi, se obtuvo {resp.status_code}: {resp.get_data(as_text=True)}"
    assert get_pool_status()["checkedout"] == 0


def test_read_payments_with_filters_no_pool_leak_on_invalid_input():
    """Garantiza cero fugas del QueuePool cuando get_payments_with_filters recibe servicio o fecha inválidos."""
    rp = ReadPayment()
    for _ in range(20):
        status_bad_srv, data_bad_srv = rp.get_payments_with_filters("servicio_invalido", {"DIM_Date": 2026})
        assert status_bad_srv == 400 and data_bad_srv == []

        status_no_date, data_no_date = rp.get_payments_with_filters("agua", {})
        assert status_no_date == 404 and data_no_date == []

        status_empty_date, data_empty_date = rp.get_payments_with_filters("agua", {"DIM_Date": ""})
        assert status_empty_date == 404 and data_empty_date == []

    assert get_pool_status()["checkedout"] == 0


def test_weak_password_rejected_on_create_owner():
    """Verifica que insert_new_Onwer y validate_password_with_feedback rechacen contraseñas débiles (bug dict unpacking)."""
    sec = SecurityUsers()
    check = sec.validate_password_with_feedback("1")
    assert check["is_valid"] is False
    assert isinstance(check["errors"], str) and len(check["errors"]) > 0

    cust_id = "e2e_cust_weak_pwd"
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, CustomerName, CustomerLastName,
                CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (cust_id, "Elena", "Seguridad", "1990-02-10", "2026-01-01", "s/n", "centro"),
        )
        conn.save_changes()
    finally:
        conn.close_conexion()

    status, msg = sec.insert_new_Onwer(
        {
            "DIM_CustomerId": cust_id,
            "CustomerFraction": "centro",
            "username": "e2e_elena_weak",
            "password": "1",
            "RoleName": "subdelegado",
            "serviceName": "personas",
        }
    )
    assert status == 400, f"Debió rechazar contraseña débil con 400, devolvió {status}: {msg}"


def test_subdelegado_validate_user_post_accepts_valid_fraction():
    """Verifica que subdelegado valida serviceName='personas' y fracción válida (no CustomerFraction in {'personas'})."""
    sec = SecurityUsers()

    status_ok, msg_ok = sec.validate_user_post(
        {
            "RoleName": "subdelegado",
            "CustomerFraction": "centro",
            "serviceName": "personas",
        }
    )
    assert status_ok == 200, f"Falló validación de subdelegado en centro: {status_ok} {msg_ok}"

    status_bad_role, _ = sec.validate_user_post(
        {
            "RoleName": "rol_inventado",
            "CustomerFraction": "centro",
            "serviceName": "personas",
        }
    )
    assert status_bad_role == 400

    status_bad_fraction, _ = sec.validate_user_post(
        {
            "RoleName": "subdelegado",
            "CustomerFraction": "manzana_inexistente",
            "serviceName": "personas",
        }
    )
    assert status_bad_fraction == 409


def test_refresh_token_preserves_name_claim(client):
    """El access_token renovado en /api/security/refresh_token/ debe conservar el claim 'name'."""
    with app.app_context():
        refresh = create_refresh_token(
            identity="e2e_owner_refresh",
            additional_claims={
                "role": "comitiva",
                "service": "agua",
                "fraction": "tepetate",
                "name": "demo_user",
            },
        )

    resp = client.post(
        "/api/security/refresh_token/",
        headers={"Authorization": f"Bearer {refresh}"},
    )
    assert resp.status_code == 200, f"Error en refresh_token: {resp.get_data(as_text=True)}"
    new_access_token = resp.get_json()["body"]["data"]

    with app.app_context():
        decoded = decode_token(new_access_token)
    assert decoded.get("name") == "demo_user"
    assert decoded.get("role") == "comitiva"
    assert decoded.get("service") == "agua"
    assert decoded.get("fraction") == "tepetate"


def test_multi_installment_3_payments_atomic_completion_and_overpayment_rejected():
    """
    Crea cliente, cuenta activa y servicio e2e de $300.
    Registra 3 abonos ($100 + $100 + $100), verifica que los 3 queden en status4 (completo),
    y verifica rechazo de montos negativos (-50) y sobrepagos (500).
    """
    dim_date = DIM_DATE()
    date_id = dim_date.dateId or 20260101
    year_str = str(dim_date.full_date[0])
    cust_id = "e2e_cust_multi_pay"
    acc_id = "e2e_acc_multi_pay"
    sd_id = "e2e_sd_multi_pay"
    srv_type = "e2e_cuota_parcial"

    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT DIM_RoleId FROM DIM_Role WHERE RoleName = 'vecino'")
        role_id = cur.fetchone()[0]
        cur.execute("SELECT DIM_ServiceId FROM DIM_Service WHERE ServiceName = 'feria'")
        service_id = cur.fetchone()[0]

        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, DIM_DateId, CustomerName, CustomerMiddleName, CustomerLastName, CustomerSecondLastName,
                CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction, CustomerAddress, CustomerNumberExt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (cust_id, date_id, "Carlos", "Prueba", "Parcial", "Tres", "1990-05-01", f"{year_str}-01-01", "s/n", "centro", "Calle Uno", "10"),
        )
        cur.execute(
            """
            INSERT INTO DIM_Account (
                DIM_AccountId, DIM_DateId, DIM_CustomerId, DIM_RoleId, DIM_StatusId, StartDate, EndDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (acc_id, date_id, cust_id, role_id, "status1", f"{year_str}-01-01", "s/n"),
        )
        cur.execute(
            """
            INSERT INTO DIM_ServiceDetails (
                DIM_ServiceDetailsId, DIM_DateId, DIM_ServiceId, ServiceDetailesType, amount, DIM_StatusId, StartDate, EndDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (sd_id, date_id, service_id, srv_type, 300.0, "status6", f"{year_str}-01-01", f"{year_str}-12-31"),
        )
        conn.save_changes()
    finally:
        conn.close_conexion()

    payment_crud = PaymentCrud()
    base_payload = {
        "DIM_AccountId": acc_id,
        "DIM_CustomerId": cust_id,
        "ServiceName": "feria",
        "serviceDetailsType": srv_type,
        "AnioPago": year_str,
        "movementName": "ingreso",
        "amount": 300.0,
    }

    # 1er abono ($100) -> crear_pago -> pendiente (status5)
    c1, m1, _ = payment_crud.create_payment({**base_payload, "entrada": "crear_pago", "FactAmount": 100.0})
    assert c1 == 201, f"Fallo 1er abono: {c1} {m1}"

    # Negativo rechazado (-50)
    c_neg, _, _ = payment_crud.create_payment({**base_payload, "entrada": "", "FactAmount": -50.0})
    assert c_neg == 400

    # 2do abono ($100) -> pendiente (status5)
    c2, m2, _ = payment_crud.create_payment({**base_payload, "entrada": "", "FactAmount": 100.0})
    assert c2 == 201, f"Fallo 2do abono: {c2} {m2}"

    # Sobrepago rechazado ($500 cuando faltan $100)
    c_over, _, _ = payment_crud.create_payment({**base_payload, "entrada": "", "FactAmount": 500.0})
    assert c_over == 400

    # 3er abono ($100) -> completo (status4) en los 3 registros atómicamente
    c3, m3, data3 = payment_crud.create_payment({**base_payload, "entrada": "", "FactAmount": 100.0})
    assert c3 == 201, f"Fallo 3er abono: {c3} {m3}"
    assert isinstance(data3, list) and len(data3) >= 1

    check_conn = Conexion()
    try:
        _, cur = check_conn.conexion()
        cur.execute(
            "SELECT DIM_StatusId, amount FROM FACT_Revenue WHERE DIM_AccountId = ? AND DIM_ServiceDetailsId = ?",
            (acc_id, sd_id),
        )
        rows = cur.fetchall()
        assert len(rows) == 3, f"Se esperaban 3 abonos registrados, hay {len(rows)}: {rows}"
        assert all(r[0] == "status4" for r in rows), f"Todos los abonos debieron quedar en status4: {rows}"
        assert sum(r[1] for r in rows) == 300.0
    finally:
        check_conn.close_conexion()


def test_realtime_search_manzana_and_street_not_swapped(client):
    """Verifica que /api/search/search_client/ mapee correctamente CustomerAddress->street y CustomerFraction->manzana."""
    cust_id = "e2e_cust_search_map"
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, CustomerName, CustomerMiddleName, CustomerLastName, CustomerSecondLastName,
                CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction, CustomerAddress, CustomerNumberExt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (cust_id, "XimenaSearchE2E", "s/n", "Mapa", "Test", "1992-03-15", "2026-01-01", "s/n", "centro", "Calle Reforma", "42"),
        )
        conn.save_changes()
    finally:
        conn.close_conexion()

    with app.app_context():
        token = create_access_token(
            identity="e2e_tester",
            additional_claims={"role": "delegado", "service": "delegado", "fraction": "centro", "name": "e2e_delegado"},
        )
    resp = client.get("/api/search/search_client/?q=ximenasearche2e", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    results = resp.get_json()["results"]
    matched = [r for r in results if r["id"] == cust_id]
    assert len(matched) == 1
    data = matched[0]["data"]
    assert data["street"] == "Calle Reforma"
    assert data["manzana"] == "centro"


def test_leap_year_2028_generates_366_days():
    """generar_anio_real debe generar 366 días en años bisiestos incluyendo 20280229."""
    days = generar_anio_real(2028)
    assert len(days) == 366
    date_ids = {row[0] for row in days}
    assert 20280229 in date_ids


def test_batch_payment_rejects_cross_comitiva_item(client):
    """POST /api/payment/create/ con lista debe rechazar 403 si cualquier elemento pertenece a otra comitiva."""
    with app.app_context():
        token = create_access_token(
            identity="e2e_agua_owner",
            additional_claims={"role": "comitiva", "service": "agua", "fraction": "tepetate", "name": "e2e_agua"},
        )

    payload = [
        {"ServiceName": "agua", "DIM_AccountId": "a1", "DIM_CustomerId": "c1", "serviceDetailsType": "consumo", "AnioPago": "2026", "movementName": "ingreso", "entrada": "check_list", "FactAmount": 0, "amount": 360, "DIM_OnwerCustomerId": "o1"},
        {"ServiceName": "panteon", "DIM_AccountId": "a1", "DIM_CustomerId": "c1", "serviceDetailsType": "faena", "AnioPago": "2026", "movementName": "ingreso", "entrada": "check_list", "FactAmount": 0, "amount": 300, "DIM_OnwerCustomerId": "o1"},
    ]
    resp = client.post("/api/payment/create/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
