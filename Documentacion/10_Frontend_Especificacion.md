# 10 – Frontend: especificación

**Proyecto:** SkilledGuard  
**Documento:** Especificación del frontend (interfaz de usuario)  
**Referencia:** [README principal](../README.md) (sección Frontend), API en [06_API_Endpoints](06_API_Endpoints.md).

---

## 1. Estado actual

La carpeta **CodigoForntend** está prevista para la interfaz de usuario de SkilledGuard. **Por el momento no contiene implementación** (solo un README mínimo). Este documento define qué debe cumplir el frontend cuando se implemente y sirve como especificación y checklist.

---

## 2. Objetivo del frontend

- Ofrecer una **interfaz web** para que usuarios y administradores utilicen el sistema de auditoría.
- Consumir la **API REST** del backend (`CodigoBackend/Auditorias`) para todas las operaciones de datos.
- Permitir **login**, gestión de **usuarios**, **dispositivos**, **auditoría de negocio**, **reportes** y consulta de **logs** según el rol (Administrador / Usuario).

---

## 3. Integración con la API

Cualquier implementación del frontend debe cumplir lo siguiente:

| Aspecto | Requisito |
|---------|-----------|
| **URL base del backend** | Configurable (p. ej. variable de entorno). En desarrollo suele ser la URL donde corre la API (ej. `https://localhost:7xxx`). |
| **Autenticación** | Login mediante `POST /api/Auth/login` con cuerpo `{ "email": "...", "contraseña": "..." }`. La respuesta incluye `token` y `usuario`. |
| **Peticiones autenticadas** | Incluir en todas las peticiones que requieran autenticación el header: `Authorization: Bearer <token>`. |
| **Almacenamiento del token** | Guardar el token (y opcionalmente datos del usuario) en memoria, sessionStorage o localStorage; renovar o redirigir a login cuando el backend devuelva 401. |
| **Endpoints disponibles** | Ver listado completo en [06_API_Endpoints](06_API_Endpoints.md). Recursos: Auth, Usuario, Rol, TipoDocumento, LogSistema, Dispositivo, AuditoriaNegocio, TipoRegistro, Reportes, TipoReporte, Sede. |

**CORS:** Si el frontend se sirve desde otro origen (puerto o dominio distinto al del backend), en el backend debe configurarse CORS para permitir ese origen (ver [09_Configuracion_Entornos](09_Configuracion_Entornos.md)).

---

## 4. Stack tecnológico (a definir)

Cuando se implemente el frontend, completar en este documento o en el README de CodigoForntend:

| Elemento | Descripción | Ejemplo (a rellenar) |
|----------|-------------|----------------------|
| **Framework / librería** | React, Angular, Vue, u otra. | _Por definir_ |
| **Lenguaje** | TypeScript recomendado para tipado y mantenibilidad. | _Por definir_ |
| **Gestor de estado** | Si se usa (Redux, Context, Pinia, etc.). | _Por definir_ |
| **Cliente HTTP** | Axios, fetch nativo, HttpClient, etc. | _Por definir_ |
| **Enrutamiento** | React Router, Vue Router, Angular Router, etc. | _Por definir_ |
| **UI / componentes** | Librería de componentes (Material UI, Bootstrap, etc.) o propio. | _Por definir_ |
| **Herramienta de build** | Vite, Create React App, Angular CLI, etc. | _Por definir_ |

---

## 5. Estructura de carpetas (recomendación)

Cuando exista implementación, se recomienda documentar una estructura coherente. Ejemplo genérico (adaptar al stack elegido):

```text
CodigoForntend/
├── public/                 # Assets estáticos (index.html, favicon)
├── src/
│   ├── api/                # Cliente HTTP, configuración base URL, interceptores (token)
│   ├── components/         # Componentes reutilizables
│   ├── pages/ o views/     # Pantallas (Login, Usuarios, Dispositivos, Reportes, etc.)
│   ├── store/ o context/   # Estado global (usuario, token) si aplica
│   ├── routes/             # Definición de rutas
│   ├── utils/ o helpers/   # Utilidades
│   └── App.tsx / main.tsx  # Punto de entrada
├── package.json
├── .env.example            # Variables de entorno (ej. VITE_API_BASE_URL)
└── README.md               # Instalación y ejecución (ver doc 11)
```

Actualizar esta sección cuando se fije la estructura real.

---

## 6. Convenciones recomendadas

- **URL base de la API:** leer desde variable de entorno (ej. `VITE_API_BASE_URL` o `REACT_APP_API_BASE_URL`) para no hardcodear entornos.
- **Token:** añadir automáticamente el header `Authorization: Bearer <token>` en todas las peticiones autenticadas (interceptor o wrapper del cliente HTTP).
- **Respuesta 401:** cerrar sesión o redirigir a la pantalla de login y limpiar token.
- **Manejo de errores:** mostrar mensajes claros al usuario (credenciales incorrectas, error de red, etc.).
- **Roles:** usar el rol devuelto en el login para mostrar u ocultar opciones (ej. solo administradores gestionan usuarios o reportes).

---

## 7. Pantallas / funcionalidades previstas

A modo de checklist para la implementación:

| Área | Funcionalidad |
|------|----------------|
| **Login** | Formulario email/contraseña; llamada a `POST /api/Auth/login`; guardar token y usuario; redirigir al inicio. |
| **Usuarios** | Listar (GET /api/Usuario), ver detalle, crear, editar, eliminar, cambiar contraseña (según permisos). |
| **Dispositivos** | Listar, ver, crear, editar, eliminar (GET/POST/PUT/DELETE /api/Dispositivo). |
| **Auditoría de negocio** | Listar registros (GET /api/AuditoriaNegocio); crear/editar cuando la API lo exponga. |
| **Reportes** | Listar, ver detalle, crear (GET/POST /api/Reportes). |
| **Catálogos** | Roles, tipos de documento, tipos de dispositivo, tipos de registro, tipos de reporte, sedes (según necesidad en formularios). |
| **Logs** | Consulta por id (GET /api/LogSistema/{id}); listado cuando la API lo ofrezca. |

---

## 8. Actualización de este documento

Cuando el frontend esté implementado:

1. Completar la sección **4. Stack tecnológico** con las tecnologías elegidas.
2. Ajustar la sección **5. Estructura de carpetas** a la estructura real del proyecto.
3. Añadir o enlazar la [11_Frontend_Guia_Instalacion](11_Frontend_Guia_Instalacion.md) para instalación y ejecución.
4. Mantener la sección **3. Integración con la API** como referencia; si hay particularidades (ej. refresh token), documentarlas aquí.

---

## Referencias

- [README principal](../README.md) – Sección Frontend
- [06_API_Endpoints](06_API_Endpoints.md) – Listado de endpoints de la API
- [04_Arquitectura_Sistema](04_Arquitectura_Sistema.md) – Flujo de autenticación JWT
- [09_Configuracion_Entornos](09_Configuracion_Entornos.md) – CORS y configuración por entorno
- Carpeta del proyecto: `CodigoForntend/`
