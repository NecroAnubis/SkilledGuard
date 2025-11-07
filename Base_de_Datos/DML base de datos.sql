-- 1. Tablas base

-- Rol
INSERT INTO Rol (id, nombre, descripcion) VALUES
('11111111-1111-1111-1111-111111111111', 'Administrador', 'Rol con todos los permisos'),
('22222222-2222-2222-2222-222222222222', 'Usuario', 'Rol con permisos limitados');

-- Tipo_documento
INSERT INTO Tipo_documento (id, nombre, acronimo) VALUES
('33333333-3333-3333-3333-333333333333', 'Cédula de Ciudadanía', 'CC'),
('44444444-4444-4444-4444-444444444444', 'Pasaporte', 'PASS');

-- Tipo_dispositivo
INSERT INTO Tipo_dispositivo (id, nombre) VALUES
('55555555-5555-5555-5555-555555555555', 'Laptop'),
('66666666-6666-6666-6666-666666666666', 'Smartphone');

-- Tipo_registro
INSERT INTO Tipo_registro (id, nombre) VALUES
('77777777-7777-7777-7777-777777777777', 'Ingreso'),
('88888888-8888-8888-8888-888888888888', 'Salida');

-- Tipo_Reporte
INSERT INTO Tipo_Reporte (id, nombre) VALUES
('99999999-9999-9999-9999-999999999999', 'Reporte Diario'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Reporte Mensual');

-- Sede
INSERT INTO Sede (id, nombre_sede) VALUES
('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Sede Central'),
('cccccccc-cccc-cccc-cccc-cccccccccccc', 'Sede Norte');

-- 2. Usuario
INSERT INTO Usuario (id, nombres, apellidos, id_tipo_documento, documento, tipo_usuario, email, direccion, contraseña, fecha_creado, fecha_actualizado, id_rol)
VALUES
('dddddddd-dddd-dddd-dddd-dddddddddddd', 'Juan', 'Pérez', '33333333-3333-3333-3333-333333333333', '12345678', 'admin', 'juan@correo.com', 'Calle 1', 'clave123', GETDATE(), NULL, '11111111-1111-1111-1111-111111111111'),
('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Ana', 'Gómez', '44444444-4444-4444-4444-444444444444', '87654321', 'user', 'ana@correo.com', 'Calle 2', 'clave456', GETDATE(), NULL, '22222222-2222-2222-2222-222222222222');

-- 3. Log_Sistema
INSERT INTO Log_Sistema (id, id_usuario, descripcion, fecha_creado)
VALUES
('ffffffff-ffff-ffff-ffff-ffffffffffff', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'Primer log de Juan', GETDATE()),
('10101010-1010-1010-1010-101010101010', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Primer log de Ana', GETDATE());

-- 4. Dispositivo
INSERT INTO Dispositivo (id, serial, marca, modelo, sistema, descripcion, foto_url, qr, id_tipo_dispositivo, id_usuario, fecha_creado, fecha_actualizado)
VALUES
('12121212-1212-1212-1212-121212121212', 'ABC123', 'Dell', 'XPS 13', 'Windows 10', 'Laptop de Juan', 'http://foto1.com', 'QR1', '55555555-5555-5555-5555-555555555555', 'dddddddd-dddd-dddd-dddd-dddddddddddd', GETDATE(), NULL),
('13131313-1313-1313-1313-131313131313', 'XYZ789', 'Apple', 'iPhone 12', 'iOS', 'Teléfono de Ana', 'http://foto2.com', 'QR2', '66666666-6666-6666-6666-666666666666', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', GETDATE(), NULL);

-- 5. Auditoria_Negocio
INSERT INTO Auditoria_Negocio (id, fecha_registro, id_tipo_registro, registrado_por, descripcion)
VALUES
('14141414-1414-1414-1414-141414141414', GETDATE(), '77777777-7777-7777-7777-777777777777', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'Auditoría de ingreso'),
('15151515-1515-1515-1515-151515151515', GETDATE(), '88888888-8888-8888-8888-888888888888', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Auditoría de salida');

-- 6. Reporte
INSERT INTO Reporte (id, generado_por, sede, descripcion, fecha_generado, url_archivo, id_tipo_reporte, fecha_creado, fecha_actualizado)
VALUES
('16161616-1616-1616-1616-161616161616', 'dddddddd-dddd-dddd-dddd-dddddddddddd', 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb', 'Reporte diario de Juan', GETDATE(), 'http://reporte1.com', '99999999-9999-9999-9999-999999999999', GETDATE(), NULL),
('17171717-1717-1717-1717-171717171717', 'eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'cccccccc-cccc-cccc-cccc-cccccccccccc', 'Reporte mensual de Ana', GETDATE(), 'http://reporte2.com', 'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', GETDATE(), NULL);