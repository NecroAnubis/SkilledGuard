# 06 – API Endpoints

**Proyecto:** SkilledGuard  
**Documento:** Índice de endpoints de la API REST  
**Referencia:** Generado a partir de los controladores del proyecto. La **fuente de verdad** para probar y ver contratos es **Swagger** (habilitado en entorno Development).

---

## Uso del token JWT

- **Login:** `POST /api/Auth/login` no requiere token (`[AllowAnonymous]`).
- **Resto de endpoints:** requieren el header `Authorization: Bearer <token>` (salvo `POST /api/Usuario` que tiene `[AllowAnonymous]` para permitir crear el primer usuario).
- Sustituir `<token>` por el valor devuelto en la respuesta del login.

---

## 1. Autenticación

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| POST | `/api/Auth/login` | No (AllowAnonymous) | `{ "email": "string", "contraseña": "string" }` | 200: `{ token, usuario: { id, nombres, apellidos, email, rol } }` · 401: Credenciales inválidas |

---

## 2. Usuario

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/Usuario` | JWT | — | 200: lista de usuarios (sin contraseña) · 404/500 |
| GET | `/api/Usuario/{id}` | JWT | — | 200: usuario · 404 |
| POST | `/api/Usuario` | No (AllowAnonymous) | Objeto `Usuario` (nombres, apellidos, id_tipo_documento, documento, tipo_usuario, email, direccion, contraseña, id_rol) | 200: usuario creado · 400: email o documento ya registrado |
| PUT | `/api/Usuario/{id}` | JWT | Objeto `Usuario` (campos a actualizar) | 200 · 404 |
| DELETE | `/api/Usuario/{id}` | JWT | — | 200 · 404 |
| POST | `/api/Usuario/changePassword` | JWT | `{ "idUsuario": "guid", "contraseñaActual": "string", "nuevaContraseña": "string" }` | 200 · 404 |

---

## 3. Rol

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/Rol` | JWT | — | 200: lista de roles · 404 |
| GET | `/api/Rol/{id}` | JWT | — | 200: rol · 404 |
| POST | `/api/Rol` | JWT | Objeto `Rol` (nombre, descripcion) | 200 |
| PUT | `/api/Rol/{id}` | JWT | Objeto `Rol` | 200 · 404 |
| DELETE | `/api/Rol/{id}` | JWT | — | 200 · 404 |

---

## 4. Tipo de documento

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/TipoDocumento` | JWT | — | 200: lista · 404 |
| GET | `/api/TipoDocumento/{id}` | JWT | — | 200: tipo documento · 404 |
| POST | `/api/TipoDocumento` | JWT | Objeto (nombre, acronimo) | 201 Created · 400 |
| PUT | `/api/TipoDocumento/{id}` | JWT | Objeto (nombre, acronimo) | 200 · 404 |

---

## 5. Log del sistema

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/LogSistema/{id}` | JWT | — | 200: log · 404 · 500 |

*No hay endpoint para listar logs ni para crear desde la API en el estado actual.*

---

## 6. Dispositivo

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/Dispositivo` | JWT | — | 200: lista (con tipo e info de usuario) · 400 |
| GET | `/api/Dispositivo/{id}` | JWT | — | 200: dispositivo · 404 |
| POST | `/api/Dispositivo` | JWT | Objeto (serial, marca, modelo, sistema, descripcion, foto_url, qr, id_tipo_dispositivo, id_usuario) | 200 · 404 |
| PUT | `/api/Dispositivo/{id}` | JWT | Objeto Dispositivo | 200 · 404 |
| DELETE | `/api/Dispositivo/{id}` | JWT | — | 200 · 404 |

---

## 7. Auditoría de negocio

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/AuditoriaNegocio` | JWT | — | 200: lista de registros de auditoría · 400/500 |

*Ruta base del controlador: `AuditoriaNegocio` (clase `AuditoriaNegocioController`). No hay POST/PUT/DELETE en el estado actual.*

---

## 8. Tipo de registro

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/TipoRegistro` | JWT | — | 200: lista · 404 |
| GET | `/api/TipoRegistro/{id}` | JWT | — | 200: tipo registro · 404 |
| POST | `/api/TipoRegistro` | JWT | Objeto (nombre) | 201 · 400 |
| PUT | `/api/TipoRegistro/{id}` | JWT | Objeto (nombre) | 200 · 404 |

---

## 9. Reportes

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/Reportes` | JWT | — | 200: lista de reportes · 404 |
| GET | `/api/Reportes/{id}` | JWT | — | 200: reporte · 404 |
| POST | `/api/Reportes` | JWT | Objeto (generado_por, sede, descripcion, fecha_generado, url_archivo, id_tipo_reporte) | 200 · 404 |

*No hay PUT ni DELETE en el controlador actual.*

---

## 10. Tipo de reporte

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/TipoReporte` | JWT | — | 200: lista · 404 |
| GET | `/api/TipoReporte/{id}` | JWT | — | 200: tipo reporte · 404 |
| POST | `/api/TipoReporte` | JWT | Objeto (nombre) | 201 · 400 |
| PUT | `/api/TipoReporte/{id}` | JWT | Objeto (nombre) | 200 · 404 |
| DELETE | `/api/TipoReporte/{id}` | JWT | — | 200 · 404 |

---

## 11. Sede

| Método | Ruta | Auth | Cuerpo | Respuestas |
|--------|------|------|--------|------------|
| GET | `/api/Sede` | JWT | — | 200: lista de sedes · 404 |
| GET | `/api/Sede/{id}` | JWT | — | 200: sede · 404 |
| POST | `/api/Sede` | JWT | Objeto (nombre_sede) | 200 · 404 |
| PUT | `/api/Sede/{id}` | JWT | Objeto (nombre_sede) | 200 · 404 |
| DELETE | `/api/Sede/{id}` | JWT | — | 200 · 404 |

---

## Resumen por controlador

| Prefijo ruta | Controlador | GET lista | GET por id | POST | PUT | DELETE |
|--------------|-------------|-----------|------------|------|-----|--------|
| /api/Auth | Auth | — | — | login | — | — |
| /api/Usuario | Usuario | ✓ | ✓ | ✓, changePassword | ✓ | ✓ |
| /api/Rol | Rol | ✓ | ✓ | ✓ | ✓ | ✓ |
| /api/TipoDocumento | TipoDocumento | ✓ | ✓ | ✓ | ✓ | — |
| /api/LogSistema | LogSistema | — | ✓ | — | — | — |
| /api/Dispositivo | Dispositivo | ✓ | ✓ | ✓ | ✓ | ✓ |
| /api/AuditoriaNegocio | AuditoriaNegocio | ✓ | — | — | — | — |
| /api/TipoRegistro | TipoRegistro | ✓ | ✓ | ✓ | ✓ | — |
| /api/Reportes | Reportes | ✓ | ✓ | ✓ | — | — |
| /api/TipoReporte | TipoReporte | ✓ | ✓ | ✓ | ✓ | ✓ |
| /api/Sede | Sede | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## Colección de Postman

Se incluye una colección lista para importar en Postman: `Postman/SkilledGuard_API.postman_collection.json`

**Uso:** 1) Importar la colección. 2) Configurar `baseUrl` (http://localhost:5164 o https://localhost:7086). 3) Ejecutar Auth → Login para obtener el token (se guarda en variable `token`). 4) El resto de endpoints usan el token automáticamente.

---

## Referencias

- **Swagger** (en ejecución, entorno Development): documentación interactiva y contratos actualizados. Se abre automáticamente al ejecutar la API.
- [README principal](../README.md) – Uso de la API y login de ejemplo.
- [04_Arquitectura_Sistema](04_Arquitectura_Sistema.md) – Flujo JWT y pipeline.
- [02_Requisitos_Funcionales](02_Requisitos_Funcionales.md) – Requisitos asociados a cada recurso.
- Código: `CodigoBackend/Auditorias/Controllers/`
