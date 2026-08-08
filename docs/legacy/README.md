# Histórico — versión C# / SQL Server

Archivos de la primera implementación del proyecto, conservados como evidencia
del proceso. **No forman parte del sistema actual y no deben ejecutarse.**

| Archivo | Qué es |
|---|---|
| `DDL-original-con-bug.sql` | Esquema inicial. No ejecuta: declara `id INT uniqueidentifier PRIMARY KEY`, dos tipos incompatibles en la misma columna |
| `DDL-corregido.sql` | El anterior, con los tipos corregidos a `INT IDENTITY` |
| `DML-original.sql` | Datos semilla iniciales. Guardaba contraseñas en texto plano |

El esquema vigente lo define **Alembic** (`alembic/versions/`), generado desde los
modelos de `app/models.py`. Para crear la base de datos:

```bash
alembic upgrade head
```

El backend en C# / ASP.NET Core vive en las ramas archivadas del repositorio
(ver etiquetas `legacy/*`).
