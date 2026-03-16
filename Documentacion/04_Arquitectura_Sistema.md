# 04 – Arquitectura del sistema

**Proyecto:** SkilledGuard  
**Documento:** Arquitectura del sistema  
**Referencia:** Resumen y ampliación de la sección de arquitectura del [README principal](../README.md) y de `Program.cs`.

---

## 1. Vista general

SkilledGuard se organiza en tres partes:

1. **Cliente** (navegador, aplicación móvil o otro servicio) que consume la API.
2. **Backend (API REST)** sobre ASP.NET Core 9: autenticación JWT, controladores y acceso a datos.
3. **Base de datos** SQL Server (`auditoria_sistema`), accedida mediante Entity Framework Core.

```
┌─────────────┐         HTTPS          ┌──────────────────────────────────┐         ┌──────────────┐
│   Cliente   │ ◄──────────────────►  │  API REST (ASP.NET Core 9)       │ ◄─────► │  SQL Server  │
│ (frontend,  │   Authorization:       │  • Controllers                   │   EF    │  auditoria_  │
│  Postman…)  │   Bearer <token>       │  • Data (AuditoriaContext)        │  Core   │  sistema     │
└─────────────┘                        │  • Models                        │         └──────────────┘
                                        └──────────────────────────────────┘
```

El **frontend** (carpeta CodigoForntend) está previsto pero no implementado; cuando exista, actuará como cliente de la API.

---

## 2. Capas del backend

El backend sigue un patrón de **capas implícitas** (sin proyectos separados de “servicios” o “repositorios”): los controladores usan directamente el contexto de datos y los modelos.

| Capa | Carpeta / componente | Responsabilidad |
|------|----------------------|------------------|
| **API** | `Controllers/` | Reciben peticiones HTTP, validan (y en algunos casos construyen el JWT), llaman al contexto y devuelven respuestas (JSON). |
| **Datos** | `Data/AuditoriaContext.cs` | DbContext de Entity Framework Core: define los `DbSet` por entidad y la conexión a SQL Server. |
| **Modelos** | `Models/` | Entidades C# mapeadas a tablas (atributos `[Table]`, `[Column]`, `[ForeignKey]`). |
| **Utilidades** | `utils/` | Helpers (por ejemplo `PasswordHelper` para hash de contraseñas, DTOs como `LoginRequest`, `CambiarContraseñaRequest`). |

Flujo típico de una petición protegida:

1. El middleware de autenticación valida el token JWT del header `Authorization`.
2. El controlador correspondiente recibe la petición (inyección de `AuditoriaContext` e `IConfiguration` cuando se necesita).
3. El controlador consulta o modifica datos mediante el contexto (EF Core).
4. El controlador devuelve el resultado (por ejemplo `Ok(...)`, `NotFound()`, `BadRequest()`).

---

## 3. Flujo de autenticación JWT

1. **Login (sin token)**  
   El cliente envía `POST /api/Auth/login` con cuerpo JSON `{ "email": "...", "contraseña": "..." }`.  
   El endpoint tiene `[AllowAnonymous]`, por lo que no se exige token.

2. **Validación**  
   El servidor busca el usuario por email, verifica la contraseña con `PasswordHelper.VerifyPassword` frente al hash almacenado y, si es correcta, construye un JWT con claims (id, email, rol).

3. **Respuesta**  
   El servidor devuelve HTTP 200 con un objeto que incluye el token y los datos básicos del usuario (id, nombres, apellidos, email, rol). La contraseña no se devuelve.

4. **Peticiones posteriores**  
   El cliente envía en cada petición el header:  
   `Authorization: Bearer <token>`.

5. **Validación del token**  
   El middleware JWT (`UseAuthentication`) valida emisor, firma y vigencia del token. Si es válido, el usuario queda identificado y el controlador puede ejecutarse; si no, se responde 401.

---

## 4. Pipeline de la aplicación

Orden de middleware en `Program.cs` (resumen):

| Orden | Middleware | Función |
|-------|------------|--------|
| 1 | Swagger / SwaggerUI | Solo en entorno `Development`: documentación e interfaz de la API. |
| 2 | `UseHttpsRedirection()` | Redirige peticiones HTTP a HTTPS. |
| 3 | `UseAuthentication()` | Valida el token JWT y establece la identidad del usuario. |
| 4 | `UseAuthorization()` | Comprueba permisos (por ejemplo `[Authorize]`). |
| 5 | `MapControllers()` | Enruta las peticiones a los controladores según `api/[controller]`. |

---

## 5. Componentes principales

| Componente | Ubicación | Descripción |
|------------|-----------|-------------|
| **AuditoriaContext** | `Data/AuditoriaContext.cs` | DbContext con `DbSet` para Usuario, Rol, Dispositivo, AuditoriaNegocio, Reporte, LogSistema, etc. |
| **AuthController** | `Controllers/AuthController.cs` | Login y generación del token JWT. |
| **PasswordHelper** | `utils/PasswordHelper.cs` | Hash y verificación de contraseñas (PBKDF2, SHA-256, salt). |
| **Configuración JWT** | `Program.cs` + `appsettings` | Clave (`Jwt:Key`), emisor (`Jwt:Issuer`) y parámetros de validación del token. |
| **Cadena de conexión** | `appsettings.json` | `ConnectionStrings:AuditoriaConnection` para SQL Server. |

---

## 6. Estructura de carpetas del backend

```
CodigoBackend/Auditorias/
├── Program.cs              # Registro de servicios (EF, JWT, Swagger) y pipeline
├── appsettings*.json       # Conexión BD y JWT
├── Controllers/            # Endpoints REST (Auth, Usuario, Dispositivo, Reportes, etc.)
├── Data/
│   └── AuditoriaContext.cs # DbContext EF Core
├── Models/                 # Entidades (Usuario, Rol, Dispositivo, Reporte, …)
└── utils/                 # PasswordHelper, DTOs (LoginRequest, CambiarContraseñaRequest)
```

---

## Referencias

- [README principal](../README.md) – Arquitectura, tecnologías y estructura del proyecto
- [01_Vision_y_Alcance](01_Vision_y_Alcance.md)
- [03_Requisitos_No_Funcionales](03_Requisitos_No_Funcionales.md) – Seguridad y JWT
- Código: `CodigoBackend/Auditorias/Program.cs`
