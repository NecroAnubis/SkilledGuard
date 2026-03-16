-- Script para actualizar contraseñas de usuarios existentes a formato hash (PBKDF2-SHA256).
-- EJECUTAR SOLO si ya ejecutó DML_base_de_datos.sql con la versión anterior (contraseñas en texto plano).
-- Si está creando la BD por primera vez, use solo DML_base_de_datos.sql (ya incluye hashes).

USE auditoria_sistema;
GO

-- Las contraseñas deben estar hasheadas. Ejecute el generador de hashes:
--   cd Base_de_Datos/HashPasswordGenerator
--   dotnet run
-- Luego reemplace los valores siguientes con los hashes generados.

-- Hash para 'clave123' (ejemplo - genere el suyo con HashPasswordGenerator):
UPDATE Usuario SET contraseña = 'I+OLp1mN4ZoUkOoNDDbtGTs5Et2QlmrQWTn1B7B18/CS6LmgLuvb00X1qo/tUsW+' WHERE email = 'juan@correo.com';

-- Hash para 'clave456':
UPDATE Usuario SET contraseña = 'FJEDl0noHQ7eEgat67qIqqxC9p3M0jihMr9ORNwkreCHWcWjiM3oqtvmjMy9ir6r' WHERE email = 'ana@correo.com';

-- Agregar los 2 usuarios adicionales de prueba si no existen:
IF NOT EXISTS (SELECT 1 FROM Usuario WHERE email = 'admin@skilledguard.com')
INSERT INTO Usuario (id, nombres, apellidos, id_tipo_documento, documento, tipo_usuario, email, direccion, contraseña, fecha_creado, fecha_actualizado, id_rol)
VALUES ('18181818-1818-1818-1818-181818181818', 'Admin', 'Sistema', '33333333-3333-3333-3333-333333333333', '11223344', 'admin', 'admin@skilledguard.com', 'Sede Central', '3lA7QNJH8OFOdh+vlCQr9RrW2TIDSgBtqFpP2U966auYtdETTUt1bFab89knd2MB', GETDATE(), NULL, '11111111-1111-1111-1111-111111111111');

IF NOT EXISTS (SELECT 1 FROM Usuario WHERE email = 'usuario@skilledguard.com')
INSERT INTO Usuario (id, nombres, apellidos, id_tipo_documento, documento, tipo_usuario, email, direccion, contraseña, fecha_creado, fecha_actualizado, id_rol)
VALUES ('19191919-1919-1919-1919-191919191919', 'Usuario', 'Prueba', '33333333-3333-3333-3333-333333333333', '55667788', 'user', 'usuario@skilledguard.com', 'Sede Norte', 'e9rRXkjbbr6q63UDGUPcJqRdZkv450ITjwpTohjdq7fNn32GQJiw+nJX9kgTm49o', GETDATE(), NULL, '22222222-2222-2222-2222-222222222222');
