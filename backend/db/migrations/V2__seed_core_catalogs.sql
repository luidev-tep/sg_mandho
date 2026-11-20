-- =============================================================================
-- V2__seed_core_catalogs.sql — Catálogos maestros idempotentes
-- =============================================================================

-- DIM_Role (11 registros)
IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'16c84d0b-3148-5769')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'16c84d0b-3148-5769', N'residente', N'usuario', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'74789a1e-2fc7-5131')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'74789a1e-2fc7-5131', N'pequeño propietario', N'usuario', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'822bbdbb-964d-50a6')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'822bbdbb-964d-50a6', N'ranchero', N'usuario', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'9bce4ac0-5414-561d')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'9bce4ac0-5414-561d', N'delegado', N'administrador', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'ac53ea10-cb43-5ce6')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'ac53ea10-cb43-5ce6', N'vecino exento', N'usuario', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'bfd06808-257d-5710')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'bfd06808-257d-5710', N'comitiva', N'administrador', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'c77ea6a3-4baa-523e')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'c77ea6a3-4baa-523e', N'estudiante', N'usuario', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'dbae332e-87a9-5fc3')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'dbae332e-87a9-5fc3', N'subdelegado', N'administrador', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'dcd3a2ee-69c1-545d')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'dcd3a2ee-69c1-545d', N'vecino', N'usuario', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'e03b67a8-f9d7-5e9d')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'e03b67a8-f9d7-5e9d', N'invalido', N'inactivo', N'2000-01-01', N'2100-01-01');

IF NOT EXISTS (SELECT 1 FROM DIM_Role WHERE DIM_RoleId = N'e2a5d805-8738-5069')
    INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate)
    VALUES (N'e2a5d805-8738-5069', N'inmigrante', N'usuario', N'2000-01-01', N'2100-01-01');

-- DIM_Status (8 registros)
IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status1')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status1', N'activo');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status2')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status2', N'inactivo');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status3')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status3', N'trabajado');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status4')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status4', N'completo');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status5')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status5', N'pendiente');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status6')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status6', N'requerido');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status7')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status7', N'nousado');

IF NOT EXISTS (SELECT 1 FROM DIM_Status WHERE DIM_StatusId = N'status8')
    INSERT INTO DIM_Status (DIM_StatusId, StatusName) VALUES (N'status8', N'usado');

-- DIM_Service (6 registros)
IF NOT EXISTS (SELECT 1 FROM DIM_Service WHERE DIM_ServiceId = N'17259752-21dd-5d83')
    INSERT INTO DIM_Service (DIM_ServiceId, ServiceName) VALUES (N'17259752-21dd-5d83', N'feria');

IF NOT EXISTS (SELECT 1 FROM DIM_Service WHERE DIM_ServiceId = N'1fbd9d83-7a85-50ec')
    INSERT INTO DIM_Service (DIM_ServiceId, ServiceName) VALUES (N'1fbd9d83-7a85-50ec', N'agua');

IF NOT EXISTS (SELECT 1 FROM DIM_Service WHERE DIM_ServiceId = N'acf85e49-6bce-5a8b')
    INSERT INTO DIM_Service (DIM_ServiceId, ServiceName) VALUES (N'acf85e49-6bce-5a8b', N'delegacion');

IF NOT EXISTS (SELECT 1 FROM DIM_Service WHERE DIM_ServiceId = N'dd9bd03b-0180-54c6')
    INSERT INTO DIM_Service (DIM_ServiceId, ServiceName) VALUES (N'dd9bd03b-0180-54c6', N'delegado');

IF NOT EXISTS (SELECT 1 FROM DIM_Service WHERE DIM_ServiceId = N'e2d33355-5186-597c')
    INSERT INTO DIM_Service (DIM_ServiceId, ServiceName) VALUES (N'e2d33355-5186-597c', N'panteon');

IF NOT EXISTS (SELECT 1 FROM DIM_Service WHERE DIM_ServiceId = N'e9d33cc0-90a8-51fd')
    INSERT INTO DIM_Service (DIM_ServiceId, ServiceName) VALUES (N'e9d33cc0-90a8-51fd', N'personas');

-- DIM_Movement (2 registros)
IF NOT EXISTS (SELECT 1 FROM DIM_Movement WHERE DIM_MovementId = N'9d8dff92-630b-5f51')
    INSERT INTO DIM_Movement (DIM_MovementId, MovementName) VALUES (N'9d8dff92-630b-5f51', N'egreso');

IF NOT EXISTS (SELECT 1 FROM DIM_Movement WHERE DIM_MovementId = N'd3e7d32b-d440-5048')
    INSERT INTO DIM_Movement (DIM_MovementId, MovementName) VALUES (N'd3e7d32b-d440-5048', N'ingreso');
GO
