# Índice y plan de documentación – SkilledGuard

Este documento define **qué archivos o documentos deberían estar en la carpeta Documentación**, teniendo en cuenta lo que ya está construido en el proyecto y lo que falta para que la información quede completa al finalizar el proyecto.

---

## 1. Estado actual del proyecto

### 1.1 Lo que ya existe (fuera de Documentacion)

| Ubicación | Contenido |
|-----------|-----------|
| **Raíz** | `README.md` – Descripción general, arquitectura, tecnologías, configuración, uso de la API, frontend (resumen). |
| **Base_de_Datos/** | `README.txt` – Tablas, relaciones, ER en texto, DDL/DML, permisos. `DDL_base_de_datos.sql`, `DML_base_de_datos.sql`. |
| **CodigoBackend/** | `README.txt` (mínimo: "CodB"). Dependencias en `Dependencias.txt`. Swagger en ejecución para la API. |
| **CodigoForntend/** | `README.txt` (mínimo: "Cod Frontend"). Carpeta prevista, sin implementación. |
| **Documentacion/** | Vacía. |

### 1.2 Lo que falta (documentación recomendada)

- Documentos centralizados en **Documentacion/** que complementen el README principal y den una visión única para el cierre del proyecto.
- Documentación de diseño, requisitos, despliegue, pruebas y manuales de usuario/operación.

---

## 2. Documentos que deberían ir en la carpeta Documentacion

A continuación se listan los documentos recomendados, si ya existen en otra parte se indica **“Referencia / resumen”**; si no existen, **“Por crear”**.

---

### 2.1 Visión y alcance

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **01_Vision_y_Alcance.md** | Objetivos del sistema, usuarios objetivo, alcance funcional (qué hace y qué no hace SkilledGuard), criterios de éxito. | Por crear |

*Nota: Partes de esto están en el README principal; aquí se puede ampliar y dejar como referencia oficial.*

---

### 2.2 Requisitos

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **02_Requisitos_Funcionales.md** | Listado de requisitos funcionales (usuarios, roles, dispositivos, auditoría de negocio, reportes, logs) con prioridad y estado (implementado / pendiente). | Por crear |
| **03_Requisitos_No_Funcionales.md** | Seguridad (JWT, contraseñas), rendimiento, disponibilidad, escalabilidad, compatibilidad (navegadores, .NET 9, SQL Server). | Por crear |

*Incluir qué está cubierto por el backend actual y qué queda para el frontend.*

---

### 2.3 Diseño y arquitectura

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **04_Arquitectura_Sistema.md** | Diagrama o descripción de capas (cliente → API → BD), flujo de autenticación JWT, componentes principales. Puede resumir o enlazar el README. | Por crear (resumen/enlace) |
| **05_Modelo_de_Datos.md** | Descripción de entidades y relaciones. Puede ser un resumen que enlace a `Base_de_Datos/README.txt` y a los scripts DDL/DML, más un diagrama ER (imagen o Mermaid) si se genera. | Por crear (resumen + opcional diagrama) |
| **06_API_Endpoints.md** | Listado de endpoints por recurso (Auth, Usuario, Rol, TipoDocumento, Dispositivo, Auditoría, Reportes, Sedes, etc.) con método, ruta, cuerpo y respuestas típicas. Referencia a Swagger como fuente de verdad. | Por crear (índice desde Swagger) |

*El README ya describe controladores y login; este documento puede ser la “tabla de contenidos” de la API para la carpeta Documentacion.*

---

### 2.4 Base de datos

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **07_Base_de_Datos_Resumen.md** | Resumen: nombre de la BD, scripts (DDL/DML), orden de ejecución, enlace a `Base_de_Datos/README.txt` y a los archivos SQL. | Por crear (resumen/enlace) |

*Evita duplicar todo el detalle que ya está en Base_de_Datos/README.txt.*

---

### 2.5 Desarrollo y configuración

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **08_Guia_Desarrollo.md** | Requisitos previos (.NET 9, SQL Server, IDE), clonado, restauración, build, ejecución del backend, configuración (appsettings, JWT), ejecución de Swagger. Puede resumir el README y enlazarlo. | Por crear (resumen/enlace) |
| **09_Configuracion_Entornos.md** | Desarrollo vs producción: cadenas de conexión, JWT (variables de entorno o secretos), CORS, logging, Swagger (solo desarrollo). | Por crear |

---

### 2.6 Frontend (cuando exista)

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **10_Frontend_Especificacion.md** | Stack elegido (React/Angular/Vue, etc.), estructura de carpetas, convenciones, integración con la API (URL base, JWT en headers). | Por crear cuando se implemente el frontend |
| **11_Frontend_Guia_Instalacion.md** | Instalación de dependencias (npm/yarn), variables de entorno, script de ejecución, build de producción. | Por crear cuando se implemente el frontend |

*El README principal ya sugiere documentar el frontend en README o en CodigoForntend; estos archivos pueden vivir en Documentacion como vista consolidada.*

---

### 2.7 Pruebas y calidad

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **12_Pruebas.md** | Estrategia de pruebas: unitarias (backend), integración (API + BD), pruebas E2E (si aplica), datos de prueba (usuarios del DML). Casos clave (login, CRUD usuarios, etc.). | Por crear |

---

### 2.8 Despliegue y operación

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **13_Despliegue.md** | Pasos para desplegar backend (IIS, Kestrel, contenedor, etc.), base de datos (ejecución de DDL/DML en el servidor), variables de entorno, HTTPS, recomendaciones de seguridad. | Por crear |
| **14_Operacion_y_Mantenimiento.md** | Logs, monitoreo, backups de BD, actualización de dependencias, qué hacer ante fallos frecuentes. | Por crear (opcional pero recomendado) |

---

### 2.9 Usuario final y administración

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **15_Manual_Usuario.md** | Cómo usar la aplicación (cuando el frontend exista): login, pantallas principales, gestión de usuarios/dispositivos/auditorías/reportes. | Por crear con el frontend |
| **16_Manual_Administrador.md** | Roles, permisos, gestión de sedes y catálogos, generación de reportes, revisión de logs. | Por crear con el frontend |

---

### 2.10 Cierre del proyecto y referencias

| Documento | Propósito | Estado |
|-----------|-----------|--------|
| **17_Glosario.md** | Términos: auditoría de negocio, tipo de registro, sede, tipo de reporte, JWT, etc. | Por crear (opcional) |
| **18_Changelog_o_Historial.md** | Versiones, fechas y cambios relevantes (funcionalidades, correcciones, dependencias). | Por crear (opcional) |

---

## 3. Resumen: qué poner en Documentacion

### Mínimo recomendado (para que la documentación esté “completa” al finalizar)

1. **01_Vision_y_Alcance.md** – Visión y alcance.
2. **02_Requisitos_Funcionales.md** – Requisitos funcionales.
3. **03_Requisitos_No_Funcionales.md** – Requisitos no funcionales.
4. **04_Arquitectura_Sistema.md** – Arquitectura (resumen/enlace al README).
5. **05_Modelo_de_Datos.md** – Modelo de datos (resumen + enlace a Base_de_Datos).
6. **06_API_Endpoints.md** – Índice de endpoints (referencia a Swagger).
7. **07_Base_de_Datos_Resumen.md** – Resumen de BD y scripts.
8. **08_Guia_Desarrollo.md** – Guía de desarrollo (resumen/enlace al README).
9. **09_Configuracion_Entornos.md** – Configuración por entorno.
10. **12_Pruebas.md** – Estrategia de pruebas.
11. **13_Despliegue.md** – Despliegue.

### Cuando exista frontend

12. **10_Frontend_Especificacion.md**  
13. **11_Frontend_Guia_Instalacion.md**  
14. **15_Manual_Usuario.md**  
15. **16_Manual_Administrador.md**

### Opcionales

- **14_Operacion_y_Mantenimiento.md**  
- **17_Glosario.md**  
- **18_Changelog_o_Historial.md**

---

## 4. Relación con el resto del proyecto

- **README.md (raíz)**: Sigue siendo el punto de entrada; puede incluir al final un enlace a `Documentacion/INDICE_DOCUMENTACION.md` para quien quiera toda la documentación.
- **Base_de_Datos/README.txt**: Se mantiene; en Documentacion solo se resume y se enlaza.
- **CodigoBackend / CodigoForntend**: Sus README pueden seguir siendo breves; el detalle técnico puede vivir en Documentacion (guías, API, configuración).

Con esto, la carpeta **Documentacion** queda definida como el lugar donde se consolida la información del proyecto para tenerla completa al finalizar.
