-- =============================================================================
-- R__views_security_and_clients.sql — Vistas repetibles de seguridad y padrón activo
-- =============================================================================

CREATE OR ALTER VIEW SecurityUsers AS
SELECT
    CONCAT(cust.CustomerName, N' ', cust.CustomerMiddleName, N' ', cust.CustomerLastName, N' ', cust.CustomerSecondLastName) AS fullname,
    cust.username,
    cust.[password],
    rol.RoleName,
    s.ServiceName,
    cust.CustomerFraction,
    stat.StatusName,
    srvon.StartDate,
    srvon.EndDate,
    srvon.DIM_ServiceOwnersId,
    cust.DIM_CustomerId,
    acc.DIM_AccountId
FROM DIM_Account acc
JOIN DIM_Customer cust ON acc.DIM_CustomerId = cust.DIM_CustomerId
JOIN DIM_ServiceOwners srvon ON srvon.DIM_CustomerId = cust.DIM_CustomerId
JOIN DIM_Service s ON s.DIM_ServiceId = srvon.DIM_ServiceId
JOIN DIM_Role rol ON acc.DIM_RoleId = rol.DIM_RoleId AND rol.RoleType = N'administrador'
JOIN DIM_Status stat ON acc.DIM_StatusId = stat.DIM_StatusId;
GO

CREATE OR ALTER VIEW VISTA_CLIENTES_ACTIVOS AS
SELECT
    c.CustomerName, 
    c.CustomerMiddleName, 
    c.CustomerLastName, 
    c.CustomerSecondLastName,
    c.CustomerFraction,
    r.RoleName, 
    a.DIM_AccountId,
    c.DIM_CustomerId
FROM DIM_Account a
INNER JOIN DIM_Role r ON r.DIM_RoleId = a.DIM_RoleId
INNER JOIN DIM_Customer c ON c.DIM_CustomerId = a.DIM_CustomerId
INNER JOIN DIM_Status s ON a.DIM_StatusId = s.DIM_StatusId 
WHERE c.CustomerEndDate = N's/n'
AND a.DIM_StatusId IN (
    SELECT DIM_StatusId 
    FROM DIM_Status 
    WHERE StatusName = N'activo'
);
GO
