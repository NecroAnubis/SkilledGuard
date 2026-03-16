# 07 – Base de datos (resumen)

**Proyecto:** SkilledGuard  
**Documento:** Resumen ejecutivo de la base de datos  
**Referencia:** Detalle completo en [Base_de_Datos/README.txt](../Base_de_Datos/README.txt). Modelo de datos en [05_Modelo_de_Datos](05_Modelo_de_Datos.md).

---

## 1. Datos generales

| Aspecto | Valor |
|---------|--------|
| **Nombre de la base de datos** | `auditoria_sistema` |
| **Motor** | Microsoft SQL Server (T-SQL) |
| **Ubicación de scripts** | Carpeta `Base_de_Datos/` en la raíz del proyecto |

---

## 2. Archivos

| Archivo | Propósito |
|---------|-----------|
| **DDL_base_de_datos.sql** | Crea la base de datos y todas las tablas (Rol, Tipo_documento, Usuario, Log_Sistema, Tipo_dispositivo, Dispositivo, Tipo_registro, Auditoria_Negocio, Tipo_Reporte, Sede, Reporte). |
| **DML_base_de_datos.sql** | Inserta datos iniciales: catálogos (roles, tipos de documento, tipos de dispositivo, tipos de registro, tipos de reporte, sedes) y datos de prueba (usuarios, logs, dispositivos, auditorías, reportes). |
| **README.txt** | Documentación detallada: estructura de tablas, relaciones, diagrama ER en texto, índices recomendados, permisos y seguridad, uso de los scripts. |

---

## 3. Orden de ejecución

1. Ejecutar **DDL_base_de_datos.sql** (crear BD y tablas).  
2. Ejecutar **DML_base_de_datos.sql** (poblar catálogos y datos de prueba).

Requisito: cliente compatible con T-SQL (por ejemplo SQL Server Management Studio, Azure Data Studio o `sqlcmd`) y permisos para crear base de datos y ejecutar DDL/DML.

---

## 4. Conexión desde la API

La API usa Entity Framework Core con SQL Server. La cadena de conexión se configura en:

- **Archivo:** `CodigoBackend/Auditorias/appsettings.json` (o `appsettings.Development.json`)
- **Clave:** `ConnectionStrings:AuditoriaConnection`
- **Base de datos:** debe ser `auditoria_sistema` (o el nombre que se haya usado al ejecutar el DDL).

Ejemplo:

```text
Server=TU_SERVIDOR;Database=auditoria_sistema;Trusted_Connection=True;TrustServerCertificate=True;
```

---

## 5. Contenido del DML (resumen)

- 2 roles (Administrador, Usuario)
- 2 tipos de documento (CC, Pasaporte)
- 2 tipos de dispositivo (Laptop, Smartphone)
- 2 tipos de registro (Ingreso, Salida)
- 2 tipos de reporte (Diario, Mensual)
- 2 sedes (Sede Central, Sede Norte)
- 2 usuarios de ejemplo (p. ej. para login: email y contraseña indicados en el README principal)
- Registros de ejemplo en Log_Sistema, Dispositivo, Auditoria_Negocio y Reporte

---

## 6. Dónde encontrar más información

| Tema | Dónde |
|------|--------|
| Estructura de tablas y columnas | [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – sección TABLAS Y ESTRUCTURA |
| Relaciones y diagrama ER | [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – RELACIONES y DIAGRAMA ENTIDAD-RELACIÓN |
| Modelo resumido y diagrama Mermaid | [05_Modelo_de_Datos](05_Modelo_de_Datos.md) |
| Índices recomendados (opcionales) | [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – ÍNDICES |
| Permisos y seguridad en producción | [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – PERMISOS Y SEGURIDAD |
| Configuración y ejecución del proyecto | [README principal](../README.md) – Paso a paso |

---

## Referencias

- [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – Documentación completa de la base de datos
- [05_Modelo_de_Datos](05_Modelo_de_Datos.md) – Modelo de datos y diagrama ER
- [README principal](../README.md) – Configuración de conexión y ejecución
