# 13 – Despliegue

**Proyecto:** SkilledGuard  
**Documento:** Guía de despliegue del backend, base de datos y consideraciones de producción  
**Referencia:** [08_Guia_Desarrollo](08_Guia_Desarrollo.md), [09_Configuracion_Entornos](09_Configuracion_Entornos.md), [07_Base_de_Datos_Resumen](07_Base_de_Datos_Resumen.md).

---

## 1. Resumen

Este documento describe los pasos para llevar SkilledGuard a un entorno de **producción** (o staging): publicación del backend, preparación de la base de datos, configuración en el servidor y recomendaciones de seguridad. No existe en el proyecto configuración de contenedores (Docker) ni scripts de despliegue automatizado; lo que sigue son pasos manuales y opciones de hospedaje.

---

## 2. Requisitos del servidor

| Requisito | Descripción |
|-----------|-------------|
| **.NET 9 Runtime** | Para ejecutar la API publicada. Instalar el runtime adecuado al sistema operativo (Windows/Linux). |
| **SQL Server** | Instancia accesible desde el servidor (misma máquina o remota). |
| **HTTPS** | Certificado para servir la API por HTTPS (recomendado en producción). |
| **Firewall / puertos** | Permitir el puerto donde escuchará la API (p. ej. 443 si hay inversor de proxy, o el puerto configurado para Kestrel). |

---

## 3. Base de datos en el servidor

1. **Conectar** a la instancia de SQL Server del entorno de producción (o staging).
2. **Ejecutar en orden** los scripts de la carpeta `Base_de_Datos/`:
   - `DDL_base_de_datos.sql` — crea la base de datos `auditoria_sistema` y las tablas.
   - `DML_base_de_datos.sql` — opcional en producción: inserta catálogos y, si se desea, datos iniciales (en producción a veces solo se ejecuta DDL y los datos se cargan por la aplicación o por un proceso controlado).
3. **Usuario de la aplicación:** según [Base_de_Datos/README.txt](../Base_de_Datos/README.txt), crear un login con permisos limitados (por ejemplo `db_datareader`, `db_datawriter`) sobre `auditoria_sistema`, sin rol sysadmin. No usar `sa` para la aplicación.
4. **Cadena de conexión:** usar en la configuración del backend el servidor, nombre de BD (`auditoria_sistema`), usuario y contraseña de ese login (o autenticación integrada si aplica).

Ver [07_Base_de_Datos_Resumen](07_Base_de_Datos_Resumen.md) para detalles de scripts y [09_Configuracion_Entornos](09_Configuracion_Entornos.md) para no dejar la cadena en archivos versionados.

---

## 4. Publicar el backend

Desde la raíz del repositorio (o desde la carpeta de la solución):

```bash
dotnet publish CodigoBackend/Auditorias/Auditorias.csproj -c Release -o ./publish
```

Se genera la carpeta `publish/` con la aplicación y sus dependencias. Esa carpeta es la que se copia al servidor o se usa para construir una imagen de contenedor.

**Otras opciones:**
- Publicar para un runtime concreto: `-r win-x64` o `-r linux-x64` (self-contained).
- Publicar como dependiente del framework (solo el proyecto, requiere .NET instalado en el servidor): no usar `-r` (es el comportamiento por defecto sin `--self-contained`).

---

## 5. Configuración en producción

**No** depender de `appsettings.json` con secretos en el servidor. Usar **variables de entorno** (o un gestor de secretos) para:

| Variable (ejemplo) | Descripción |
|--------------------|-------------|
| `ASPNETCORE_ENVIRONMENT` | `Production` (para desactivar Swagger y usar configuración de producción). |
| `ConnectionStrings__AuditoriaConnection` | Cadena de conexión a SQL Server (servidor, base de datos, usuario y contraseña de la aplicación). |
| `Jwt__Key` | Clave secreta para firmar el token JWT (larga y aleatoria). |
| `Jwt__Issuer` | Emisor del token (p. ej. nombre o URL de la API). |

En .NET, el doble guion bajo `__` en nombres de variables de entorno equivale a `:` en la jerarquía de configuración (ej. `Jwt__Key` → `Jwt:Key`).

**URLs y puertos:** por defecto Kestrel escucha en un puerto definido en la configuración o en la variable `ASPNETCORE_URLS` (ej. `http://localhost:5000`). En producción suele ponerse detrás de un reverso proxy (IIS, Nginx, etc.) que termina HTTPS y reenvía a Kestrel.

---

## 6. Opciones de hospedaje del backend

### 6.1 Kestrel (proceso directo)

Copiar la carpeta publicada al servidor y ejecutar:

```bash
cd publish
dotnet Auditorias.dll
```

O configurar un servicio (systemd en Linux, Windows Service) para que ejecute `dotnet Auditorias.dll` desde la carpeta de publicación, con las variables de entorno definidas para el servicio.

### 6.2 IIS (Windows)

1. Instalar el **módulo ASP.NET Core Hosting Bundle** (o el runtime .NET) en el servidor.
2. Crear un **sitio** o **aplicación** en IIS que apunte a la carpeta publicada.
3. Configurar el **Application Pool** para “No Managed Code” y que arranque el proceso de la aplicación.
4. Definir las variables de entorno en el Application Pool o en `web.config` (sin incluir contraseñas en archivos versionados; usar variables del sistema o de IIS si está disponible).
5. Opcional: usar IIS como reverso proxy con enlace HTTPS y reenvío al proceso Kestrel.

### 6.3 Contenedor (Docker)

El proyecto **no incluye actualmente** un `Dockerfile`. Si se desea desplegar en contenedor:

1. Añadir un `Dockerfile` en la raíz o en `CodigoBackend/Auditorias/` que haga `dotnet publish` y ejecute la aplicación.
2. Pasar la cadena de conexión y JWT mediante variables de entorno del contenedor (o un volumen/gestor de secretos).
3. La base de datos puede estar en otro contenedor o en un SQL Server externo; asegurar conectividad de red.

---

## 7. HTTPS y seguridad

| Aspecto | Recomendación |
|---------|----------------|
| **HTTPS** | La API ya usa `UseHttpsRedirection()`. En producción, servir la aplicación detrás de un terminador SSL (IIS, Nginx, balanceador) o configurar el certificado en Kestrel. |
| **Clave JWT** | Generar una clave larga y aleatoria; no usar la de desarrollo. No versionar la clave. |
| **Cadena de conexión** | No subirla al repositorio; usar variables de entorno o gestor de secretos en el servidor. |
| **Swagger** | En `Production` no se activa (condición `IsDevelopment()` en `Program.cs`). No es necesario cambiar código. |
| **AllowedHosts** | En producción limitar a los dominios/hosts de la API (ver [09_Configuracion_Entornos](09_Configuracion_Entornos.md)). |
| **CORS** | Si hay frontend en otro dominio, configurar CORS en el backend permitiendo solo los orígenes necesarios. |

---

## 8. Frontend (cuando exista)

Cuando la carpeta **CodigoForntend** tenga una aplicación:

1. **Build de producción:** ejecutar el comando de build del frontend (ej. `npm run build`) según [11_Frontend_Guia_Instalacion](11_Frontend_Guia_Instalacion.md).
2. **Desplegar la salida:** la carpeta generada (`dist/`, `build/`, etc.) se sirve con un servidor web estático (Nginx, IIS, CDN) o desde el mismo dominio que la API.
3. **URL de la API:** configurar en el frontend la URL base de la API de producción (variable de entorno en el build o archivo de configuración).

---

## 9. Checklist de despliegue

| Paso | Acción |
|------|--------|
| 1 | Servidor con .NET 9 Runtime y SQL Server accesible. |
| 2 | Ejecutar DDL (y DML si aplica) en la instancia de BD; crear usuario de aplicación con permisos limitados. |
| 3 | `dotnet publish` del proyecto Auditorias en Release. |
| 4 | Copiar la carpeta publicada al servidor (o construir imagen de contenedor). |
| 5 | Definir variables de entorno: `ASPNETCORE_ENVIRONMENT=Production`, cadena de conexión, `Jwt:Key`, `Jwt:Issuer`. |
| 6 | Configurar HTTPS y puertos (Kestrel directo, IIS o proxy inverso). |
| 7 | Arrancar la aplicación (proceso, servicio o contenedor) y comprobar que responde (p. ej. login desde un cliente). |
| 8 | (Opcional) Desplegar frontend y configurar su URL de API. |

---

## Referencias

- [08_Guia_Desarrollo](08_Guia_Desarrollo.md) – Configuración y ejecución en desarrollo
- [09_Configuracion_Entornos](09_Configuracion_Entornos.md) – Variables de entorno y producción
- [07_Base_de_Datos_Resumen](07_Base_de_Datos_Resumen.md) – Scripts y conexión
- [Base_de_Datos/README.txt](../Base_de_Datos/README.txt) – Permisos y seguridad en BD
- [03_Requisitos_No_Funcionales](03_Requisitos_No_Funcionales.md) – Seguridad (RNF)
