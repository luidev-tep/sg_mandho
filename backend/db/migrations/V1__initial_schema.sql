-- =============================================================================
-- V1__initial_schema.sql — Esquema inicial T-SQL para SQL Server / Azure SQL
-- 11 Tablas dimensionales/hechos + 5 Índices no agrupados
-- =============================================================================

CREATE TABLE DIM_Role (
    DIM_RoleId NVARCHAR(64) NOT NULL PRIMARY KEY,
    RoleName NVARCHAR(100) NOT NULL,
    RoleType NVARCHAR(50) NOT NULL,
    RoleStartDate NVARCHAR(20) NOT NULL,
    RoleEndDate NVARCHAR(20) DEFAULT N's/n',
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_Status (
    DIM_StatusId NVARCHAR(64) NOT NULL PRIMARY KEY,
    StatusName NVARCHAR(100) NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_Date (
    DIM_DateId INT NOT NULL PRIMARY KEY,
    FiscalYear NVARCHAR(10) NOT NULL,
    FiscalMonth NVARCHAR(10) NOT NULL,
    FiscalQuarter NVARCHAR(10) NOT NULL,
    FiscalWeek NVARCHAR(10) NOT NULL,
    FiscalDay NVARCHAR(10) NOT NULL,
    [Year] INT NOT NULL,
    [Month] NVARCHAR(10) NOT NULL,
    [Week] NVARCHAR(10) NOT NULL,
    [Day] NVARCHAR(10) NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_Customer (
    DIM_CustomerId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    CustomerName NVARCHAR(100) NOT NULL,
    CustomerMiddleName NVARCHAR(100) DEFAULT N's/n',
    CustomerLastName NVARCHAR(100) NOT NULL,
    CustomerSecondLastName NVARCHAR(100) DEFAULT N's/n',
    CustomerDateBirth NVARCHAR(20) NOT NULL,
    CustomerStartDate NVARCHAR(20) NOT NULL,
    CustomerEndDate NVARCHAR(20) DEFAULT N's/n',
    CustomerFraction NVARCHAR(100) DEFAULT N's/n',
    CustomerAddress NVARCHAR(255) DEFAULT N's/n',
    CustomerNumberExt NVARCHAR(50) DEFAULT N's/n',
    username NVARCHAR(100) DEFAULT N'n/a',
    [password] NVARCHAR(255) NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_Customer_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId)
);

CREATE TABLE DIM_Account (
    DIM_AccountId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NOT NULL,
    DIM_CustomerId NVARCHAR(64) NOT NULL,
    DIM_RoleId NVARCHAR(64) NOT NULL,
    DIM_StatusId NVARCHAR(64) NOT NULL,
    StartDate NVARCHAR(20) NOT NULL,
    EndDate NVARCHAR(20) DEFAULT N's/n',
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_Account_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_Account_Customer FOREIGN KEY (DIM_CustomerId) REFERENCES DIM_Customer(DIM_CustomerId),
    CONSTRAINT FK_Account_Role FOREIGN KEY (DIM_RoleId) REFERENCES DIM_Role(DIM_RoleId),
    CONSTRAINT FK_Account_Status FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

CREATE TABLE DIM_Service (
    DIM_ServiceId NVARCHAR(64) NOT NULL PRIMARY KEY,
    ServiceName NVARCHAR(100) NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE DIM_ServiceDetails (
    DIM_ServiceDetailsId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    DIM_ServiceId NVARCHAR(64) NULL,
    ServiceDetailesType NVARCHAR(100) NULL,
    amount FLOAT NULL CHECK (amount >= 0.0),
    DIM_StatusId NVARCHAR(64) NULL,
    StartDate NVARCHAR(20) NOT NULL,
    EndDate NVARCHAR(20) NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_ServiceDetails_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_ServiceDetails_Service FOREIGN KEY (DIM_ServiceId) REFERENCES DIM_Service(DIM_ServiceId),
    CONSTRAINT FK_ServiceDetails_Status FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

CREATE TABLE DIM_ServiceOwners (
    DIM_ServiceOwnersId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    DIM_ServiceId NVARCHAR(64) NULL,
    DIM_CustomerId NVARCHAR(64) NULL,
    StartDate NVARCHAR(20) NOT NULL,
    EndDate NVARCHAR(20) DEFAULT N's/n',
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_ServiceOwners_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_ServiceOwners_Service FOREIGN KEY (DIM_ServiceId) REFERENCES DIM_Service(DIM_ServiceId),
    CONSTRAINT FK_ServiceOwners_Customer FOREIGN KEY (DIM_CustomerId) REFERENCES DIM_Customer(DIM_CustomerId)
);

CREATE TABLE DIM_Movement (
    DIM_MovementId NVARCHAR(64) NOT NULL PRIMARY KEY,
    MovementName NVARCHAR(100) NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120)
);

CREATE TABLE FACT_Revenue (
    FACT_RevenueId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_DateId INT NULL,
    DIM_AccountId NVARCHAR(64) NULL,
    DIM_ServiceDetailsId NVARCHAR(64) NULL,
    DIM_MovementId NVARCHAR(64) NULL,
    DIM_StatusId NVARCHAR(64) NULL,
    amount FLOAT NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT CK_FACT_Revenue_Amount_NonNegative CHECK (amount >= 0),
    CONSTRAINT FK_Revenue_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_Revenue_Account FOREIGN KEY (DIM_AccountId) REFERENCES DIM_Account(DIM_AccountId),
    CONSTRAINT FK_Revenue_ServiceDetails FOREIGN KEY (DIM_ServiceDetailsId) REFERENCES DIM_ServiceDetails(DIM_ServiceDetailsId),
    CONSTRAINT FK_Revenue_Movement FOREIGN KEY (DIM_MovementId) REFERENCES DIM_Movement(DIM_MovementId),
    CONSTRAINT FK_Revenue_Status FOREIGN KEY (DIM_StatusId) REFERENCES DIM_Status(DIM_StatusId)
);

CREATE TABLE DIM_CashCut (
    DIM_CashCutId NVARCHAR(64) NOT NULL PRIMARY KEY,
    DIM_ServiceDetailsId NVARCHAR(64) NOT NULL UNIQUE,
    DIM_DateId INT NOT NULL,
    DIM_ServiceOwnersId NVARCHAR(64) NOT NULL,
    DIM_CountRegisters INT NOT NULL,
    [timestamp] NVARCHAR(30) DEFAULT CONVERT(NVARCHAR(19), SYSUTCDATETIME() AT TIME ZONE 'UTC' AT TIME ZONE 'Central Standard Time (Mexico)', 120),
    CONSTRAINT FK_CashCut_ServiceDetails FOREIGN KEY (DIM_ServiceDetailsId) REFERENCES DIM_ServiceDetails(DIM_ServiceDetailsId),
    CONSTRAINT FK_CashCut_Date FOREIGN KEY (DIM_DateId) REFERENCES DIM_Date(DIM_DateId),
    CONSTRAINT FK_CashCut_ServiceOwners FOREIGN KEY (DIM_ServiceOwnersId) REFERENCES DIM_ServiceOwners(DIM_ServiceOwnersId)
);

CREATE INDEX IX_DIM_Customer_Fraction_EndDate ON DIM_Customer(CustomerFraction, CustomerEndDate);
CREATE INDEX IX_DIM_Account_Customer_Status ON DIM_Account(DIM_CustomerId, DIM_StatusId);
CREATE INDEX IX_FACT_Revenue_Account_ServiceDetails ON FACT_Revenue(DIM_AccountId, DIM_ServiceDetailsId);
CREATE INDEX IX_FACT_Revenue_Date ON FACT_Revenue(DIM_DateId);
CREATE INDEX IX_DIM_ServiceDetails_Service_Date ON DIM_ServiceDetails(DIM_ServiceId, DIM_DateId);
GO
