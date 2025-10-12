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

--SE AGREGARON 2 NUEVOS ROLES LOS CUALES POR EL MOMENTO CUMPLES CON LA LABOR DE MANEJAR A PERSONAS LAS CUALES NO VAN A PARTICIPAR

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('16c84d0b-3148-5769', 'residente', 'usuario', '2000-01-01', '2100-01-01');

INSERT INTO DIM_Role (DIM_RoleId, RoleName, RoleType, RoleStartDate, RoleEndDate) 
VALUES ('ac53ea10-cb43-5ce6', 'vecino exento', 'usuario', '2000-01-01', '2100-01-01');

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

