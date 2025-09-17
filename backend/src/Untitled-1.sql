WITH vwCustomerPayments AS (

SELECT 
    FACT_Revenue.DIM_DateId,
    FACT_Revenue.DIM_AccountId,
    DIM_Customer.DIM_CustomerId,
    CAST(DIM_Date.Year AS TEXT) as YearPayment,
    FACT_Revenue.DIM_ServiceDetailsId,
	DIM_Customer.CustomerName,
    DIM_Customer.CustomerMiddleName, 
    DIM_Customer.CustomerSecondLastName, 


	DIM_Role.RoleName,
    DIM_Service.ServiceName,
    DIM_ServiceDetails.ServiceDetailesType,
    DIM_Status.StatusName,

    sum(FACT_Revenue.amount) as BilledRevenue    
FROM FACT_Revenue
JOIN DIM_Date ON
    DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
JOIN DIM_Account ON 
    DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId

JOIN DIM_Customer ON
    DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId    
JOIN DIM_Role ON
    DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId 
JOIN DIM_ServiceDetails ON
    DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
JOIN DIM_Service ON
    DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
JOIN DIM_Movement ON
    DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId

JOIN DIM_Status  ON
    DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId 


WHERE UPPER(DIM_Movement.MovementName) = 'INGRESO'

GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12
),

vwServiceCost AS (


SELECT 
	DIM_ServiceDetails.DIM_DateId,
	DIM_Date.FiscalYear,
	DIM_Date.FiscalMonth,
    DIM_ServiceDetails.DIM_ServiceDetailsId,
    DIM_Service.ServiceName,
    DIM_ServiceDetails.ServiceDetailesType,
    sum(DIM_ServiceDetails.amount) as BilledServiceRevenue
FROM DIM_ServiceDetails
JOIN DIM_Date ON
	DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId 
	
JOIN DIM_Service ON
    DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
GROUP BY 1,2,3,4,5,6
),

vwCustomerDetailedTransactions AS (
SELECT
    vwServiceCost.DIM_DateId as ServiceDateCreated,
	vwCustomerPayments.DIM_DateId as CustomerPaymentDate,
    vwServiceCost.FiscalYear,
    vwCustomerPayments.DIM_AccountId,
    vwCustomerPayments.DIM_CustomerId,
    vwCustomerPayments.DIM_ServiceDetailsId,
    vwServiceCost.ServiceName,
    vwServiceCost.ServiceDetailesType,
    vwCustomerPayments.CustomerName, 
    vwCustomerPayments.CustomerMiddleName,
    vwCustomerPayments.CustomerSecondLastName,
    
    vwCustomerPayments.RoleName,
    vwCustomerPayments.StatusName as BillStatus,
    
    SUM(COALESCE(vwCustomerPayments.BilledRevenue,0)) as CustomerPaid,
    SUM(COALESCE(vwCustomerPayments.BilledRevenue,0)) OVER (PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId ORDER BY vwCustomerPayments.DIM_DateId) as CustomerPaidTotal,

    SUM(COALESCE(vwServiceCost.BilledServiceRevenue,0)) as TotalCost
 

FROM vwServiceCost
LEFT JOIN  vwCustomerPayments ON
    vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
	

GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13
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
    CustomerSecondLastName,
    RoleName,
    BillStatus,

    CustomerPaid,
    CustomerPaidTotal,
    TotalCost,
    TotalCost - CustomerPaidTotal as  Pending,
    CASE WHEN 
        TotalCost - CustomerPaidTotal = 0 THEN 'pagada' ELSE 'pendiente' 
    END as RealStatusHardcoded,
    RANK() OVER (PARTITION BY DIM_CustomerId,DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) as Ranking

FROM vwCustomerDetailedTransactions

)


SELECT 
*,

FROM vwCustomerRecords  WHERE FiscalYear = 'Y25' and  ServiceName = 'agua' and Ranking = 1

--DIM_AccountId = '6914eb86-9fb6-5ef7' and -- '6914eb86-9fb6-5ef7 ' and 
--DIM_CustomerId = 'ab8c820a-8364-5860'--'ab8c820a-8364-5860'


