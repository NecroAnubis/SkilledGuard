USE auditoria_sistema;
GO

-- Tabla: Tipo_Accion
INSERT INTO Tipo_Accion (nombre, descripcion) VALUES
('Creación', 'Registro de creación de datos'),
('Actualización', 'Registro de actualización de datos'),
('Eliminación', 'Registro de eliminación de datos'),
('Consulta', 'Registro de consulta de información');
GO

-- Tabla: Objeto_Afectado
INSERT INTO Objeto_Afectado (nombre_tabla, descripcion) VALUES
('Usuario', 'Tabla que almacena los usuarios del sistema'),
('Dispositivo', 'Tabla que almacena los dispositivos del sistema'),
('Reporte', 'Tabla que almacena los reportes generados');
GO

-- Tabla: Tipo_documento
INSERT INTO Tipo_documento (nombre, acronimo, descripcion) VALUES
('Cédula de ciudadanía', 'CC', 'Documento de identidad nacional'),
('Tarjeta de identidad', 'TI', 'Documento de identidad para menores de edad'),
('Cédula extranjera', 'CE', 'Documento de identidad para extranjeros');
GO

-- Tabla: Usuario
INSERT INTO Usuario (nombres, apellidos, id_tipo_documento, documento, direccion, contrasena) VALUES
('Carlos', 'Oliveira', 1, '1002003001', 'Cra 45 #12-34', '12345'),
('María', 'Gómez', 2, '1002003002', 'Cl 56 #45-21', 'abcde'),
('Juan', 'Martínez', 1, '1002003003', 'Av 10 #8-19', 'password');
GO

-- Tabla: Rol
INSERT INTO Rol (nombre, descripcion) VALUES
('Administrador', 'Gestión completa del sistema'),
('Auditor', 'Acceso a reportes y registros de auditoría'),
('Usuario', 'Acceso limitado a funciones básicas');
GO

-- Tabla: Usuario_rol
INSERT INTO Usuario_rol (id_usuario, id_rol) VALUES
(1, 1),
(2, 2),
(3, 3);
GO

-- Tabla: Tipo_dispositivo
INSERT INTO Tipo_dispositivo (nombre, descripcion) VALUES
('Computador', 'Equipos de escritorio o portátiles'),
('Celular', 'Dispositivos móviles'),
('Tablet', 'Dispositivos tipo tableta');
GO

-- Tabla: Dispositivo
INSERT INTO Dispositivo (serial, marca, modelo, sistema, id_tipo_dispositivo, id_usuario) VALUES
('PC-12345', 'HP', 'Pavilion', 'Windows 11', 1, 1),
('MB-67890', 'Samsung', 'Galaxy S22', 'Android 13', 2, 2),
('TB-11122', 'Apple', 'iPad Pro', 'iOS 17', 3, 3);
GO

-- Tabla: Tipo_registro
INSERT INTO Tipo_registro (nombre, descripcion) VALUES
('Transacción', 'Registro de una transacción realizada'),
('Cambio de estado', 'Registro de modificaciones de estado'),
('Ingreso', 'Registro de accesos o inicios de sesión');
GO

-- Tabla: Auditoria_Negocio
INSERT INTO Auditoria_Negocio (id_tipo_registro, registrado_por, ejemplo_data) VALUES
(1, 1, 'Compra realizada por el usuario'),
(2, 2, 'Actualización del perfil de usuario'),
(3, 3, 'Inicio de sesión del usuario');
GO

-- Tabla: Tipo_Reporte
INSERT INTO Tipo_Reporte (nombre, descripcion) VALUES
('Reporte de usuarios', 'Listados de usuarios del sistema'),
('Reporte de auditoría', 'Registros de acciones en el sistema'),
('Reporte de dispositivos', 'Listado y control de dispositivos');
GO

-- Tabla: Reporte
INSERT INTO Reporte (generado_por, filtros_aplicados, url_archivo, id_tipo_reporte) VALUES
(1, 'Usuarios activos', 'reporte_usuarios.pdf', 1),
(2, 'Acciones recientes', 'reporte_auditoria.pdf', 2),
(3, 'Dispositivos asignados', 'reporte_dispositivos.pdf', 3);
GO

-- Tabla: consulta_reporte
INSERT INTO consulta_reporte (entidad_consultada, filtro_aplicado, id_reporte) VALUES
('Usuario', 'Activos', 1),
('Log_Sistema', 'Últimos 7 días', 2),
('Dispositivo', 'Asignados', 3);
GO

-- Tabla: Log_Sistema
INSERT INTO Log_Sistema (id_accion, id_usuario, id_objeto_afectado, iv_firma) VALUES
(1, 1, 1, 'firma123'),
(2, 2, 2, 'firma456'),
(3, 3, 3, 'firma789');
GO

-- Tabla: Log_Detalle
INSERT INTO Log_Detalle (id_log, campo_afectado, valor_anterior, valor_nuevo) VALUES
(1, 'nombres', NULL, 'Carlos'),
(2, 'direccion', 'Cl 12 #34-56', 'Cl 45 #67-89'),
(3, 'sistema', 'Android 12', 'Android 13');
GO
