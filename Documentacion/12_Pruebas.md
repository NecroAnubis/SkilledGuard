# 12 – Pruebas

**Proyecto:** SkilledGuard  
**Documento:** Estrategia de pruebas y casos clave  
**Referencia:** [02_Requisitos_Funcionales](02_Requisitos_Funcionales.md), [06_API_Endpoints](06_API_Endpoints.md), [08_Guia_Desarrollo](08_Guia_Desarrollo.md).

---

## 1. Estado actual

En el estado actual del proyecto **no hay un proyecto de pruebas automatizadas** (ni xUnit, NUnit ni MSTest) en la solución. La validación se realiza de forma **manual** mediante:

- **Swagger** (entorno Development): ejecución de endpoints y comprobación de respuestas.
- **Cliente REST** (Postman, Insomnia, etc.): peticiones con token JWT y verificación manual.

Este documento describe la **estrategia de pruebas** recomendada y los **casos clave** para pruebas manuales o para implementar cuando se añadan pruebas automatizadas.

---

## 2. Estrategia de pruebas recomendada

| Nivel | Qué probar | Herramientas típicas | Estado en el proyecto |
|-------|------------|----------------------|------------------------|
| **Unitarias** | Lógica aislada (ej. `PasswordHelper`, validaciones, mapeos). | xUnit, NUnit, MSTest | No implementadas. |
| **Integración (API + BD)** | Endpoints contra una BD de prueba: respuestas HTTP, datos persistidos. | ASP.NET Core `WebApplicationFactory`, BD en memoria o SQL Server de prueba. | No implementadas. |
| **Pruebas E2E** | Flujo completo desde el cliente (ej. login → listar usuarios). | Playwright, Selenium, Cypress (cuando exista frontend). | No aplicable (sin frontend). |
| **Pruebas manuales** | Login, CRUD, flujos críticos con Swagger o cliente REST. | Swagger, Postman. | En uso. |

---

## 3. Datos de prueba (DML)

El script **`Base_de_Datos/DML_base_de_datos.sql`** inserta datos que sirven para probar la API:

| Dato | Uso en pruebas |
|------|-----------------|
| **Usuarios** | Juan Pérez (`juan@correo.com`) y Ana Gómez (`ana@correo.com`). Las contraseñas de prueba se definen en el DML; si la API almacena contraseñas hasheadas, el DML debe contener el hash (no texto plano). Ver credenciales de login en el [README](../README.md) o en el DML. |
| **Roles** | Administrador, Usuario (para probar permisos cuando se implementen por rol). |
| **Catálogos** | Tipos de documento, tipos de dispositivo, tipos de registro, tipos de reporte, sedes (necesarios para crear usuarios, dispositivos, reportes). |
| **Registros de ejemplo** | Logs, dispositivos, auditorías, reportes (para probar GET lista y GET por id). |

**Recomendación:** usar una **copia de la BD** o una BD dedicada (ej. `auditoria_sistema_test`) para pruebas automatizadas, para no alterar datos de desarrollo. En integración, se puede ejecutar DDL + DML antes de cada suite o usar transacciones que se revierten.

---

## 4. Casos clave para pruebas manuales (checklist)

Comprobar con Swagger o un cliente REST, con el backend y la BD en ejecución.

### 4.1 Autenticación

| Caso | Pasos | Resultado esperado |
|------|--------|--------------------|
| Login correcto | `POST /api/Auth/login` con email y contraseña válidos (usuario del DML). | 200; cuerpo con `token` y `usuario` (id, nombres, apellidos, email, rol). |
| Login incorrecto | `POST /api/Auth/login` con contraseña errónea o email inexistente. | 401; mensaje de credenciales inválidas. |
| Acceso sin token | Llamar a `GET /api/Usuario` sin header `Authorization`. | 401. |
| Acceso con token válido | Llamar a `GET /api/Usuario` con `Authorization: Bearer <token>` (token del login). | 200; lista de usuarios. |
| Token inválido o expirado | Llamar con token mal formado o expirado. | 401. |

### 4.2 Usuarios

| Caso | Pasos | Resultado esperado |
|------|--------|--------------------|
| Listar usuarios | `GET /api/Usuario` con token. | 200; array de usuarios (sin contraseña). |
| Obtener por id | `GET /api/Usuario/{id}` con id existente. | 200; objeto usuario. |
| Crear usuario | `POST /api/Usuario` con cuerpo válido (nombres, email, documento, id_rol, id_tipo_documento, contraseña, etc.). | 200; usuario creado. |
| Crear con email duplicado | `POST /api/Usuario` con email ya existente. | 400; mensaje indicando que el email ya está registrado. |
| Actualizar usuario | `PUT /api/Usuario/{id}` con cuerpo parcial o completo. | 200. |
| Eliminar usuario | `DELETE /api/Usuario/{id}`. | 200. |
| Cambiar contraseña | `POST /api/Usuario/changePassword` con idUsuario, contraseñaActual, nuevaContraseña. | 200 con contraseña correcta; 404 o error si no. |

### 4.3 Dispositivos, reportes y auditoría

| Área | Casos mínimos |
|------|----------------|
| **Dispositivos** | GET lista, GET por id, POST (con id_usuario e id_tipo_dispositivo válidos), PUT, DELETE. |
| **Reportes** | GET lista, GET por id, POST (generado_por, sede, id_tipo_reporte, etc.). |
| **Auditoría de negocio** | GET /api/AuditoriaNegocio devuelve lista de registros. |
| **Logs** | GET /api/LogSistema/{id} con un id existente del DML devuelve el log. |
| **Catálogos** | GET de Rol, TipoDocumento, TipoRegistro, TipoReporte, Sede (listas y por id según el controlador). |

---

## 5. Recomendaciones para pruebas automatizadas (futuro)

Cuando se incorporen pruebas al proyecto:

1. **Proyecto de pruebas:** añadir un proyecto de tipo “xUnit Test Project” (o NUnit/MSTest) a la solución, referenciando el proyecto `Auditorias`.
2. **Unitarias:** probar `PasswordHelper.HashPassword` y `VerifyPassword` con contraseñas conocidas; probar DTOs y validaciones si se extraen a clases reutilizables.
3. **Integración API:** usar `WebApplicationFactory<Program>` (ASP.NET Core) para levantar la API en memoria; opcionalmente usar SQL Server en contenedor o BD en memoria (EF In-Memory) para no depender de una BD compartida; ejecutar DDL/DML de prueba si se usa BD real.
4. **Datos aislados:** no depender del orden de ejecución; crear los datos necesarios en el test o usar una BD que se restaura por suite.
5. **Cobertura prioritaria:** login, CRUD de usuarios, endpoints que modifican datos (POST/PUT/DELETE) y respuestas de error (400, 401, 404).

---

## 6. Resumen

| Aspecto | Estado / acción |
|---------|------------------|
| **Pruebas automatizadas** | No existen; estrategia y casos documentados para implementación futura. |
| **Pruebas manuales** | Swagger y cliente REST; usar usuarios y datos del DML. |
| **Datos de prueba** | Definidos en `Base_de_Datos/DML_base_de_datos.sql`; credenciales de login según README o DML. |
| **Casos críticos** | Login, token en peticiones, CRUD usuarios, creación con validaciones (email/documento duplicado), y al menos un flujo por recurso (dispositivos, reportes, auditoría, logs, catálogos). |

---

## Referencias

- [02_Requisitos_Funcionales](02_Requisitos_Funcionales.md) – Requisitos a validar
- [06_API_Endpoints](06_API_Endpoints.md) – Rutas y métodos
- [08_Guia_Desarrollo](08_Guia_Desarrollo.md) – Cómo ejecutar backend y Swagger
- [README principal](../README.md) – Credenciales de ejemplo para login
- Datos: `Base_de_Datos/DML_base_de_datos.sql`
