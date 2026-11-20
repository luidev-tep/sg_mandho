import hashlib
from src.utils.conexion import Conexion, get_pool_status
from src.dim_dates.dim_date import DIM_DATE


def test_e2e_legacy_md5_login_auto_upgrades_to_scrypt_in_sqlserver(client):
    """
    Test E2E sin mocks:
    Inserta un administrador con hash MD5 heredado en SQL Server.
    Ejecuta el endpoint de login vía HTTP.
    Verifica que el usuario se autentica (200), emite tokens JWT,
    y que en la BD real su hash se actualizó automáticamente a formato seguro scrypt.
    """
    dim_date = DIM_DATE()
    year = dim_date.full_date[0]
    cust_id = "e2e_admin_md5_journey"
    plain_password = "AdminSecret2026!"
    md5_hash = hashlib.md5(plain_password.encode()).hexdigest()

    conn = Conexion()
    try:
        _, cur = conn.conexion()
        # 1. Crear cliente con hash MD5
        cur.execute(
            """
            INSERT INTO DIM_Customer (
                DIM_CustomerId, CustomerName, CustomerMiddleName, CustomerLastName, CustomerSecondLastName,
                CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction, username, [password]
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (cust_id, "AdminE2E", "M", "Mandho", "Tepetate", "1980-01-01", f"{year}-01-01", "s/n", "centro", "admin_e2e_md5", md5_hash)
        )

        # Obtener IDs reales dinámicamente
        cur.execute("SELECT DIM_RoleId FROM DIM_Role WHERE RoleName = 'delegado'")
        role_id = cur.fetchone()[0]
        cur.execute("SELECT DIM_ServiceId FROM DIM_Service WHERE ServiceName = 'delegado'")
        service_id = cur.fetchone()[0]

        # 2. Asignar rol delegado y cuenta activa para el año en curso
        cur.execute(
            """
            INSERT INTO DIM_Account (
                DIM_AccountId, DIM_DateId, DIM_CustomerId, DIM_RoleId, DIM_StatusId, StartDate, EndDate
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            ("e2e_acc_admin_md5", dim_date.dateId, cust_id, role_id, "status1", f"{year}-01-01", f"{year}-12-31")
        )

        # 3. Asignar service owner
        cur.execute(
            """
            INSERT INTO DIM_ServiceOwners (
                DIM_ServiceOwnersId, DIM_DateId, DIM_ServiceId, DIM_CustomerId, StartDate, EndDate
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("e2e_so_admin_md5", dim_date.dateId, service_id, cust_id, f"{year}-01-01", f"{year}-12-31")
        )
        conn.save_changes()
    finally:
        conn.close_conexion()

    # 4. Invocar endpoint de login HTTP real
    login_payload = {
        "name": "admin_e2e_md5",
        "password": plain_password,
        "role": "delegado",
        "manzana": "centro"
    }
    response = client.post("/api/security/login/", json=login_payload)
    assert response.status_code == 200, f"Error en login: {response.get_data(as_text=True)}"
    data = response.get_json()
    assert data["status"] == "success"
    assert "access_token" in data["body"]["tokens"]

    # 5. Comprobar que en SQL Server el hash se migró de MD5 a scrypt
    check_conn = Conexion()
    try:
        _, check_cur = check_conn.conexion()
        check_cur.execute("SELECT [password] FROM DIM_Customer WHERE DIM_CustomerId = ?", (cust_id,))
        updated_password_hash = check_cur.fetchone()[0]
        assert updated_password_hash != md5_hash, "El hash MD5 no fue reemplazado en SQL Server"
        assert updated_password_hash.startswith("scrypt:"), f"El nuevo hash no tiene formato scrypt: {updated_password_hash}"
    finally:
        check_conn.close_conexion()


def test_e2e_full_customer_account_service_payment_lifecycle(client):
    """
    Test E2E de ciclo de vida completo:
    1. Login de administrador para obtener JWT Bearer.
    2. Creación de vecino (/api/user/create_user/).
    3. Creación de cuenta (/api/account/create/).
    4. Consulta de analíticas (/api/analitycs/get_analytics/).
    5. Verificación de cero fugas en el QueuePool al finalizar.
    """
    # 1. Login del admin creado previamente o autenticación
    login_payload = {
        "name": "admin_e2e_md5",
        "password": "AdminSecret2026!",
        "role": "delegado",
        "manzana": "centro"
    }
    # Si no existe, crear admin rápido
    dim_date = DIM_DATE()
    year = dim_date.full_date[0]
    cust_id = "e2e_admin_journey_full"
    plain_password = "AdminSecret2026!"
    md5_hash = hashlib.md5(plain_password.encode()).hexdigest()

    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("SELECT COUNT(*) FROM DIM_Customer WHERE DIM_CustomerId = ?", (cust_id,))
        if cur.fetchone()[0] == 0:
            cur.execute(
                """
                INSERT INTO DIM_Customer (
                    DIM_CustomerId, CustomerName, CustomerMiddleName, CustomerLastName, CustomerSecondLastName,
                    CustomerDateBirth, CustomerStartDate, CustomerEndDate, CustomerFraction, username, [password]
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (cust_id, "AdminFull", "M", "Mandho", "Tepetate", "1980-01-01", f"{year}-01-01", "s/n", "centro", "admin_full_e2e", md5_hash)
            )
            cur.execute("SELECT DIM_RoleId FROM DIM_Role WHERE RoleName = 'delegado'")
            role_id = cur.fetchone()[0]
            cur.execute("SELECT DIM_ServiceId FROM DIM_Service WHERE ServiceName = 'delegado'")
            service_id = cur.fetchone()[0]

            cur.execute(
                """
                INSERT INTO DIM_Account (
                    DIM_AccountId, DIM_DateId, DIM_CustomerId, DIM_RoleId, DIM_StatusId, StartDate, EndDate
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                ("e2e_acc_admin_full", dim_date.dateId, cust_id, role_id, "status1", f"{year}-01-01", f"{year}-12-31")
            )
            cur.execute(
                """
                INSERT INTO DIM_ServiceOwners (
                    DIM_ServiceOwnersId, DIM_DateId, DIM_ServiceId, DIM_CustomerId, StartDate, EndDate
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                ("e2e_so_admin_full", dim_date.dateId, service_id, cust_id, f"{year}-01-01", f"{year}-12-31")
            )
            conn.save_changes()
    finally:
        conn.close_conexion()

    resp_login = client.post("/api/security/login/", json={
        "name": "admin_full_e2e",
        "password": plain_password,
        "role": "delegado",
        "manzana": "centro"
    })
    assert resp_login.status_code == 200
    token = resp_login.get_json()["body"]["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Crear nuevo vecino a través de la API con primeras 3 letras dinámicas (create_id usa field[:3])
    import random, string
    r_name = "".join(random.choices(string.ascii_letters, k=4))
    r_last = "".join(random.choices(string.ascii_letters, k=4))
    new_user_payload = {
        "nombre": r_name,
        "segundo_nombre": "Eduardo",
        "apellido": r_last,
        "segundo_apellido": "Perez",
        "fecha_nacimiento": "1995-04-12",
        "fecha_inicio": f"{year}-01-01",
        "fecha_fin": "s/n",
        "calle": "Calle Central",
        "manzana": "centro",
        "numero_ext": "105"
    }
    resp_user = client.post("/api/user/create_user/", json={"data": new_user_payload}, headers=headers)
    assert resp_user.status_code == 200, f"Error al crear usuario: {resp_user.get_data(as_text=True)}"
    body_user = resp_user.get_json()["body"]
    created_cust_id = body_user["id"]
    assert created_cust_id is not None

    # Registrar el ID para limpieza
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        # Verificar que el usuario existe en SQL Server
        cur.execute("SELECT COUNT(*) FROM DIM_Customer WHERE DIM_CustomerId = ?", (created_cust_id,))
        assert cur.fetchone()[0] == 1
    finally:
        conn.close_conexion()

    # 3. Crear cuenta para el vecino
    account_payload = {
        "status": "pequeño propietario",
        "customer_id": created_cust_id,
        "start_date": f"{year}-01-01",
        "end_date": "s/n"
    }
    resp_acc = client.post("/api/account/create/", json=account_payload, headers=headers)
    assert resp_acc.status_code in (200, 201), f"Error al crear cuenta: {resp_acc.get_data(as_text=True)}"

    # 4. Consultar analíticas
    resp_analytics = client.post("/api/analitycs/get_analytics/", json={
        "comitiva": "agua",
        "mes": "M01",
        "anio": "Y25"
    }, headers=headers)
    assert resp_analytics.status_code == 200

    # 5. Asegurar limpieza específica de este usuario generado vía API
    conn = Conexion()
    try:
        _, cur = conn.conexion()
        cur.execute("DELETE FROM DIM_Account WHERE DIM_CustomerId = ?", (created_cust_id,))
        cur.execute("DELETE FROM DIM_Customer WHERE DIM_CustomerId = ?", (created_cust_id,))
        conn.save_changes()
    finally:
        conn.close_conexion()

    # 6. Verificación de cero fugas en el QueuePool
    pool_status = get_pool_status()
    assert pool_status["checkedout"] == 0


def test_e2e_read_payments_all_modules_2026_and_authorization(client):
    """
    Verifica que en el año en curso (2026) todos los módulos (agua, panteón, feria, delegación)
    carguen pagos correctamente para el delegado y comitiva, permitiendo también acceso a subdelegado.
    """
    # 1. Login delegado
    resp_login = client.post("/api/security/login/", json={
        "name": "luisTorres",
        "password": "Admin1234!",
        "role": "delegado",
        "manzana": "tepetate"
    })
    assert resp_login.status_code == 200
    token_delegado = resp_login.get_json()["body"]["tokens"]["access_token"]
    headers_delegado = {"Authorization": f"Bearer {token_delegado}"}

    # 2. Consultar cada uno de los 4 módulos para 2026
    for service_name in ["panteon", "agua", "feria", "delegacion"]:
        resp = client.post("/api/payment/read/", json={
            "serviceName": service_name,
            "filters": {"DIM_Date": 2026}
        }, headers=headers_delegado)
        assert resp.status_code == 200, f"Fallo al leer pagos 2026 de {service_name}: {resp.get_data(as_text=True)}"
        json_data = resp.get_json()
        assert json_data["status"] == "success"
        body = json_data.get("body", [])
        assert len(body) > 0, f"El módulo {service_name} retornó 0 pagos para 2026"

    # 3. Comitiva (Agua) consulta agua 2026
    resp_login_comitiva = client.post("/api/security/login/", json={
        "name": "Arcov",
        "password": "Admin1234!",
        "role": "comitiva",
        "manzana": "tepetate"
    })
    assert resp_login_comitiva.status_code == 200
    token_comitiva = resp_login_comitiva.get_json()["body"]["tokens"]["access_token"]
    headers_comitiva = {"Authorization": f"Bearer {token_comitiva}"}

    resp_agua = client.post("/api/payment/read/", json={
        "serviceName": "agua",
        "filters": {"DIM_Date": 2026}
    }, headers=headers_comitiva)
    assert resp_agua.status_code == 200
    assert len(resp_agua.get_json().get("body", [])) > 0

    # 4. Subdelegado autorizado para ver pagos
    resp_login_sub = client.post("/api/security/login/", json={
        "name": "monseLopez",
        "password": "Admin1234!",
        "role": "subdelegado",
        "manzana": "garambullo"
    })
    assert resp_login_sub.status_code == 200
    token_sub = resp_login_sub.get_json()["body"]["tokens"]["access_token"]
    headers_sub = {"Authorization": f"Bearer {token_sub}"}

    resp_sub = client.post("/api/payment/read/", json={
        "serviceName": "panteon",
        "filters": {"DIM_Date": 2026}
    }, headers=headers_sub)
    assert resp_sub.status_code == 200
    assert len(resp_sub.get_json().get("body", [])) > 0

    # 5. Cero fugas en el QueuePool
    pool_status = get_pool_status()
    assert pool_status["checkedout"] == 0
