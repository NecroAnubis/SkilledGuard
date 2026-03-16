# 08 – Guía de desarrollo

**Proyecto:** SkilledGuard  
**Documento:** Guía de desarrollo (configuración y ejecución)  
**Referencia:** Resumen de la sección "Requisitos previos" y "Paso a paso" del [README principal](../README.md). Para el detalle completo, consultar ese README.

---

## 1. Requisitos previos

| Requisito | Descripción |
|-----------|-------------|
| **.NET 9 SDK** | Compatible con `net9.0` del proyecto. Comprobar con `dotnet --version`. |
| **SQL Server** | Local o remoto, con permisos para crear base de datos y ejecutar DDL/DML. |
| **IDE (opcional)** | Visual Studio 2022 (recomendado), VS Code o línea de comandos con `dotnet CLI`. |
| **Cliente REST (opcional)** | Postman, Insomnia o Swagger UI para probar la API. |

---

## 2. Clonar o abrir el proyecto

- Abrir la carpeta del proyecto en el IDE o, en terminal, ir a la **raíz del repositorio** (donde está `SkilledGuard.sln`).

---

## 3. Crear la base de datos

1. Conectar a SQL Server (SQL Server Management Studio, Azure Data Studio o `sqlcmd`).
2. Ejecutar **en este orden**:
   - `Base_de_Datos/DDL_base_de_datos.sql` — crea la base de datos y las tablas.
   - `Base_de_Datos/DML_base_de_datos.sql` — inserta catálogos y datos de prueba.
3. Comprobar que la base de datos `auditoria_sistema` existe y contiene datos (p. ej. usuarios de prueba).

Más detalle: [07_Base_de_Datos_Resumen](07_Base_de_Datos_Resumen.md) y [Base_de_Datos/README.txt](../Base_de_Datos/README.txt).

---

## 4. Configurar la API

1. Ir a la carpeta **`CodigoBackend/Auditorias/`**.
2. Editar **`appsettings.json`** o **`appsettings.Development.json`** y ajustar:
   - **ConnectionStrings:AuditoriaConnection** — servidor, base de datos (`auditoria_sistema`) y, si aplica, usuario/contraseña o `Trusted_Connection=True;TrustServerCertificate=True;`.
   - **Jwt:Key** — clave secreta para firmar el token (en producción usar valores seguros y no subirlos al repositorio).
   - **Jwt:Issuer** — emisor del token (p. ej. `"SkilledGuard"`).

Ejemplo de estructura:

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

---

## 5. Restaurar dependencias y compilar

En la **raíz del proyecto** (donde está `SkilledGuard.sln`):

```bash
dotnet restore
dotnet build
```

---

## 6. Ejecutar el backend

**Opción A – Línea de comandos (desde la raíz del proyecto):**

```bash
dotnet run --project CodigoBackend/Auditorias/Auditorias.csproj
```

**Opción B – Visual Studio:**  
Abrir `SkilledGuard.sln`, establecer **Auditorias** como proyecto de inicio y pulsar **F5** (o ejecutar con depuración).

La consola mostrará la URL de la API (por ejemplo `https://localhost:7xxx`).

---

## 7. Probar la API

- **Swagger:** en entorno Development, abrir en el navegador la URL que indique la consola más la ruta `/swagger` (por ejemplo `https://localhost:7xxx/swagger`). Desde ahí se pueden probar todos los endpoints.
- **Login:** llamar a `POST /api/Auth/login` con un usuario del DML, por ejemplo:
  - Body: `{ "email": "juan@correo.com", "contraseña": "clave123" }`
  - Respuesta esperada: `{ "token": "...", "usuario": { "id", "nombres", "apellidos", "email", "rol" } }`
- **Llamadas protegidas:** usar en las peticiones el header `Authorization: Bearer <token>` con el token devuelto en el login.

Detalle de endpoints: [06_API_Endpoints](06_API_Endpoints.md).

---

## 8. Resumen rápido

| Paso | Acción |
|------|--------|
| 1 | Tener .NET 9 y SQL Server. |
| 2 | Abrir/clonar el proyecto (raíz con `SkilledGuard.sln`). |
| 3 | Ejecutar DDL y DML en SQL Server para crear `auditoria_sistema`. |
| 4 | Configurar `appsettings.json` (cadena de conexión y JWT). |
| 5 | `dotnet restore` y `dotnet build` en la raíz. |
| 6 | `dotnet run --project CodigoBackend/Auditorias/Auditorias.csproj` o F5 en Visual Studio. |
| 7 | Probar con Swagger (`/swagger`) y login. |

---

## Referencias

- [README principal](../README.md) – Requisitos previos, paso a paso, configuración y uso de la API (documento de referencia completo)
- [07_Base_de_Datos_Resumen](07_Base_de_Datos_Resumen.md) – Scripts y orden de ejecución
- [06_API_Endpoints](06_API_Endpoints.md) – Listado de endpoints
- [04_Arquitectura_Sistema](04_Arquitectura_Sistema.md) – Arquitectura y flujo JWT
