USE auditoria_sistema;
GO

-- =====================================
-- TABLA: Tipo_Accion
-- =====================================
INSERT INTO Tipo_Accion (nombre, descripcion)
VALUES 
('Creación', 'Registro de creación de datos'),
('Actualización', 'Registro de actualización de datos'),
('Eliminación', 'Registro de eliminación de datos'),
('Consulta', 'Registro de consultas realizadas');
GO

-- =====================================
-- TABLA: Objeto_Afectado
-- =====================================
INSERT INTO Objeto_Afectado (nombre_tabla, descripcion)
VALUES
('Usuario', 'Tabla que almacena los usuarios del sistema'),
('Dispositivo', 'Tabla que almacena los dispositivos registrados'),
('Reporte', 'Tabla con los reportes generados');
GO

-- =====================================
-- TABLA: Tipo_documento
-- =====================================
INSERT INTO Tipo_documento (nombre, acronimo, descripcion)
VALUES
('Cédula de ciudadanía', 'CC', 'Documento nacional'),
('Tarjeta de identidad', 'TI', 'Documento para menores de edad'),
('Cédula extranjera', 'CE', 'Documento para extranjeros');
GO

-- =====================================
-- TABLA: Usuario
-- =====================================
INSERT INTO Usuario (nombres, apellidos, id_tipo_documento, documento, direccion, contrasena)
VALUES
('Carlos', 'Oliveira', 1, '1002003001', 'Cra 45 #12-34', '12345'),
('María', 'Gómez', 2, '1002003002', 'Cl 56 #45-21', 'abcde'),
('Juan', 'Martínez', 1, '1002003003', 'Av 10 #8-19', 'password');
GO

-- =====================================
-- TABLA: Rol
-- =====================================
INSERT INTO Rol (nombre, descripcion)
VALUES
('Administrador', 'Gestión total del sistema'),
('Auditor', 'Acceso a reportes y auditorías'),
('Usuario', 'Acceso limitado a funcionalidades básicas');
GO

-- =====================================
-- TABLA: Usuario_Rol
-- =====================================
INSERT INTO Usuario_Rol (id_usuario, id_rol)
VALUES
(1, 1),
(2, 2),
(3, 3);
GO

-- =====================================
-- TABLA: Tipo_dispositivo
-- =====================================
INSERT INTO Tipo_dispositivo (nombre, descripcion)
VALUES
('Computador', 'Equipo portátil o de escritorio'),
('Celular', 'Teléfono móvil'),
('Tablet', 'Dispositivo tipo tableta');
GO

-- =====================================
-- TABLA: Dispositivo
-- =====================================
INSERT INTO Dispositivo (serial, marca, modelo, sistema, id_tipo_dispositivo, id_usuario)
VALUES
('PC-12345', 'HP', 'Pavilion', 'Windows 11', 1, 1),
('MB-67890', 'Samsung', 'Galaxy S22', 'Android 13', 2, 2),
('TB-11122', 'Apple', 'iPad Pro', 'iOS 17', 3, 3);
GO

-- =====================================
-- TABLA: Tipo_registro
-- =====================================
INSERT INTO Tipo_registro (nombre, descripcion)
VALUES
('Transacción', 'Registro de una transacción realizada'),
('Cambio de estado', 'Registro de modificaciones de estado'),
('Ingreso', 'Registro de inicio de sesión o acceso');
GO

-- =====================================
-- TABLA: Auditoria_Negocio
-- =====================================
INSERT INTO Auditoria_Negocio (id_tipo_registro, registrado_por, ejemplo_data)
VALUES
(1, 1, 'Compra realizada por el usuario'),
(2, 2, 'Cambio de contraseña del usuario'),
(3, 3, 'Inicio de sesión exitoso');
GO

-- =====================================
-- TABLA: Log_Sistema
-- =====================================
INSERT INTO Log_Sistema (id_accion, id_usuario, id_objeto_afectado, iv_firma)
VALUES
(1, 1, 1, 'firmaABC123'),
(2, 2, 2, 'firmaDEF456'),
(3, 3, 3, 'firmaGHI789');
GO

-- =====================================
-- TABLA: Log_Detalle
-- =====================================
INSERT INTO Log_Detalle (id_log, campo_afectado, valor_anterior, valor_nuevo)
VALUES
(1, 'nombres', NULL, 'Carlos'),
(2, 'direccion', 'Cl 12 #34-56', 'Cl 45 #67-89'),
(3, 'sistema', 'Android 12', 'Android 13');
GO

-- =====================================
-- TABLA: Tipo_Reporte
-- =====================================
INSERT INTO Tipo_Reporte (nombre, descripcion)
VALUES
('Reporte de usuarios', 'Listados de usuarios del sistema'),
('Reporte de auditoría', 'Registros de acciones en el sistema'),
('Reporte de dispositivos', 'Listado y control de dispositivos');
GO

-- =====================================
-- TABLA: Reporte
-- =====================================
INSERT INTO Reporte (generado_por, filtros_aplicados, url_archivo, id_tipo_reporte)
VALUES
(1, 'Usuarios activos', 'reporte_usuarios.pdf', 1),
(2, 'Acciones recientes', 'reporte_auditoria.pdf', 2),
(3, 'Dispositivos asignados', 'reporte_dispositivos.pdf', 3);
GO

-- =====================================
-- TABLA: Consulta_Reporte
-- =====================================
INSERT INTO Consulta_Reporte (entidad_consultada, filtro_aplicado, id_reporte)
VALUES
('Usuario', 'Activos', 1),
('Log_Sistema', 'Últimos 7 días', 2),
('Dispositivo', 'Asignados', 3);
GO