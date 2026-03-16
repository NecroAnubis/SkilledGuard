================================================================================
                    BASE DE DATOS - AUDITORÍA SISTEMA
                         Proyecto SkilledGuard
================================================================================

DESCRIPCIÓN
-----------
Base de datos SQL Server para el sistema de auditoría. Gestiona usuarios, roles,
dispositivos, registros de auditoría de negocio, reportes y logs del sistema.

Nombre de la base de datos: auditoria_sistema


ARCHIVOS INCLUIDOS
------------------
• DDL_base_de_datos.sql     - Script de definición (creación de tablas y estructura)
• DML_base_de_datos.sql     - Script de datos iniciales (catálogos y datos de prueba)
• DML_actualizar_contraseñas.sql - Solo si ya ejecutó DML con contraseñas en texto plano
• HashPasswordGenerator/    - Herramienta para generar hashes (dotnet run)


TABLAS Y ESTRUCTURA
-------------------

1. Rol
   - id (UNIQUEIDENTIFIER, PK)
   - nombre (NVARCHAR 100)
   - descripcion (NVARCHAR 500)
   Catálogo de roles del sistema (Administrador, Usuario, etc.).

2. Tipo_documento
   - id (UNIQUEIDENTIFIER, PK)
   - nombre (NVARCHAR 100)
   - acronimo (NVARCHAR 20)
   Tipos de documento de identidad (CC, Pasaporte, etc.).

3. Usuario
   - id (UNIQUEIDENTIFIER, PK)
   - nombres, apellidos (NVARCHAR 100)
   - id_tipo_documento (FK → Tipo_documento)
   - documento (NVARCHAR 50)
   - tipo_usuario (NVARCHAR 50)
   - email (NVARCHAR 150), direccion (NVARCHAR 255)
   - contraseña (NVARCHAR 255)
   - fecha_creado, fecha_actualizado (DATE)
   - id_rol (FK → Rol)

4. Log_Sistema
   - id (UNIQUEIDENTIFIER, PK)
   - id_usuario (FK → Usuario)
   - descripcion (NVARCHAR 500)
   - fecha_creado (DATE)
   Registro de acciones o eventos del sistema por usuario.

5. Tipo_dispositivo
   - id (UNIQUEIDENTIFIER, PK)
   - nombre (NVARCHAR 100)
   Catálogo (Laptop, Smartphone, etc.).

6. Dispositivo
   - id (UNIQUEIDENTIFIER, PK)
   - serial, marca, modelo, sistema (NVARCHAR 100)
   - descripcion (NVARCHAR 500), foto_url, qr (NVARCHAR 255)
   - id_tipo_dispositivo (FK → Tipo_dispositivo)
   - id_usuario (FK → Usuario)
   - fecha_creado, fecha_actualizado (DATE)

7. Tipo_registro
   - id (UNIQUEIDENTIFIER, PK)
   - nombre (NVARCHAR 100)
   Catálogo para auditoría (Ingreso, Salida, etc.).

8. Auditoria_Negocio
   - id (UNIQUEIDENTIFIER, PK)
   - fecha_registro (DATE)
   - id_tipo_registro (FK → Tipo_registro)
   - registrado_por (FK → Usuario)
   - descripcion (NVARCHAR 500)
   Registros de auditoría de negocio (ingresos/salidas, etc.).

9. Tipo_Reporte
   - id (UNIQUEIDENTIFIER, PK)
   - nombre (NVARCHAR 100)
   Catálogo (Reporte Diario, Reporte Mensual, etc.).

10. Sede
    - id (UNIQUEIDENTIFIER, PK)
    - nombre_sede (NVARCHAR 150)

11. Reporte
    - id (UNIQUEIDENTIFIER, PK)
    - generado_por (FK → Usuario)
    - sede (FK → Sede)
    - descripcion (NVARCHAR 500)
    - fecha_generado (DATE)
    - url_archivo (NVARCHAR 255)
    - id_tipo_reporte (FK → Tipo_Reporte)
    - fecha_creado, fecha_actualizado (DATE)


RELACIONES PRINCIPALES
----------------------
• Usuario → Rol, Tipo_documento
• Log_Sistema → Usuario
• Dispositivo → Tipo_dispositivo, Usuario
• Auditoria_Negocio → Tipo_registro, Usuario
• Reporte → Usuario, Sede, Tipo_Reporte


DATOS INICIALES (DML)
---------------------
El script DML incluye:
- 2 roles: Administrador, Usuario
- 2 tipos de documento: Cédula de Ciudadanía (CC), Pasaporte
- 2 tipos de dispositivo: Laptop, Smartphone
- 2 tipos de registro: Ingreso, Salida
- 2 tipos de reporte: Reporte Diario, Reporte Mensual
- 2 sedes: Sede Central, Sede Norte
- 4 usuarios de prueba (contraseñas con hash PBKDF2):
  • juan@correo.com / clave123 (Administrador)
  • ana@correo.com / clave456 (Usuario)
  • admin@skilledguard.com / admin123 (Administrador)
  • usuario@skilledguard.com / user123 (Usuario)
- Registros de ejemplo en Log_Sistema, Dispositivo, Auditoria_Negocio y Reporte


DIAGRAMA ENTIDAD-RELACIÓN (ER)
------------------------------
Representación en texto de las entidades y relaciones (1 = uno, N = muchos).

    +-------------+         +------------------+
    |    Rol      |         |  Tipo_documento  |
    | id (PK)     |         | id (PK)          |
    | nombre      |         | nombre, acronimo |
    | descripcion |         +--------+---------+
    +------+------+                  |
           | 1                       |
           |                         | 1
           |    +---------------+   |
           +----|   Usuario     |---+-
                | id (PK)       |
                | nombres       |
                | apellidos     |
                | documento     |
                | id_tipo_doc(FK)
                | id_rol (FK)   |
                | email, etc.   |
                +-------+-------+
                        | 1
        +---------------+---------------+
        |               |               | N
        v               v               v
+-------+-------+ +-----+--------+ +----+----------+
|Log_Sistema   | | Dispositivo   | |Auditoria_     |
| id (PK)      | | id (PK)       | | Negocio       |
| id_usuario(FK)| | id_tipo_disp(FK)| id (PK)     |
| descripcion  | | id_usuario(FK)| | id_tipo_reg(FK)|
| fecha_creado | | serial, marca | | registrado_por(FK)|
+--------------+ +-------+-------+ | descripcion   |
                    | 1           +----------------+
                    | N
    +---------------+---------------+
    |               |               |
    v               v               v
+---+--------+ +----+--------+ +----+----------+
|Tipo_      | | Sede        | |Tipo_Reporte   |
|dispositivo| | id (PK)     | | id (PK)       |
| id (PK)   | | nombre_sede | | nombre        |
| nombre    | +------+------+ +-------+-------+
+-----------+       | 1                | 1
                    |                  |
                    | N                | N
                    v                  v
              +-----+------------+-----+
              |     Reporte            |
              | id (PK)                |
              | generado_por (FK→Usuario)
              | sede (FK→Sede)         |
              | id_tipo_reporte (FK)   |
              | url_archivo, etc.      |
              +------------------------+

  +----------------+
  | Tipo_registro   |
  | id (PK)         |----1---N---> Auditoria_Negocio
  | nombre          |
  +----------------+


ÍNDICES
-------
Definidos por el DDL:
• Clave primaria (PK) en cada tabla: índice único sobre id (UNIQUEIDENTIFIER).
  SQL Server crea automáticamente un índice clustered o unique para cada PK.

Recomendaciones para mejorar consultas (opcionales, no están en el DDL actual):
• Usuario: índice sobre id_tipo_documento, id_rol (búsquedas por rol o tipo doc).
• Log_Sistema: índice sobre id_usuario y fecha_creado (listados por usuario y fecha).
• Dispositivo: índice sobre id_usuario, id_tipo_dispositivo (filtros por dueño o tipo).
• Auditoria_Negocio: índice sobre fecha_registro, id_tipo_registro, registrado_por.
• Reporte: índice sobre generado_por, sede, fecha_generado, id_tipo_reporte.

Ejemplo para agregar un índice después de crear las tablas:
  CREATE NONCLUSTERED INDEX IX_Log_Sistema_id_usuario
  ON Log_Sistema (id_usuario, fecha_creado);


PERMISOS Y SEGURIDAD
--------------------
• El DDL no define usuarios ni permisos; se asume ejecución con un usuario con
  derechos de creación (ej. sa o dbo) en el servidor.
• En producción se recomienda:
  - Crear un usuario de aplicación con permisos limitados (ej. db_datareader,
    db_datawriter) sobre auditoria_sistema, sin rol sysadmin.
  - No usar sa para la aplicación; usar un login dedicado.
  - Considerar cifrado de columnas sensibles (ej. contraseña) o almacenar solo
    hashes y no contraseñas en claro.
• La tabla Usuario contiene contraseña (NVARCHAR); en producción debe usarse
  solo almacenamiento de hash (ej. bcrypt/Argon2) desde la aplicación.


CÓMO USAR LOS SCRIPTS
----------------------
1. Ejecutar primero "DDL_base_de_datos.sql" en SQL Server Management Studio
   (o cliente compatible) para crear la base de datos y todas las tablas.
2. Ejecutar después "DML_base_de_datos.sql" para insertar los datos iniciales
   y de prueba (incluye 4 usuarios con contraseñas hasheadas).

Si ya ejecutó una versión anterior del DML con contraseñas en texto plano y el
login falla, ejecute "DML_actualizar_contraseñas.sql" para actualizar los hashes.
Para generar hashes de nuevas contraseñas: cd HashPasswordGenerator; dotnet run

Requisito: Motor de base de datos compatible con T-SQL (SQL Server).

================================================================================
