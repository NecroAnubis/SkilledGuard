# Ficha técnica del proyecto

---

## Identificación

| Campo | Valor |
|---|---|
| **Nombre** | Skilled Guard |
| **Descripción** | Sistema de automatización para el control de ingreso de equipos tecnológicos |
| **Autor** | Johan S. Restrepo |
| **Programa** | Tecnólogo en Análisis y Desarrollo de Software (ADSO) |
| **Institución** | SENA |
| **Repositorio** | https://github.com/NecroAnubis/SkilledGuard |
| **Versión** | 0.3.0 |
| **Licencia** | Proyecto académico |

## Problema que resuelve

Reemplaza el registro manual en minuta del ingreso y salida de equipos tecnológicos, que hoy toma ~10 minutos por persona, no deja trazabilidad consultable y no permite verificar que el equipo que sale sea el mismo que entró.

## Arquitectura

| Aspecto | Definición |
|---|---|
| **Tipo** | API REST |
| **Patrón** | Capas: Routers → Reglas de negocio → ORM → Base de datos |
| **Estilo de datos** | Relacional, normalizado |
| **Autenticación** | JWT (Bearer token) con autorización por rol |
| **Despliegue** | Contenedores Docker orquestados con docker-compose |

Las reglas de negocio viven en un módulo propio (`app/porteria.py`), separado de los endpoints, de modo que puedan probarse y reutilizarse sin depender de la capa HTTP.

## Tecnologías

### Producción

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.12 |
| Framework web | FastAPI | 0.115.6 |
| Servidor | Uvicorn | 0.34.0 |
| ORM | SQLAlchemy | 2.0.36 |
| Migraciones | Alembic | 1.14.0 |
| Base de datos | PostgreSQL | 16 |
| Controlador de BD | psycopg | 3.2.3 |
| Validación | Pydantic | 2.10.4 |
| Tokens | PyJWT | 2.10.1 |
| Hash de contraseñas | bcrypt | 4.2.1 |
| Códigos QR | qrcode | 8.0 |
| Reportes Excel | openpyxl | 3.1.5 |
| Reportes PDF | fpdf2 | 2.8.2 |

### Desarrollo

| Componente | Tecnología | Versión |
|---|---|---|
| Pruebas | pytest | 8.3.4 |
| Cliente HTTP de pruebas | httpx | 0.28.1 |
| Análisis estático y formato | ruff | 0.8.6 |
| Contenedores | Docker + docker-compose | — |
| Integración continua | GitHub Actions | — |
| Control de versiones | Git / GitHub | — |

## Métricas del proyecto

| Métrica | Valor |
|---|---|
| Líneas de código de aplicación | 1.589 |
| Líneas de código de pruebas | 939 |
| Relación pruebas / código | 0,59 |
| Endpoints expuestos | 21 |
| Entidades del modelo de datos | 15 |
| Migraciones versionadas | 4 |
| Casos de prueba automatizados | 70 |
| Dependencias directas | 13 |
| Commits | 25 |

## Módulos

| Módulo | Responsabilidad |
|---|---|
| `app/main.py` | Configuración de la aplicación y registro de rutas |
| `app/config.py` | Configuración por variables de entorno |
| `app/database.py` | Motor y sesión de base de datos |
| `app/models.py` | Modelo de datos (15 entidades) |
| `app/schemas.py` | Validación de entradas y salidas |
| `app/security.py` | Hash de contraseñas, emisión y verificación de JWT, control de roles |
| `app/porteria.py` | **Reglas de negocio del control de ingreso** |
| `app/auditoria.py` | Registro de acciones sobre los datos |
| `app/consultas.py` | Construcción de consultas compartida por API y reportes |
| `app/reportes.py` | Generación de Excel y PDF |
| `app/qr.py` | Generación de códigos QR |
| `app/seed.py` | Datos iniciales del sistema |
| `app/routers/` | Endpoints agrupados por área |

## Modelo de datos

15 entidades organizadas en cuatro grupos:

| Grupo | Entidades |
|---|---|
| **Catálogos** | `tipo_documento`, `rol`, `tipo_dispositivo`, `tipo_accion`, `objeto_afectado`, `tipo_registro`, `tipo_reporte` |
| **Usuarios** | `usuario`, `usuario_rol` |
| **Equipos** | `dispositivo` |
| **Auditoría y reportes** | `auditoria_negocio`, `log_sistema`, `log_detalle`, `reporte`, `consulta_reporte` |

## Requisitos de operación

### Para ejecutar

| Requisito | Detalle |
|---|---|
| Software | Docker y docker-compose |
| Memoria | 2 GB disponibles |
| Puertos | 8000 (API) y 5432 (base de datos) |
| Conectividad | No requiere internet en modo local |

### Para desarrollar

Python 3.12, además de lo anterior.

## Metodología

| Aspecto | Definición |
|---|---|
| Marco de trabajo | Scrum adaptado a un solo desarrollador |
| Duración del sprint | 2 semanas |
| Número de sprints | 4 |
| Tablero | GitHub Projects |
| Control de cambios | Pull Request con revisión previa a integrar |

### Definition of Done

Una historia se considera terminada solo si:

1. El código entra por Pull Request, nunca por push directo
2. Tiene pruebas automatizadas
3. La integración continua está en verde
4. El endpoint aparece documentado en Swagger
5. Los cambios de esquema tienen su migración versionada

## Estado por sprint

| Sprint | Entregable | Estado |
|---|---|---|
| 1 | Fundación: API, modelo de datos, autenticación, Docker, CI | ✅ |
| 2 | Control de ingreso: equipos, códigos QR, validación en portería | ✅ |
| 3 | Auditoría, reportes descargables y optimización | ✅ |
| 4 | Documentación, diagramas UML y despliegue en la nube | 🔄 |

## Puntos de acceso

| Recurso | Ruta |
|---|---|
| Documentación interactiva de la API | `/docs` |
| Documentación alterna | `/redoc` |
| Estado del servicio | `/salud` |
| Esquema OpenAPI | `/openapi.json` |
