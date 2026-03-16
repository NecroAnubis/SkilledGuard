# 03 – Requisitos no funcionales

**Proyecto:** SkilledGuard  
**Documento:** Requisitos no funcionales  
**Referencia:** Extraídos de `Program.cs`, `PasswordHelper`, README, Base de datos y convenciones del proyecto.

---

## Convenciones

| Estado           | Significado |
|------------------|-------------|
| **Implementado** | Cubierto por la implementación actual. |
| **Recomendado**  | No obligatorio en el código; buena práctica documentada (ej. producción). |
| **Pendiente**    | No implementado o fuera del alcance actual. |

---

## 1. Seguridad

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF01 | Las contraseñas no deben almacenarse en texto plano. | Implementado | `PasswordHelper`: PBKDF2 con SHA-256, 100.000 iteraciones y salt aleatorio de 16 bytes; hash en Base64. |
| RNF02 | El sistema debe autenticar las peticiones mediante JWT (Bearer). | Implementado | `Program.cs`: esquema JwtBearer; validación de emisor, firma y vigencia. |
| RNF03 | El token JWT debe validar emisor (Issuer), firma (SigningKey) y tiempo de vida. | Implementado | `TokenValidationParameters`: ValidateIssuer, ValidateLifetime, ValidateIssuerSigningKey; clave e issuer desde configuración. |
| RNF04 | Los endpoints sensibles deben exigir autenticación; el login debe ser accesible sin token. | Implementado | `[Authorize]` por defecto; `[AllowAnonymous]` en `POST /api/Auth/login`. |
| RNF05 | La comunicación cliente–servidor debe usar HTTPS en producción. | Implementado | `app.UseHttpsRedirection()` en el pipeline. |
| RNF06 | La clave JWT y los secretos no deben estar en el código ni versionados en producción. | Recomendado | README y Base_de_Datos: usar variables de entorno o gestor de secretos para `Jwt:Key` y cadena de conexión. |
| RNF07 | El acceso a la base de datos en producción debe usar un usuario con permisos limitados. | Recomendado | Base_de_Datos/README: usuario de aplicación con db_datareader/db_datawriter, sin sysadmin; no usar sa. |

---

## 2. Rendimiento

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF08 | Las operaciones de acceso a datos deben ser asíncronas cuando sea posible. | Implementado | Varios controladores usan `async`/`await` y `ToListAsync()`, `FindAsync()` (EF Core). |
| RNF09 | La conexión a la base de datos debe ser gestionada por un pool. | Implementado | Entity Framework Core con SQL Server utiliza pooling de conexiones por defecto. |
| RNF10 | Cargas y tiempos de respuesta máximos (SLA) definidos. | Pendiente | No hay umbrales documentados; se pueden definir en operación según necesidad. |

---

## 3. Disponibilidad y resiliencia

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF11 | La API debe poder ejecutarse de forma continua (proceso o servicio). | Implementado | Aplicación ASP.NET Core estándar; en producción se puede hospedar en IIS, Kestrel o contenedor. |
| RNF12 | Alta disponibilidad (varios nodos, balanceador). | Pendiente | No implementado; depende del entorno de despliegue (ver documento de Despliegue cuando exista). |

---

## 4. Escalabilidad

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF13 | La autenticación no debe depender de estado en el servidor (sesiones en memoria). | Implementado | JWT stateless; el servidor no almacena sesiones; se puede escalar horizontalmente añadiendo instancias. |
| RNF14 | Escalado horizontal (múltiples instancias de la API). | Implementado | Diseño stateless permite varias réplicas detrás de un balanceador; BD como único estado compartido. |

---

## 5. Compatibilidad y dependencias

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF15 | El backend debe ejecutarse sobre .NET 9. | Implementado | `Auditorias.csproj`: `<TargetFramework>net9.0</TargetFramework>`. |
| RNF16 | La base de datos debe ser Microsoft SQL Server (compatible T-SQL). | Implementado | Scripts DDL/DML en T-SQL; EF Core con proveedor SqlServer. |
| RNF17 | La API debe ser consumible por clientes HTTP (navegador, móvil, otros servicios). | Implementado | API REST; respuestas JSON; CORS no restringido en el código actual (AllowedHosts/configuración según entorno). |
| RNF18 | Compatibilidad con navegadores modernos (frontend). | Pendiente | Aplicable cuando exista la interfaz en CodigoForntend; dependerá del stack elegido. |

---

## 6. Operabilidad y documentación

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF19 | La API debe exponer documentación interactiva en entorno de desarrollo. | Implementado | Swagger (Swashbuckle) habilitado solo cuando `Environment.IsDevelopment()`. |
| RNF20 | Los secretos y la documentación de despliegue no deben exponerse en Swagger en producción. | Implementado | Swagger no se activa en producción según `Program.cs`. |
| RNF21 | El registro de eventos (logging) debe ser configurable. | Implementado | `appsettings` y `appsettings.Development.json` con niveles de log (ej. Information, Warning para Microsoft.AspNetCore). |

---

## 7. Mantenibilidad y estándares

| Id    | Requisito | Estado | Notas |
|-------|-----------|--------|--------|
| RNF22 | Convención de rutas REST bajo el prefijo `api/[controller]`. | Implementado | Todos los controladores usan `[Route("api/[controller]")]`. |
| RNF23 | Uso de ORM para acceso a datos y consistencia con el modelo relacional. | Implementado | Entity Framework Core 9.x con `AuditoriaContext` y mapeo a tablas existentes. |

---

## Resumen por estado

| Estado        | Cantidad | Observación |
|---------------|----------|-------------|
| **Implementado** | 18     | Cubierto por código o configuración actual. |
| **Recomendado**  | 2      | Producción: secretos y usuario de BD limitado. |
| **Pendiente**    | 4      | SLA (RNF10), alta disponibilidad (RNF12), compatibilidad frontend (RNF18); resto dependiente de despliegue. |

---

## Referencias

- [01_Vision_y_Alcance](01_Vision_y_Alcance.md)
- [02_Requisitos_Funcionales](02_Requisitos_Funcionales.md)
- [README principal](../README.md) – Configuración, metodologías, seguridad
- [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – Permisos y seguridad en BD
- Código: `CodigoBackend/Auditorias/Program.cs`, `utils/PasswordHelper.cs`
