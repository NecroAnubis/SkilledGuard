# SkilledGuard

Sistema de auditoría para gestión de usuarios, dispositivos, registros de negocio y reportes. Incluye autenticación JWT, roles y trazabilidad mediante logs del sistema.

---

## Tabla de contenidos

- [Descripción del proyecto](#descripción-del-proyecto)
- [Tecnologías y lenguajes](#tecnologías-y-lenguajes)
- [Arquitectura](#arquitectura)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Base de datos](#base-de-datos)
- [Backend (API)](#backend-api)
- [Metodologías y convenciones](#metodologías-y-convenciones)
- [Requisitos previos](#requisitos-previos)
- [Paso a paso: configuración y ejecución](#paso-a-paso-configuración-y-ejecución)
- [Configuración](#configuración)
- [Uso de la API](#uso-de-la-api)
- [Frontend](#frontend)

---

## Descripción del proyecto

**SkilledGuard** es una aplicación de auditoría que permite:

- **Usuarios y roles**: Gestión de usuarios con roles (Administrador / Usuario), tipos de documento y autenticación segura.
- **Dispositivos**: Registro de dispositivos (por ejemplo laptops, smartphones) asociados a usuarios, con serial, marca, modelo, sistema y códigos QR.
- **Auditoría de negocio**: Registro de eventos de ingreso/salida u otros tipos, con fecha y usuario que los registra.
- **Reportes**: Generación de reportes por sede y tipo (diario, mensual), con URL de archivo.
- **Logs del sistema**: Trazabilidad de acciones mediante logs asociados a usuarios.

La solución está organizada en **base de datos**, **backend (API REST)** y **frontend** (carpeta prevista para la interfaz de usuario).

---

## Tecnologías y lenguajes

| Componente   | Tecnología |
|-------------|------------|
| **Backend** | C# / .NET 9.0 (ASP.NET Core Web API) |
| **Base de datos** | Microsoft SQL Server, SQL (DDL/DML) |
| **ORM** | Entity Framework Core 9.x |
| **Autenticación** | JWT (JSON Web Tokens) con `Microsoft.AspNetCore.Authentication.JwtBearer` |
| **Documentación API** | Swagger (Swashbuckle.AspNetCore 6.6.2) |
| **IDE / Solución** | Visual Studio 2022 (solución .sln), .NET 9 |
| **Frontend** | Carpeta preparada para implementación (ver sección [Frontend](#frontend)) |

---

## Arquitectura

- **Tipo**: API REST sobre ASP.NET Core.
- **Patrón**: Capas implícitas (Controllers → DbContext/Data → Models).
- **Base de datos**: SQL Server; acceso mediante Entity Framework Core (Code-First compatible con scripts DDL existentes).
- **Seguridad**: Autenticación JWT; endpoints protegidos con `[Authorize]`; login público con `[AllowAnonymous]`.
- **Flujo**:
  1. Cliente envía credenciales a `POST /api/Auth/login`.
  2. El servidor valida y devuelve un token JWT.
  3. Las peticiones subsiguientes incluyen el token en el header `Authorization: Bearer <token>`.
  4. Los controladores acceden a datos a través de `AuditoriaContext` (EF Core).

---

## Estructura del proyecto

```
SkilledGuard/
├── SkilledGuard.sln              # Solución Visual Studio
├── README.md                     # Este archivo
├── .gitignore
│
├── Base_de_Datos/                # Scripts SQL
│   ├── DDL base de datos.sql     # Creación de BD y tablas
│   ├── DML base de datos.sql     # Datos iniciales (catálogos y ejemplos)
│   └── README.txt
│
├── CódigoBackend/                # API REST
│   ├── Dependencias.txt          # Comandos para instalar paquetes NuGet
│   ├── README.txt
│   └── Auditorias/               # Proyecto ASP.NET Core
│       ├── Auditorias.csproj
│       ├── Program.cs            # Configuración de servicios, JWT, EF, Swagger
│       ├── appsettings.json      # Cadena de conexión y JWT (no versionado si aplica)
│       ├── appsettings.Development.json
│       ├── Data/
│       │   └── AuditoriaContext.cs   # DbContext de EF Core
│       ├── Models/                    # Entidades (Usuario, Rol, Dispositivo, etc.)
│       ├── Controllers/              # API (Auth, Usuario, Dispositivo, Reportes, etc.)
│       └── utils/                    # Helpers (ej. PasswordHelper, DTOs)
│
└── CódigoForntend/               # Frontend (por implementar)
    └── README.txt
```

---

## Base de datos

- **Nombre de la base de datos**: `auditoria_sistema`.
- **Motor**: Microsoft SQL Server.

### Scripts

1. **DDL** (`Base_de_Datos/DDL base de datos.sql`): crea la base de datos y las tablas.
2. **DML** (`Base_de_Datos/DML base de datos.sql`): inserta datos de catálogos y ejemplos (roles, tipos de documento, tipos de dispositivo, tipos de registro, tipos de reporte, sedes, usuarios de prueba, logs, dispositivos, auditorías y reportes).

### Modelo de datos (resumen)

| Tabla              | Descripción |
|--------------------|-------------|
| `Rol`              | Roles (ej. Administrador, Usuario). |
| `Tipo_documento`   | Tipos de documento (CC, Pasaporte, etc.). |
| `Usuario`          | Usuarios; FK a `Tipo_documento` y `Rol`. |
| `Log_Sistema`      | Logs de sistema; FK a `Usuario`. |
| `Tipo_dispositivo` | Tipos de dispositivo (Laptop, Smartphone, etc.). |
| `Dispositivo`      | Dispositivos; FK a `Tipo_dispositivo` y `Usuario`. |
| `Tipo_registro`    | Tipos de registro (Ingreso, Salida). |
| `Auditoria_Negocio`| Registros de auditoría; FK a `Tipo_registro` y `Usuario`. |
| `Tipo_Reporte`     | Tipos de reporte (Diario, Mensual). |
| `Sede`             | Sedes. |
| `Reporte`          | Reportes; FK a `Usuario`, `Sede` y `Tipo_Reporte`. |

Las claves primarias son `UNIQUEIDENTIFIER` (GUID). Las fechas de creación/actualización usan `GETDATE()` donde corresponde.

---

## Backend (API)

- **Framework**: ASP.NET Core 9.0 (Web API).
- **Proyecto**: `CódigoBackend/Auditorias/Auditorias.csproj`.

### Dependencias principales (NuGet)

En `CódigoBackend/Dependencias.txt` se documentan los paquetes; en el `.csproj` están ya referenciados:

- `Microsoft.EntityFrameworkCore` + `SqlServer` + `Tools`
- `Microsoft.AspNetCore.Authentication.JwtBearer`
- `Swashbuckle.AspNetCore`

### Configuración en `Program.cs`

- **Entity Framework**: `AuditoriaContext` con SQL Server usando la cadena `AuditoriaConnection` de `appsettings.json`.
- **JWT**: esquema por defecto Bearer; clave e issuer configurables desde `appsettings` (con valores por defecto si no se definen).
- **Swagger**: habilitado en entorno de desarrollo.
- **Pipeline**: HTTPS, autenticación, autorización y mapeo de controladores.

### Capas

- **Controllers**: exponen endpoints REST bajo `api/[controller]`; inyectan `AuditoriaContext` e `IConfiguration` cuando se necesita.
- **Data**: `AuditoriaContext` define los `DbSet` para cada entidad y se usa en los controladores.
- **Models**: entidades con `[Table]` y `[Column]` para mapeo a las tablas existentes; relaciones con `[ForeignKey]` y navegación.

### Controladores (recursos expuestos)

| Controlador           | Recurso principal |
|-----------------------|-------------------|
| `AuthController`       | Login (JWT), cambio de contraseña (si se implementa). |
| `UsuarioController`   | CRUD usuarios. |
| `RolController`       | Roles. |
| `TipoDocumentoControllers` | Tipos de documento. |
| `LogSistemaController`| Logs del sistema. |
| `TipoDispositivo` / `DispositivoController` | Tipos de dispositivo y dispositivos. |
| `AudNegocioController`| Auditoría de negocio. |
| `TipoRegistroController` | Tipos de registro. |
| `SedesController`     | Sedes. |
| `TipoReporteController` / `ReportesController` | Tipos de reporte y reportes. |

### Autenticación

- **Login**: `POST /api/Auth/login` con cuerpo JSON `{ "email": "...", "contraseña": "..." }`.
- Respuesta: token JWT y datos básicos del usuario (id, nombres, apellidos, email, rol).
- Las contraseñas se almacenan con hash (uso de `PasswordHelper` en el login).
- Endpoints que requieren autenticación deben enviar: `Authorization: Bearer <token>`.

---

## Metodologías y convenciones

- **Arquitectura**: API REST por capas (controladores, contexto de datos, modelos).
- **Convención de rutas**: `api/[controller]` para todos los controladores.
- **Base de datos**: diseño relacional con tablas normalizadas y FKs; identificadores GUID.
- **Seguridad**: JWT para sesión; contraseñas hasheadas; uso de `[Authorize]` y `[AllowAnonymous]` según el caso.
- **Documentación**: Swagger para explorar y probar la API en desarrollo.
- **Configuración**: cadenas de conexión y JWT en `appsettings.json` (no versionar datos sensibles en producción; usar variables de entorno o secretos).

---

## Requisitos previos

- **.NET 9 SDK** (compatible con el `<TargetFramework>net9.0</TargetFramework>` del proyecto).
- **SQL Server** (local o remoto) con permisos para crear base de datos y ejecutar DDL/DML.
- **Visual Studio 2022** (recomendado) o **VS Code** / línea de comandos con `dotnet CLI`.
- (Opcional) Cliente REST (Postman, Insomnia o Swagger UI) para probar la API. Se incluye colección de Postman en `Postman/SkilledGuard_API.postman_collection.json`.

---

## Paso a paso: configuración y ejecución

### 1. Clonar o abrir el proyecto

- Abrir la carpeta del proyecto en el IDE o, en terminal, navegar a la raíz del repositorio (donde está `SkilledGuard.sln`).

### 2. Crear la base de datos

1. Conectar a SQL Server (SQL Server Management Studio, Azure Data Studio o `sqlcmd`).
2. Ejecutar **en orden**:
   - `Base_de_Datos/DDL base de datos.sql` (crear BD y tablas).
   - `Base_de_Datos/DML base de datos.sql` (poblar datos iniciales).
3. Verificar que la base de datos `auditoria_sistema` existe y tiene datos (por ejemplo, usuarios de prueba).

### 3. Configurar la cadena de conexión y JWT

1. Ir a `CódigoBackend/Auditorias/`.
2. En `appsettings.json` (o `appsettings.Development.json`), ajustar:
   - **ConnectionStrings:AuditoriaConnection**: servidor, base de datos (`auditoria_sistema`), y si aplica usuario/contraseña o `Trusted_Connection=True;TrustServerCertificate=True;`.
   - **Jwt:Key** y **Jwt:Issuer** (en producción usar valores seguros y no subirlos al repositorio).

Ejemplo de estructura (los valores deben coincidir con tu entorno):

```json
{
  "ConnectionStrings": {
    "AuditoriaConnection": "Server=TU_SERVIDOR;Database=auditoria_sistema;Trusted_Connection=True;TrustServerCertificate=True;"
  },
  "Jwt": {
    "Key": "tu_clave_secreta_larga_y_segura",
    "Issuer": "SkilledGuard"
  },
  "Logging": { ... },
  "AllowedHosts": "*"
}
```

### 4. Restaurar dependencias y ejecutar el backend

En la raíz del proyecto (donde está la solución):

```bash
dotnet restore
dotnet build
```

Para ejecutar solo el proyecto de la API:

```bash
dotnet run --project CódigoBackend/Auditorias/Auditorias.csproj
```

O abrir `SkilledGuard.sln` en Visual Studio, establecer **Auditorias** como proyecto de inicio y pulsar F5.

### 5. Probar la API

- **Swagger**: en desarrollo, se abre automáticamente al ejecutar la API (`http://localhost:5164/swagger` o `https://localhost:7086/swagger`).
- **Postman**: importe la colección `Postman/SkilledGuard_API.postman_collection.json` para probar todos los endpoints.
- **Login**: en Swagger o Postman, llamar a `POST /api/Auth/login` con un usuario del DML, por ejemplo:
  - `juan@correo.com` / `clave123` (Administrador)
  - `ana@correo.com` / `clave456` (Usuario)
  - `admin@skilledguard.com` / `admin123` (Administrador)
  - `usuario@skilledguard.com` / `user123` (Usuario)

A partir de aquí, cualquier desarrollador puede seguir la documentación de Swagger y este README para integrar o extender la API.

---

## Configuración

- **Cadena de conexión**: `ConnectionStrings:AuditoriaConnection` en `appsettings.json`.
- **JWT**: `Jwt:Key` (clave secreta) y `Jwt:Issuer` (emisor del token). En producción se recomienda usar variables de entorno o un gestor de secretos en lugar de dejar la clave en el archivo.
- **Swagger**: solo se activa en entorno `Development` (configurado en `Program.cs`).

---

## Uso de la API

1. **Login**  
   `POST /api/Auth/login`  
   Body: `{ "email": "juan@correo.com", "contraseña": "clave123" }`  
   Respuesta: `{ "token": "...", "usuario": { "id", "nombres", "apellidos", "email", "rol" } }`.

2. **Llamadas protegidas**  
   Añadir en las peticiones el header:  
   `Authorization: Bearer <token_devuelto_en_login>`.

3. **Recursos adicionales**  
   Usar Swagger en desarrollo para ver todos los endpoints (usuarios, roles, dispositivos, auditorías, reportes, sedes, etc.) y sus métodos (GET, POST, PUT, DELETE).

---

## Frontend

La carpeta **CódigoForntend** está prevista para la interfaz de usuario de SkilledGuard. Por el momento no contiene código de aplicación; cuando se implemente, se recomienda:

- Consumir la API en `CódigoBackend/Auditorias` usando la URL base del backend (ej. `https://localhost:7xxx`).
- Enviar el token JWT en el header `Authorization: Bearer <token>` en cada petición autenticada.
- Documentar en este README o en un `README.md` dentro de `CódigoForntend` el stack elegido (React, Angular, Vue, etc.) y los pasos de instalación y ejecución.

---

## Resumen para desarrolladores y usuarios

- **Objetivo**: Sistema de auditoría (usuarios, dispositivos, registros de negocio, reportes) con API REST y autenticación JWT.
- **Stack**: .NET 9, SQL Server, Entity Framework Core, JWT, Swagger.
- **Para ejecutar**: crear la BD con los scripts DDL/DML, configurar conexión y JWT en `appsettings.json`, y ejecutar el proyecto `Auditorias` con `dotnet run` o desde Visual Studio.
- **Para integrar**: usar `POST /api/Auth/login` para obtener el token y el resto de endpoints documentados en Swagger con el token en el header `Authorization`.

Si necesitas ampliar alguna sección (por ejemplo, despliegue, pruebas o detalle de un controlador), se puede extender este README en consecuencia.
