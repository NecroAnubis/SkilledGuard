# 09 – Configuración por entornos

**Proyecto:** SkilledGuard  
**Documento:** Configuración según entorno (desarrollo y producción)  
**Referencia:** `Program.cs`, `appsettings.json`, `appsettings.Development.json` y [README principal](../README.md).

---

## 1. Entornos soportados

ASP.NET Core utiliza la variable de entorno **`ASPNETCORE_ENVIRONMENT`** para determinar el entorno:

| Valor | Uso típico |
|-------|------------|
| **Development** | Desarrollo local. Swagger activo, logging más detallado. |
| **Production** | Despliegue en servidor. Swagger desactivado; usar secretos y configuración segura. |
| **Staging** | Pruebas preproducción (opcional). |

Por defecto, al ejecutar con `dotnet run` o desde Visual Studio suele estar en **Development** (por `launchSettings.json` o el valor por defecto). En el servidor suele fijarse `ASPNETCORE_ENVIRONMENT=Production`.

---

## 2. Archivos de configuración

| Archivo | Cuándo se carga |
|---------|------------------|
| **appsettings.json** | Siempre (configuración base). |
| **appsettings.{Environment}.json** | Según el valor de `ASPNETCORE_ENVIRONMENT` (p. ej. `appsettings.Development.json` en Development). Las claves de este archivo sobrescriben las de `appsettings.json`. |

Las **variables de entorno** y los **argumentos de línea de comandos** tienen prioridad sobre los archivos JSON (útil para producción sin tocar archivos).

---

## 3. Cadena de conexión

- **Clave:** `ConnectionStrings:AuditoriaConnection`
- **Dónde se define:** `CodigoBackend/Auditorias/appsettings.json` (o en el archivo del entorno correspondiente).
- **Uso en código:** `builder.Configuration.GetConnectionString("AuditoriaConnection")` en `Program.cs`.

**Desarrollo:** puede estar en `appsettings.Development.json` o en `appsettings.json` (evitar subir credenciales reales si el repositorio es público).

**Producción (recomendado):**
- Definir la cadena como **variable de entorno** (p. ej. `ConnectionStrings__AuditoriaConnection`; en .NET el doble guion bajo `__` equivale a `:` en la jerarquía de configuración).
- O usar **User Secrets** (desarrollo) / **Azure Key Vault**, **gestor de secretos del servidor**, etc., y no incluir la cadena completa en archivos versionados.

---

## 4. JWT (clave e emisor)

- **Claves:** `Jwt:Key` (clave secreta para firmar el token), `Jwt:Issuer` (emisor del token).
- **Dónde se definen:** en `appsettings.json` o en el archivo del entorno. En `Program.cs` se leen con valor por defecto si no existen:
  - `Jwt:Key`: por defecto una clave de ejemplo (solo válida para desarrollo).
  - `Jwt:Issuer`: por defecto `"IssuerPorDefecto"`.

**Producción (recomendado):**
- **No** dejar la clave JWT en `appsettings.json` versionado.
- Usar **variables de entorno**, por ejemplo:
  - `Jwt__Key` = clave larga y aleatoria.
  - `Jwt__Issuer` = nombre del emisor (p. ej. el dominio de la API).
- O inyectar la configuración desde un gestor de secretos (Key Vault, variables del host, etc.).

---

## 5. Swagger

- **Comportamiento:** en `Program.cs`, Swagger y SwaggerUI solo se registran cuando `app.Environment.IsDevelopment()` es verdadero.
- **Desarrollo:** al ejecutar en entorno Development, la documentación está disponible en la ruta `/swagger` (p. ej. `https://localhost:7xxx/swagger`).
- **Producción:** Swagger no se activa; no se expone la documentación ni los endpoints de prueba. No es necesario cambiar nada si el entorno está bien fijado a `Production`.

---

## 6. Logging

- **Configuración:** en `appsettings.json` y `appsettings.Development.json` bajo `Logging:LogLevel`.
- **Ejemplo en el proyecto:** `Default: Information`, `Microsoft.AspNetCore: Warning`.
- **Producción:** se puede restringir a `Warning` o `Error` para reducir ruido y coste; en desarrollo suele usarse `Information` o `Debug` para depurar.

Estructura típica:

```json
"Logging": {
  "LogLevel": {
    "Default": "Information",
    "Microsoft.AspNetCore": "Warning"
  }
}
```

---

## 7. CORS

En el estado actual del proyecto **no se ha configurado middleware CORS** en `Program.cs`. Eso implica:

- Las peticiones desde el mismo origen (misma URL que la API) funcionan sin problema.
- Si un **frontend** se sirve desde otro origen (otro puerto o dominio), el navegador puede bloquear las peticiones por política CORS.

**Cuando exista frontend en otro origen:** habrá que añadir en `Program.cs` algo como:

- `builder.Services.AddCors(...)` con una política que permita el origen del frontend.
- `app.UseCors(...)` en el pipeline (antes de `UseAuthentication`/`UseAuthorization` según documentación de ASP.NET Core).

En producción, restringir los orígenes permitidos a los dominios conocidos (no usar `*` si se exponen datos sensibles).

---

## 8. AllowedHosts

- **Clave:** `AllowedHosts`
- En el proyecto puede estar en `appsettings.json` con valor `"*"` (acepta cualquier host). Adecuado para desarrollo.
- **Producción:** se recomienda limitar a los dominios/hosts de la API (p. ej. `"AllowedHosts": "miapi.ejemplo.com"` o una lista de hosts permitidos).

---

## 9. Resumen por entorno

| Aspecto | Development | Production |
|---------|-------------|------------|
| **ASPNETCORE_ENVIRONMENT** | Development | Production |
| **Swagger** | Activo (`/swagger`) | Inactivo |
| **Cadena de conexión** | appsettings o User Secrets | Preferible variable de entorno o gestor de secretos |
| **JWT Key / Issuer** | appsettings o valores por defecto | Variable de entorno o gestor de secretos; clave fuerte y no versionada |
| **Logging** | Information / Debug | Warning / Error según necesidad |
| **CORS** | Configurar si el frontend está en otro origen | Configurar solo orígenes permitidos |
| **AllowedHosts** | `*` aceptable | Limitar a hosts conocidos |

---

## Referencias

- [README principal](../README.md) – Configuración y recomendaciones de seguridad
- [08_Guia_Desarrollo](08_Guia_Desarrollo.md) – Configuración inicial para desarrollo
- [03_Requisitos_No_Funcionales](03_Requisitos_No_Funcionales.md) – RNF de seguridad y configuración
- Código: `CodigoBackend/Auditorias/Program.cs`, `appsettings.json`, `appsettings.Development.json`
