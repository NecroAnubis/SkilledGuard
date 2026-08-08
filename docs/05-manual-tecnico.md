# Manual técnico

**Proyecto:** Skilled Guard
**Dirigido a:** personal técnico encargado de instalar, operar o mantener el sistema

---

## 1. Arquitectura

El sistema es una API REST en cuatro capas. Cada capa solo conoce la siguiente:

```
Cliente (navegador)
      │  HTTP / JSON
      ▼
Routers          app/routers/     ← reciben la petición, validan permisos
      ▼
Reglas           app/porteria.py  ← deciden si la operación es válida
      ▼
ORM              app/models.py    ← traduce objetos a tablas
      ▼
PostgreSQL
```

**Por qué las reglas están separadas.** `app/porteria.py` no importa nada de FastAPI. Eso permite probar la lógica del negocio sin levantar un servidor, y reutilizarla si mañana llega una aplicación móvil o una tarea programada.

## 2. Instalación

### Requisitos

- Docker y docker-compose
- 2 GB de memoria disponibles
- Puertos 8000 y 5432 libres

### Pasos

```bash
git clone https://github.com/NecroAnubis/SkilledGuard.git
cd SkilledGuard
cp .env.example .env
```

Generar el secreto de firma de tokens y escribirlo en `.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

> El sistema **no arranca** sin `JWT_SECRET`. Es deliberado: un valor por defecto en el repositorio permitiría a cualquiera firmar tokens válidos de cualquier usuario.

Levantar el sistema:

```bash
docker compose up --build
```

Cargar los datos iniciales (roles, catálogos y el primer administrador):

```bash
docker compose exec -e ADMIN_CONTRASENA='una-clave-segura' api python -m app.seed
```

### Verificación

```bash
curl http://localhost:8000/salud
# {"estado":"ok","base_de_datos":"ok"}
```

Si responde `503`, la API está viva pero no alcanza la base de datos.

## 3. Configuración

Variables de entorno, en `.env`:

| Variable | Obligatoria | Descripción |
|---|---|---|
| `JWT_SECRET` | **Sí** | Clave con que se firman los tokens. Si cambia, todas las sesiones se invalidan |
| `DATABASE_URL` | No | Cadena de conexión. Por defecto, el Postgres del compose |
| `JWT_EXPIRACION_MINUTOS` | No | Vigencia del token. Por defecto 60 |
| `ADMIN_DOCUMENTO` | No | Documento del primer administrador. Por defecto `1000000000` |
| `ADMIN_CONTRASENA` | Solo para el seed | Contraseña del primer administrador |

`.env` está en `.gitignore` y nunca debe subirse al repositorio.

## 4. Base de datos

### Esquema

15 tablas. El detalle de relaciones está en el [diagrama de clases](04-diagramas-uml.md#2-clases).

### Migraciones

El esquema lo define **Alembic**, no un script SQL suelto. Cada cambio queda versionado en `alembic/versions/`.

| Comando | Efecto |
|---|---|
| `alembic upgrade head` | Aplica todas las migraciones pendientes |
| `alembic downgrade -1` | Revierte la última |
| `alembic current` | Muestra la versión actual del esquema |
| `alembic history` | Lista el historial |
| `alembic revision --autogenerate -m "descripción"` | Genera una migración a partir de los cambios en los modelos |

> **Revisar siempre la migración autogenerada antes de aplicarla.** Alembic las genera con el aviso *"please adjust"* por una razón: deja las restricciones sin nombre (lo que inutiliza el `downgrade`) y no considera las filas existentes al agregar columnas obligatorias. En este proyecto ya ocurrió dos veces.

La API aplica las migraciones automáticamente al arrancar (ver `command` en `docker-compose.yml`), de modo que el esquema nunca queda atrasado respecto al código.

### Migrar a Supabase

1. Crear un proyecto en supabase.com
2. Copiar la cadena de conexión del panel
3. Reemplazar el prefijo `postgresql://` por `postgresql+psycopg://`
4. Ponerla como `DATABASE_URL` en `.env`
5. `alembic upgrade head`

No hay cambios de código.

## 5. Seguridad

| Mecanismo | Implementación |
|---|---|
| Contraseñas | bcrypt con salt aleatorio por contraseña |
| Sesión | JWT firmado con HS256, vigencia configurable |
| Autorización | Por rol, verificado contra la base en cada petición |
| Inyección SQL | Consultas parametrizadas mediante el ORM |
| Concurrencia | Bloqueo de fila (`SELECT … FOR UPDATE`) al registrar movimientos |

**Por qué los roles se consultan en la base y no se leen del token.** El token los lleva, pero el sistema los vuelve a consultar en cada petición. Cuesta una consulta más y a cambio un cambio de rol surte efecto de inmediato, en lugar de esperar a que expire el token de una hora.

**Límite conocido:** no hay restricción de intentos de inicio de sesión. Está identificado y pendiente de implementación.

## 6. Pruebas

```bash
docker compose up -d db
pip install -r requirements-dev.txt
export DATABASE_URL="postgresql+psycopg://skilledguard:skilledguard@localhost:5432/skilledguard_test"
export JWT_SECRET="secreto-de-pruebas"
pytest -q
```

| Archivo | Cubre |
|---|---|
| `test_auth.py` | Autenticación y control de acceso |
| `test_usuarios.py` | Gestión de usuarios y roles |
| `test_catalogos.py` | Catálogos, paginación y estado del servicio |
| `test_porteria.py` | Reglas de negocio, sin levantar la API |
| `test_dispositivos.py` | Equipos, códigos QR y validación en portería |
| `test_auditoria.py` | Rastro de acciones sobre los datos |
| `test_reportes.py` | Reportes y rendimiento de consultas |
| `test_seguridad.py` | Manipulación de tokens, contraseñas y concurrencia |
| `test_seed.py` | Datos iniciales |

Las mismas pruebas corren automáticamente en cada Pull Request (`.github/workflows/ci.yml`).

## 7. Operación

### Comandos frecuentes

| Necesidad | Comando |
|---|---|
| Ver los registros de la API | `docker compose logs -f api` |
| Reiniciar solo la API | `docker compose restart api` |
| Abrir una consola SQL | `docker compose exec db psql -U skilledguard` |
| Detener todo | `docker compose down` |
| Detener y **borrar los datos** | `docker compose down -v` |

> `docker compose down -v` elimina el volumen: se pierden todos los datos. Usarlo solo en desarrollo.

### Respaldo y restauración

```bash
# Respaldo
docker compose exec db pg_dump -U skilledguard skilledguard > respaldo.sql

# Restauración
docker compose exec -T db psql -U skilledguard skilledguard < respaldo.sql
```

## 8. Diagnóstico de problemas

| Síntoma | Causa probable | Solución |
|---|---|---|
| `required variable JWT_SECRET is missing` | Falta el archivo `.env` | `cp .env.example .env` y generar el secreto |
| `/salud` responde 503 | La API no alcanza la base de datos | `docker compose ps` y revisar el contenedor `db` |
| La API reinicia en bucle | Fallan las migraciones al arrancar | `docker compose logs api` |
| `401` en todas las peticiones | Token vencido o `JWT_SECRET` cambiado | Volver a iniciar sesión |
| `403` con un usuario válido | El usuario no tiene el rol requerido | Asignar el rol con `POST /usuarios/{id}/roles` |
| `409` al registrar un movimiento | El movimiento contradice el estado del equipo | Consultar `/dispositivos/{id}/estado` |
| El puerto 8000 está ocupado | Otro proceso lo usa | Cambiar el mapeo en `docker-compose.yml` |

## 9. Mantenimiento

### Agregar un endpoint

1. Definir los esquemas de entrada y salida en `app/schemas.py`
2. Crear la función en el router correspondiente de `app/routers/`
3. Si modifica datos, registrar la acción con `registrar_accion`
4. Escribir la prueba en `tests/`
5. Verificar que aparezca en `/docs`

### Cambiar el modelo de datos

1. Modificar `app/models.py`
2. Generar la migración: `alembic revision --autogenerate -m "descripción"`
3. **Revisar el archivo generado**: nombrar las restricciones y considerar las filas existentes
4. Probar el ciclo completo: `alembic upgrade head && alembic downgrade -1 && alembic upgrade head`
5. Probar la migración contra una base **con datos**, no solo vacía

### Estándar de código

```bash
ruff check .          # análisis estático
ruff format .         # formato
```

Ambos se verifican en integración continua; un Pull Request con hallazgos no pasa.
