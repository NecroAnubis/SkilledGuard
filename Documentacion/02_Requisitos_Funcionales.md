# 02 – Requisitos funcionales

**Proyecto:** SkilledGuard  
**Documento:** Requisitos funcionales  
**Referencia:** Extraídos del backend (controladores), base de datos y [01_Vision_y_Alcance](01_Vision_y_Alcance.md).

---

## Convenciones

| Prioridad | Significado |
|-----------|-------------|
| **Alta**  | Esencial para el funcionamiento del sistema (ej. login, usuarios). |
| **Media** | Funcionalidad principal de negocio (dispositivos, auditoría, reportes). |
| **Baja**  | Catálogos y soporte (roles, tipos de documento, sedes). |

| Estado        | Significado |
|---------------|-------------|
| **Implementado** | Cubierto por la API o la base de datos en el estado actual del proyecto. |
| **Pendiente**    | No implementado o solo previsto (ej. frontend, ampliaciones). |

---

## 1. Autenticación y sesión

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF01 | El sistema debe permitir iniciar sesión con email y contraseña. | Alta | Implementado | `POST /api/Auth/login`; respuesta con token JWT y datos del usuario. |
| RF02 | El sistema debe emitir un token JWT válido tras credenciales correctas. | Alta | Implementado | Token con claims (id, email, rol); expiración configurable (p. ej. 2 h). |
| RF03 | Las operaciones protegidas deben exigir el token en el header `Authorization: Bearer <token>`. | Alta | Implementado | Endpoints con `[Authorize]`; login con `[AllowAnonymous]`. |

---

## 2. Usuarios y perfiles

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF04 | El sistema debe permitir listar todos los usuarios. | Alta | Implementado | `GET /api/Usuario`. |
| RF05 | El sistema debe permitir obtener un usuario por su identificador. | Alta | Implementado | `GET /api/Usuario/{id}`. |
| RF06 | El sistema debe permitir crear usuarios (con validación de email y documento únicos). | Alta | Implementado | `POST /api/Usuario`; contraseña hasheada antes de guardar. |
| RF07 | El sistema debe permitir actualizar usuarios. | Alta | Implementado | `PUT /api/Usuario/{id}`. |
| RF08 | El sistema debe permitir eliminar usuarios. | Media | Implementado | `DELETE /api/Usuario/{id}`. |
| RF09 | El sistema debe permitir el cambio de contraseña de un usuario. | Alta | Implementado | `POST /api/Usuario/changePassword`. |

---

## 3. Roles y catálogos de usuario

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF10 | El sistema debe gestionar roles (listar, obtener por id, crear, actualizar, eliminar). | Media | Implementado | `RolController`: GET, GET/{id}, POST, PUT/{id}, DELETE/{id}. |
| RF11 | El sistema debe gestionar tipos de documento (listar, obtener por id, crear, actualizar). | Media | Implementado | `TipoDocumentoControllers`: GET, GET/{id}, POST, PUT/{id}. |

---

## 4. Dispositivos

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF12 | El sistema debe permitir listar dispositivos (con tipo e información de usuario). | Media | Implementado | `GET /api/Dispositivo`. |
| RF13 | El sistema debe permitir obtener un dispositivo por su identificador. | Media | Implementado | `GET /api/Dispositivo/{id}`. |
| RF14 | El sistema debe permitir crear dispositivos asociados a un usuario y tipo. | Media | Implementado | `POST /api/Dispositivo`. |
| RF15 | El sistema debe permitir actualizar dispositivos. | Media | Implementado | `PUT /api/Dispositivo/{id}`. |
| RF16 | El sistema debe permitir eliminar dispositivos. | Media | Implementado | `DELETE /api/Dispositivo/{id}`. |
| RF17 | El sistema debe disponer de catálogo de tipos de dispositivo (ej. Laptop, Smartphone). | Baja | Implementado | Tabla `Tipo_dispositivo` y datos en DML; sin CRUD expuesto en la API (uso vía FK en Dispositivo). |

---

## 5. Auditoría de negocio

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF18 | El sistema debe permitir consultar los registros de auditoría de negocio (ingresos/salidas, etc.). | Media | Implementado | `GET /api/AudNegocio` (lista completa). |
| RF19 | El sistema debe disponer de catálogo de tipos de registro (ej. Ingreso, Salida). | Baja | Implementado | `TipoRegistroController`: GET, GET/{id}, POST, PUT/{id}. |
| RF20 | El sistema debe permitir crear/actualizar registros de auditoría de negocio desde la API. | Media | Pendiente | Tabla y modelo existen; no hay endpoints POST/PUT en el controlador actual. |

---

## 6. Reportes

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF21 | El sistema debe permitir listar reportes. | Media | Implementado | `GET /api/Reportes`. |
| RF22 | El sistema debe permitir obtener un reporte por su identificador. | Media | Implementado | `GET /api/Reportes/{id}`. |
| RF23 | El sistema debe permitir crear reportes (generado_por, sede, tipo, descripción, url_archivo, etc.). | Media | Implementado | `POST /api/Reportes`. |
| RF24 | El sistema debe disponer de catálogo de tipos de reporte (ej. Diario, Mensual). | Baja | Implementado | `TipoReporteController`: GET, GET/{id}, POST, PUT/{id}, DELETE/{id}. |
| RF25 | El sistema debe disponer de sedes para asociar a reportes. | Baja | Implementado | `SedesController`: GET, GET/{id}, POST, PUT/{id}, DELETE/{id}. |

---

## 7. Logs del sistema

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF26 | El sistema debe permitir consultar un log de sistema por su identificador. | Media | Implementado | `GET /api/LogSistema/{id}`. |
| RF27 | El sistema debe permitir listar logs (p. ej. por usuario o fecha). | Media | Pendiente | Solo GET por id; listado/filtros no expuestos en la API. |
| RF28 | El sistema debe registrar acciones relevantes en logs (trazabilidad). | Alta | Implementado | Tabla `Log_Sistema` y modelo; la creación de registros puede hacerse desde lógica de negocio o middleware (no documentada en este listado). |

---

## 8. Interfaz de usuario (frontend)

| Id   | Requisito | Prioridad | Estado | Notas |
|------|-----------|-----------|--------|--------|
| RF29 | La aplicación debe ofrecer una interfaz web para usuarios y administradores. | Alta | Pendiente | Carpeta CodigoForntend prevista; sin implementación. |
| RF30 | La interfaz debe consumir la API usando autenticación JWT. | Alta | Pendiente | Depende de RF29. |
| RF31 | La interfaz debe permitir realizar las operaciones previstas (login, usuarios, dispositivos, auditoría, reportes, etc.) según el rol. | Alta | Pendiente | Depende de RF29. |

---

## Resumen por estado

| Estado        | Cantidad | Observación |
|---------------|----------|-------------|
| **Implementado** | 26      | Cubierto por API y/o BD. |
| **Pendiente**    | 5       | RF20 (alta de auditoría vía API), RF27 (listado logs), RF29–RF31 (frontend). |

---

## Referencias

- [01_Vision_y_Alcance](01_Vision_y_Alcance.md)
- [README principal](../README.md) y Swagger (en ejecución) – Controladores, uso de la API y detalle de endpoints
- Código: `CodigoBackend/Auditorias/Controllers/`
