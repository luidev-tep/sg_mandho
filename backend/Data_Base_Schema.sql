-- Creación de la base de datos sistema_mandho
PRAGMA foreign_keys = ON;

-- Tabla DIM_Role
CREATE TABLE DIM_Role (
    DIM_RoleId TEXT PRIMARY KEY,
    RoleName TEXT NOT NULL,
    RoleType TEXT NOT NULL,
    RoleStartDate TEXT NOT NULL,  -- Formato YYYY-MM-DD
    RoleEndDate TEXT DEFAULT 's/n',
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Tabla DIM_Status
CREATE TABLE DIM_Status (
    DIM_StatusId TEXT PRIMARY KEY,
    StatusName TEXT NOT NULL,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Tabla DIM_Date
-- SE CREARA UN CODIGO EN PYTHON DONDE SE AGREGARAN TODOS LOS ANIOS COMO 
-- PREDEFINIDOS
CREATE TABLE DIM_Date (
    DIM_DateId INTEGER PRIMARY KEY,
    FiscalYear TEXT NOT NULL,
    FiscalMonth TEXT NOT NULL,
	FiscalQuarter TEXT NOT NULL,
    FiscalWeek TEXT NOT NULL,
    FiscalDay TEXT NOT NULL,
    Year INTEGER NOT NULL,
    Month TEXT NOT NULL,
    Week TEXT NOT NULL,
    Day TEXT NOT NULL,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Tabla DIM_Customer
CREATE TABLE DIM_Customer (
    DIM_CustomerId TEXT PRIMARY KEY,
    DIM_DateId INTEGER,
    CustomerName TEXT NOT NULL,
    CustomerMiddleName TEXT DEFAULT 's/n',
    CustomerLastName TEXT NOT NULL,
    CustomerSecondLastName TEXT DEFAULT 's/n',
    CustomerDateBirth TEXT NOT NULL,
    CustomerStartDate TEXT NOT NULL,
    CustomerEndDate TEXT DEFAULT 's/n',
    CustomerFraction TEXT DEFAULT 's/n',
    CustomerAddress TEXT DEFAULT 's/n',
    CustomerNumberExt TEXT DEFAULT 's/n',
    username TEXT DEFAULT 'n/a',
    password TEXT,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId)
);

-- Tabla DIM_Account
CREATE TABLE DIM_Account (
    DIM_AccountId TEXT PRIMARY KEY,
    DIM_DateId INTEGER,
    DIM_CustomerId TEXT NOT NULL,
    DIM_RoleId TEXT NOT NULL,
    DIM_StatusId TEXT NOT NULL,
    StartDate TEXT NOT NULL,
    EndDate TEXT DEFAULT 's/n',
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    FOREIGN KEY (DIM_CustomerId) REFERENCES DIM_Customer(DIM_CustomerId),
    FOREIGN KEY (DIM_RoleId) REFERENCES DIM_Role(DIM_RoleId),
    FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

--Se modificaron desde aqui las para agregar modificaciones de servicios y movimientos
-- Tabla DIM_Service
CREATE TABLE DIM_Service (
    DIM_ServiceId TEXT PRIMARY KEY,
    ServiceName TEXT,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Tabla DIM_ServiceDetails
CREATE TABLE DIM_ServiceDetails (
    DIM_ServiceDetailsId TEXT PRIMARY KEY,
    DIM_DateId INTEGER,
    DIM_ServiceId TEXT,
    ServiceDetailesType TEXT,
    amount REAL CHECK (amount >= 0.0),
	StartDate TEXT NOT NULL,
    EndDate TEXT NOT NULL, --Los pagos son anuales, ya se conce por defecto la fecha en la que se se vence el pago
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    FOREIGN KEY (DIM_ServiceId) REFERENCES DIM_Service(DIM_ServiceId)
);

-- Tabla DIM_ServiceOwners
CREATE TABLE DIM_ServiceOwners (
    DIM_ServiceOwnersId TEXT PRIMARY KEY,
    DIM_DateId INTEGER,
    DIM_ServiceId TEXT,
    DIM_CustomerId TEXT,
    StartDate TEXT NOT NULL,
    EndDate TEXT DEFAULT 's/n',
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    FOREIGN KEY (DIM_ServiceId) REFERENCES DIM_Service(DIM_ServiceId),
    FOREIGN KEY (DIM_CustomerId) REFERENCES DIM_Customer(DIM_CustomerId)
);

-- Tabla DIM_Movement
CREATE TABLE DIM_Movement (
    DIM_MovementId TEXT PRIMARY KEY,
    MovementName TEXT,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime'))
);

-- Tabla FACT_Revenue
CREATE TABLE FACT_Revenue (
    FACT_RevenueId TEXT PRIMARY KEY,
    DIM_DateId INTEGER,
    DIM_AccountId TEXT,
    DIM_ServiceDetailsId TEXT,
    DIM_MovementId TEXT,
    DIM_StatusId TEXT,
    amount REAL NOT NULL,
    timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    FOREIGN KEY (DIM_AccountId) REFERENCES DIM_Account(DIM_AccountId),
    FOREIGN KEY (DIM_ServiceDetailsId) REFERENCES DIM_ServiceDetails(DIM_ServiceDetailsId),
    FOREIGN KEY (DIM_MovementId) REFERENCES DIM_Movement(DIM_MovementId),
    FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);


-- Tabla DIM_CashCut    La cual almacenara el estado de los cortes de caja
--Aqui se guardara infromacion de quien lo ejecito, cuantos registros se hicieron y el total
CREATE TABLE DIM_CashCut (
    DIM_CashCutId TEXT PRIMARY KEY,
    DIM_ServiceDetailsId TEXT NOT NULL UNIQUE,
	DIM_DateId INTEGER not NULL,
	DIM_ServiceOwnersId TEXT not NULL,
    DIM_CountRegisters int not null,
	timestamp TEXT DEFAULT (strftime('%Y-%m-%d %H:%M:%S', 'now', 'localtime')),
    FOREIGN KEY (DIM_ServiceDetailsId) REFERENCES DIM_ServiceDetails(DIM_ServiceDetailsId),
	FOREIGN KEY  (DIM_DateId) REFERENCES DIM_Date(DIM_DateId)
	FOREIGN KEY  (DIM_ServiceOwnersId) REFERENCES DIM_ServiceOwners(DIM_ServiceOwnersId)
);


-- Tablas de dimensiones
SELECT * FROM DIM_Role;
SELECT * FROM DIM_Status;
SELECT * FROM DIM_Date;
SELECT * FROM DIM_Customer;
SELECT * FROM DIM_Account;
SELECT * FROM DIM_Service;
SELECT * FROM DIM_ServiceDetails;
SELECT * FROM DIM_ServiceOwners;
SELECT * FROM DIM_Movement;
SELECT * from DIM_CashCut;


-- Tabla de hechos
SELECT * FROM FACT_Revenue;

--se modificaron 3 tablas puesto que tenian algunos campos con tipos de datos incorrectos, asi como la tabla DIM_ServiceDetails que no tenia el campo StartDate y EndDate

--INSERSION DE DATOS PREDEFINIDOS EN DIM_STATUS
INSERT INTO DIM_Status(DIM_StatusId, StatusName) VALUES ('status1', 'activo');
INSERT INTO DIM_Status(DIM_StatusId, StatusName) VALUES ('status2', 'inactivo');
INSERT INTO DIM_Status(DIM_StatusId, StatusName) VALUES ('status4', 'completo');
INSERT INTO DIM_Status(DIM_StatusId, StatusName) VALUES ('status5', 'pendiente');
INSERT INTO DIM_Status(DIM_StatusId, StatusName) VALUES ('status3', 'trabajado');  --Se modifico este Status para ser el pago que si se crea pero no se paga

-- Insertar roles en la tabla DIM_Role
INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('9bce4ac0-5414-561d', 'delegado', 'administrador', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('bfd06808-257d-5710', 'comitiva', 'administrador', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('dbae332e-87a9-5fc3', 'subdelegado', 'administrador', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('c77ea6a3-4baa-523e', 'estudiante', 'usuario', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('822bbdbb-964d-50a6', 'ranchero', 'usuario', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('dcd3a2ee-69c1-545d', 'vecino', 'usuario', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('e2a5d805-8738-5069', 'inmigrante', 'usuario', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('74789a1e-2fc7-5131', 'pequeño propietario', 'usuario', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('e03b67a8-f9d7-5e9d', 'invalido', 'inactivo', '2000-01-01', '2100-01-01');


-- Insertar registros en la tabla DIM_Movement Solo son 2 registros
insert into DIM_Movement 
(DIM_MovementId, MovementName) VALUES
('d3e7d32b-d440-5048', 'ingreso');
insert into DIM_Movement 

(DIM_MovementId, MovementName) VALUES
('9d8dff92-630b-5f51', 'egreso');


-- insertar registros en la tabla DIM_service
insert into DIM_Service
(DIM_ServiceId,ServiceName)
VALUES
('1fbd9d83-7a85-50ec','agua');

insert into DIM_Service
(DIM_ServiceId,ServiceName)
VALUES
('17259752-21dd-5d83','feria');

insert into DIM_Service
(DIM_ServiceId,ServiceName)
VALUES
('e2d33355-5186-597c','panteon');

insert into DIM_Service
(DIM_ServiceId,ServiceName)
VALUES
('acf85e49-6bce-5a8b','delegacion');

--SE AGREGARON 2 NUEVOS SERVICIOS LOS CUALES SERVIRAN PARA TERMINAR DE TENER A TODOS LOS USUARIOS ADMINISTRADORES Del SISTEMA
insert into DIM_Service
 (DIM_ServiceId,ServiceName)
  VALUES
   ('e9d33cc0-90a8-51fd','personas');

insert into DIM_Service
 (DIM_ServiceId,ServiceName)
  VALUES
   ('dd9bd03b-0180-54c6','delegado');


-- Estos servicios se deberan renovar anualmente para que se mantengan actualizado, solo deberia cambia star, y endate
--Registro de peuba metido en service details, SE DEBERA ACOMPLETAR COIN TODOS LOS TIPOS DE SERVICIO DE CADA COMITIVA
insert into DIM_ServiceDetails 
(DIM_ServiceDetailsId, DIM_DateId, DIM_ServiceId, ServiceDetailesType, amount, StartDate, EndDate)
VALUES
('4942db5a-04b2-57b2', '080c33d3-7f33-55d7', '1fbd9d83-7a85-50ec', 'consumo', 360.0, '2025-01-01', '2025-12-31');

insert into DIM_ServiceDetails
(DIM_ServiceDetailsId, DIM_DateId, DIM_ServiceId, ServiceDetailesType ,amount, StartDate, EndDate)
VALUES
('d8e3ce13-aef7-5594', '080c33d3-7f33-55d7', '1fbd9d83-7a85-50ec', 'tomas', 360.0, '2025-01-01', '2025-12-31');

insert into DIM_ServiceDetails
(DIM_ServiceDetailsId, DIM_DateId, DIM_ServiceId, ServiceDetailesType, amount, StartDate, EndDate)
VALUES
('cb6a2afc-1318-5658', '080c33d3-7f33-55d7', 'e2d33355-5186-597c', 'faena', 300.0, '2025-01-01', '2025-12-31');

insert into DIM_ServiceDetails
(DIM_ServiceDetailsId, DIM_DateId, DIM_ServiceId, ServiceDetailesType, amount, StartDate, EndDate)
VALUES
('41ba58e0-500f-53ef', '080c33d3-7f33-55d7', 'e2d33355-5186-597c', 'cooperacion', 400.0, '2025-01-01', '2025-12-31');




--Registro de un ususario en la tabla propiertarios, solo se hizzo para testear, ya que Se deberan agregar bien
insert into DIM_ServiceOwners
(DIM_ServiceOwnersId, DIM_DateId, DIM_ServiceId, DIM_CustomerId, StartDate, EndDate )
VALUES
('0901a1e6-8779-5695', 20250806, '1fbd9d83-7a85-50ec', 'ed37cb83-f080-5e41', '2025-01-01', '2025-12-31');


--CREACION DE UNA VISTA, SOLAMENTE SE AGRGA UNA, PUESTO QUE AUN NO SE SABE SI SERA EL DISENIO FINAL, PUEDE CAMBIAR

CREATE VIEW VISTA_PAGOS_AGUA AS --CAMBIAR NOMBRE DE LA VISTA SEGUN EL SERVICIO
SELECT 
    customer.CustomerName, 
    customer.CustomerMiddleName, 
    customer.CustomerLastName, 
    customer.CustomerSecondLastName,
    rol.RoleName, 
    estado_cuenta.StatusName AS StatusCuenta,
    estado_factura.StatusName AS StatusFactura,
    DetalleServicio.ServiceDetailesType,
    factura.amount,
    strftime('%Y', DetalleServicio.StartDate) as YearPay, 
    factura.DIM_DateId,
    factura.FACT_RevenueId,
	cuenta.DIM_AccountId,
    customer.DIM_CustomerId --obtener id del cliente para poder filtrar por clientes
FROM FACT_Revenue AS factura
INNER JOIN DIM_Account AS cuenta ON factura.DIM_AccountId = cuenta.DIM_AccountId
INNER JOIN DIM_Customer AS customer ON cuenta.DIM_CustomerId = customer.DIM_CustomerId
INNER JOIN DIM_Role AS rol ON cuenta.DIM_RoleId = rol.DIM_RoleId
INNER JOIN DIM_Status AS estado_cuenta ON cuenta.DIM_StatusId = estado_cuenta.DIM_StatusId
INNER JOIN DIM_Status AS estado_factura ON factura.DIM_StatusId = estado_factura.DIM_StatusId
INNER JOIN DIM_ServiceDetails AS DetalleServicio ON factura.DIM_ServiceDetailsId = DetalleServicio.DIM_ServiceDetailsId
INNER JOIN DIM_Service AS servicio ON DetalleServicio.DIM_ServiceId = servicio.DIM_ServiceId
WHERE servicio.ServiceName = 'agua'; --CAMBIAR SEGUN EL SERVICIO


--CREACION DE NUEVAS VISTAS AHORA SI FINAL:

--TIENEN LOS MISMOS CAMPOS QUE LA VISTAS ANTIGUAS
CREATE VIEW VISTA_PAGOS_FERIA AS
WITH vwCustomerPayments AS (
    SELECT 
        FACT_Revenue.DIM_DateId,
        FACT_Revenue.DIM_AccountId,
        DIM_Customer.DIM_CustomerId,
        CAST(DIM_Date.Year AS TEXT) as YearPayment,
        FACT_Revenue.DIM_ServiceDetailsId,
        DIM_Customer.CustomerName,
        DIM_Customer.CustomerMiddleName,
        DIM_Customer.CustomerLastName,
        DIM_Customer.CustomerSecondLastName, 
        DIM_Role.RoleName,
        DIM_Service.ServiceName,
        DIM_ServiceDetails.ServiceDetailesType,
        DIM_Status.StatusName,
        sum(FACT_Revenue.amount) as BilledRevenue
    FROM FACT_Revenue
    JOIN DIM_Date ON DIM_Date.DIM_DateId = FACT_Revenue.DIM_DateId
    JOIN DIM_Account ON DIM_Account.DIM_AccountId = FACT_Revenue.DIM_AccountId
    JOIN DIM_Customer ON DIM_Customer.DIM_CustomerId = DIM_Account.DIM_CustomerId
    JOIN DIM_Role ON DIM_Role.DIM_RoleId = DIM_Account.DIM_RoleId
    JOIN DIM_ServiceDetails ON DIM_ServiceDetails.DIM_ServiceDetailsId = FACT_Revenue.DIM_ServiceDetailsId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
    JOIN DIM_Movement ON DIM_Movement.DIM_MovementId = FACT_Revenue.DIM_MovementId
    JOIN DIM_Status ON DIM_Status.DIM_StatusId = FACT_Revenue.DIM_StatusId
    WHERE UPPER(DIM_Movement.MovementName) = 'INGRESO'
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13
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
    JOIN DIM_Date ON DIM_Date.DIM_DateId = DIM_ServiceDetails.DIM_DateId
    JOIN DIM_Service ON DIM_Service.DIM_ServiceId = DIM_ServiceDetails.DIM_ServiceId
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
        vwCustomerPayments.CustomerLastName,
        vwCustomerPayments.CustomerSecondLastName,
        vwCustomerPayments.RoleName,
        vwCustomerPayments.StatusName as BillStatus,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue,0)) as CustomerPaid,
        SUM(COALESCE(vwCustomerPayments.BilledRevenue,0)) OVER (PARTITION BY vwCustomerPayments.DIM_ServiceDetailsId, vwCustomerPayments.DIM_AccountId ORDER BY vwCustomerPayments.DIM_DateId) as CustomerPaidTotal,
        SUM(COALESCE(vwServiceCost.BilledServiceRevenue,0)) as TotalCost
    FROM vwServiceCost
    LEFT JOIN vwCustomerPayments ON vwCustomerPayments.DIM_ServiceDetailsId = vwServiceCost.DIM_ServiceDetailsId
    GROUP BY 1,2,3,4,5,6,7,8,9,10,11,12,13,14
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
        TotalCost - CustomerPaidTotal as Pending,
        CASE 
            WHEN TotalCost - CustomerPaidTotal <= 0 THEN 'completo' 
            ELSE 'pendiente' 
        END as RealStatusHardcoded,
        RANK() OVER (PARTITION BY DIM_CustomerId, DIM_ServiceDetailsId ORDER BY CustomerPaymentDate DESC) as Ranking
    FROM vwCustomerDetailedTransactions
)
SELECT
    vw.CustomerName, 
    vw.CustomerMiddleName, 
    vw.CustomerLastName, 
    vw.CustomerSecondLastName,
    vw.RoleName,
    CASE 
        WHEN clientes.CustomerEndDate = 's/n' THEN 'activo'
        ELSE 'inactivo'
    END AS StatusCuenta,
    vw.RealStatusHardcoded AS StatusFactura,
    vw.ServiceDetailesType,
    vw.CustomerPaidTotal as amount,
    CONCAT('20', SUBSTRING(vw.FiscalYear, 2, 2)) as YearPay, 
    vw.CustomerPaymentDate as DIM_DateId,
    vw.DIM_AccountId,
    vw.DIM_CustomerId
FROM vwCustomerRecords AS vw
JOIN DIM_Customer as clientes ON clientes.DIM_CustomerId = vw.DIM_CustomerId 
WHERE vw.ServiceName = 'panteon' 
AND vw.Ranking = 1;


-- Eliminamos la vista si existe, esto es solo si se quiere actualizar la vista
--DROP VIEW IF EXISTS VISTA_PAGOS_AGUA;

--eSTE ES UN EJEMPLO DE LA CNONSULTA QUE SE CREO PARA PODER ACCEDER A LA VISTA CON FILTROS 
--TANTO DE ANIO COMO DE INACTIVOS  ASI COMO DE LAS MANZANAS A LAS QUE SE PERTENECE
SELECT vw.*
FROM VISTA_PAGOS_AGUA as vw
INNER JOIN DIM_Customer AS p 
    ON vw.DIM_CustomerId = p.DIM_CustomerId
INNER JOIN DIM_Date AS d 
    ON vw.DIM_DateId = d.DIM_DateId
WHERE 
	(p.CustomerFraction = 'cerritos' or p.CustomerFraction = 'yhonda') and 
	d.FiscalYear = 'Y25' 
	and 
     vw.StatusFactura = 'pendiente';

select * from DIM_Date



-- Ejemplo de la consulta que se haria para ver los pagos de lar personas
-- Unidos por anio y por cuenta

SELECT
vw.CustomerName,
vw.CustomerMiddleName,
vw.CustomerLastName,
vw.CustomerSecondLastName,
vw.RoleName,
vw.StatusCuenta,
vw.StatusFactura,
vw.ServiceDetailesType,
vw.amount,
vw.YearPay,
vw.DIM_AccountId,
vw.DIM_CustomerId
FROM VISTA_PAGOS_AGUA as vw --La tabla tamibien seria dinamic
--Filtros irian aqui


-- SE CREO UNA NUEVA VISTA LA CUAL SE PODRA UTILIZAR EN LAS CHECK LIST
	CREATE VIEW VISTA_CLIENTES_ACTIVOS AS
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
INNER JOIN DIM_Customer c ON c.DIM_CustomerId = a.DIM_CustomerId  -- Corregido: debe ser DIM_CustomerId
INNER JOIN DIM_Status s ON a.DIM_StatusId = s.DIM_StatusId 
WHERE c.CustomerEndDate = 's/n'  -- Persona no muerta
AND a.DIM_StatusId IN (
    SELECT DIM_StatusId 
    FROM DIM_Status 
    WHERE StatusName = 'activo'
);
--SELECT * FROM VISTA_CLIENTES_ACTIVOS

--DROP VIEW IF EXISTS VISTA_CLIENTES_ACTIVOS;

-- Índices adicionales para mejorar el rendimiento
-- CREATE INDEX idx_customer_date ON DIM_Customer(DIM_DateId);
-- CREATE INDEX idx_account_customer ON DIM_Account(DIM_CustomerId);
-- CREATE INDEX idx_account_status ON DIM_Account(DIM_StatusId);
-- CREATE INDEX idx_revenue_account ON FACT_Revenue(DIM_AccountId);
-- CREATE INDEX idx_revenue_date ON FACT_Revenue(DIM_DateId);
-- CREATE INDEX idx_service_details_service ON DIM_ServiceDetails(DIM_ServiceId);