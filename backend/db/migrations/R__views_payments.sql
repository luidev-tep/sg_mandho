-- =============================================================================
-- R__views_payments.sql — Vistas repetibles de pagos y pagos detallados (8 vistas)
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Vistas VISTA_PAGOS_<MODULO> (Ranking = 1)
-- -----------------------------------------------------------------------------

CREATE OR ALTER VIEW VISTA_PAGOS_AGUA AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN (SELECT COUNT(DIM_AccountId) FROM DIM_Account WHERE DIM_CustomerId = vw.DIM_CustomerId AND DIM_StatusId = N'status1') > 0 THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
WHERE vw.ServiceName = N'agua' 
AND vw.Ranking = 1;
GO

CREATE OR ALTER VIEW VISTA_PAGOS_DELEGACION AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN (SELECT COUNT(DIM_AccountId) FROM DIM_Account WHERE DIM_CustomerId = vw.DIM_CustomerId AND DIM_StatusId = N'status1') > 0 THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
WHERE vw.ServiceName = N'delegacion' 
AND vw.Ranking = 1;
GO

CREATE OR ALTER VIEW VISTA_PAGOS_FERIA AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN (SELECT COUNT(DIM_AccountId) FROM DIM_Account WHERE DIM_CustomerId = vw.DIM_CustomerId AND DIM_StatusId = N'status1') > 0 THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
WHERE vw.ServiceName = N'feria' 
AND vw.Ranking = 1;
GO

CREATE OR ALTER VIEW VISTA_PAGOS_PANTEON AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN (SELECT COUNT(DIM_AccountId) FROM DIM_Account WHERE DIM_CustomerId = vw.DIM_CustomerId AND DIM_StatusId = N'status1') > 0 THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
WHERE vw.ServiceName = N'panteon' 
AND vw.Ranking = 1;
GO

-- -----------------------------------------------------------------------------
-- Vistas VISTA_PAGOS_DETALLADO_<MODULO> (Sin Ranking = 1, JOIN DIM_Customer)
-- -----------------------------------------------------------------------------

CREATE OR ALTER VIEW VISTA_PAGOS_DETALLADO_AGUA AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN clientes.CustomerEndDate = N's/n' THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
JOIN DIM_Customer AS clientes ON clientes.DIM_CustomerId = vw.DIM_CustomerId
WHERE vw.ServiceName = N'agua';
GO

CREATE OR ALTER VIEW VISTA_PAGOS_DETALLADO_DELEGACION AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN clientes.CustomerEndDate = N's/n' THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
JOIN DIM_Customer AS clientes ON clientes.DIM_CustomerId = vw.DIM_CustomerId
WHERE vw.ServiceName = N'delegacion';
GO

CREATE OR ALTER VIEW VISTA_PAGOS_DETALLADO_FERIA AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN clientes.CustomerEndDate = N's/n' THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
JOIN DIM_Customer AS clientes ON clientes.DIM_CustomerId = vw.DIM_CustomerId
WHERE vw.ServiceName = N'feria';
GO

CREATE OR ALTER VIEW VISTA_PAGOS_DETALLADO_PANTEON AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)) AS YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        SUM(FACT_Revenue.amount) AS BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = N'INGRESO'
    GROUP BY 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.[Year] AS NVARCHAR(10)),
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName
),
vwServiceCost AS (
    SELECT 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        SUM(DIM_ServiceDetails.amount) AS BilledServiceRevenue
    FROM DIM_ServiceDetails
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    GROUP BY 
        DIM_ServiceDetails.DIM_DateId,
        DIM_Date.FiscalYear,
        DIM_Date.FiscalMonth,
        DIM_ServiceDetails.DIM_ServiceDetailsId,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType
),
vwCustomerDetailedTransactions AS (
    SELECT
        vwServiceCost.DIM_DateId AS ServiceDateCreated,
        vwCustomerPayments.DIM_DateId AS CustomerPaymentDate,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName AS BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0)) AS CustomerPaid,
        SUM(SUM(COALESCE(vwCustomerPayments.BilledRevenue, 0))) OVER (
            PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId 
            ORDER BY vwCustomerPayments.DIM_DateId
        ) AS CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue, 0)) AS TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 
        vwServiceCost.DIM_DateId,
        vwCustomerPayments.DIM_DateId,
        vwServiceCost.FiscalYear,
        vwCustomerPayments.DIM_AccountId,
        vwCustomerPayments.DIM_CustomerId,
        vwCustomerPayments.DIM_ServiceDetailsId,
        vwServiceCost.ServiceName,
        vwServiceCost.ServiceDetailesType,
        vwCustomerPayments.CustomerName, 
        vwCustomerPayments.CustomerMiddleName,
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName
),
vwCustomerRecords AS (
    SELECT 
        ServiceDateCreated,
        CustomerPaymentDate,
        FiscalYear,
        DIM_AccountId,
        DIM_CustomerId,
        DIM_ServiceDetailsId,
        ServiceName,
        ServiceDetailesType,
        CustomerName,
        CustomerMiddleName,
        CustomerLastName,
        CustomerSecondLastName,
        RoleName,
        BillStatus,
        CustomerPaid,
        CustomerPaidTotal,
        TotalCost,
        TotalCost - CustomerPaidTotal AS Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN N'completo' 
            ELSE N'pendiente' 
        END AS RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) AS Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN clientes.CustomerEndDate = N's/n' THEN N'activo'
        ELSE N'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal AS amount,
    CONCAT(N'20', SUBSTRING(vw.FiscalYear, 2, 2)) AS YearPay, 
    vw.CustomerPaymentDate AS DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
JOIN DIM_Customer AS clientes ON clientes.DIM_CustomerId = vw.DIM_CustomerId
WHERE vw.ServiceName = N'panteon';
GO
