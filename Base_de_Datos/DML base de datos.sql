USE auditoria_sistema;
GO


INSERT INTO Rol (id, nombre, descripcion)
VALUES 
(NEWID(), 'Administrador', 'Tiene acceso completo al sistema'),
(NEWID(), 'Auditor', 'Puede generar y revisar reportes de auditoría'),
(NEWID(), 'Usuario', 'Usuario estándar con permisos limitados');

-- Tabla Tipo_documento
INSERT INTO Tipo_documento (id, nombre, acronimo)
VALUES
(NEWID(), 'Cédula de Ciudadanía', 'CC'),
(NEWID(), 'Tarjeta de Identidad', 'TI'),
(NEWID(), 'Pasaporte', 'PA');

-- Tabla Usuario
INSERT INTO Usuario (id, nombres, apellidos, id_tipo_documento, documento, tipo_usuario, email, direccion, contraseña)
VALUES
(NEWID(), 'Juan', 'Pérez', (SELECT TOP 1 id FROM Tipo_documento WHERE acronimo = 'CC'), '10101010', 'Administrador', 'juan.perez@example.com', 'Calle 123', '12345'),
(NEWID(), 'Ana', 'García', (SELECT TOP 1 id FROM Tipo_documento WHERE acronimo = 'TI'), '20202020', 'Usuario', 'ana.garcia@example.com', 'Carrera 45', 'abcde');

-- Tabla Usuario_rol
INSERT INTO Usuario_rol (id, id_usuario, id_rol)
VALUES
(NEWID(), (SELECT TOP 1 id FROM Usuario WHERE email = 'juan.perez@example.com'),
          (SELECT TOP 1 id FROM Rol WHERE nombre = 'Administrador')),
(NEWID(), (SELECT TOP 1 id FROM Usuario WHERE email = 'ana.garcia@example.com'),
          (SELECT TOP 1 id FROM Rol WHERE nombre = 'Usuario'));

-- Tabla Tipo_dispositivo
INSERT INTO Tipo_dispositivo (id, nombre)
VALUES
(NEWID(), 'Computador'),
(NEWID(), 'Celular'),
(NEWID(), 'Tablet');

-- Tabla Dispositivo
INSERT INTO Dispositivo (id, serial, marca, modelo, sistema, descripcion, foto_url, qr, id_tipo_dispositivo, id_usuario)
VALUES
(NEWID(), 'ABC123', 'HP', 'EliteBook', 'Windows 11', 'Portátil asignado a Juan Pérez', NULL, NULL,
 (SELECT TOP 1 id FROM Tipo_dispositivo WHERE nombre = 'Computador'),
 (SELECT TOP 1 id FROM Usuario WHERE email = 'juan.perez@example.com')),

(NEWID(), 'XYZ789', 'Samsung', 'Galaxy S22', 'Android', 'Celular corporativo de Ana García', NULL, NULL,
 (SELECT TOP 1 id FROM Tipo_dispositivo WHERE nombre = 'Celular'),
 (SELECT TOP 1 id FROM Usuario WHERE email = 'ana.garcia@example.com'));

-- Tabla Tipo_registro
INSERT INTO Tipo_registro (id, nombre)
VALUES
(NEWID(), 'Inicio de Sesión'),
(NEWID(), 'Actualización de Datos'),
(NEWID(), 'Eliminación de Registro');

-- Tabla Auditoria_Negocio
INSERT INTO Auditoria_Negocio (id, fecha_registro, id_tipo_registro, registrado_por, descripcion)
VALUES
(NEWID(), GETDATE(), (SELECT TOP 1 id FROM Tipo_registro WHERE nombre = 'Inicio de Sesión'),
 (SELECT TOP 1 id FROM Usuario WHERE email = 'juan.perez@example.com'),
 'Inicio de sesión exitoso del usuario administrador');

-- Tabla Tipo_Reporte
INSERT INTO Tipo_Reporte (id, nombre)
VALUES
(NEWID(), 'Reporte General'),
(NEWID(), 'Reporte de Actividad'),
(NEWID(), 'Reporte de Auditoría');

-- Tabla Sede
INSERT INTO Sede (id, nombre_sede)
VALUES
(NEWID(), 'Sede Principal'),
(NEWID(), 'Sucursal Norte');

-- Tabla Reporte
INSERT INTO Reporte (id, generado_por, sede, descripcion, id_tipo_reporte)
VALUES
(NEWID(),
 (SELECT TOP 1 id FROM Usuario WHERE email = 'juan.perez@example.com'),
 (SELECT TOP 1 id FROM Sede WHERE nombre_sede = 'Sede Principal'),
 'Reporte general de actividades del sistema',
 (SELECT TOP 1 id FROM Tipo_Reporte WHERE nombre = 'Reporte General'));
