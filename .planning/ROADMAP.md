# Roadmap: Skilled Guard — Entrega y sustentación

## Overview

El sistema ya está construido (sprints 1–5, mergeados en `develop`). Este roadmap
no agrega funcionalidad: es una cadena de dependencias de infraestructura y
entrega que convierte un proyecto que corre en `docker-compose` local en un
proyecto desplegado, documentado con honestidad y ensayado para sustentarse.
El orden sigue la cadena real de dependencias, no un calendario: primero el
código queda listo para cualquier PaaS (sin tocar ninguna cuenta externa),
luego se aísla el riesgo de conectividad de la base de datos gestionada antes
de sumar la variable del hosting, después se resuelve la higiene pública del
repositorio junto con el primer despliegue, se verifica técnicamente ese
despliegue con un celular real, se puebla y documenta con honestidad, y solo
al final —cuando todo lo anterior ya es cierto a la vez— se ensaya la demo
completa con su plan de respaldo.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Preparación del código para desplegar** - El contenedor queda listo para correr en un PaaS y el residuo de la ruta HTTPS descartada desaparece del repositorio
- [ ] **Phase 2: Base de datos gestionada y bloqueo de login** - Un Postgres alcanzable por IPv4 queda provisionado, y el bloqueo de intentos fallidos se prueba contra él y se mergea
- [ ] **Phase 3: Higiene del repositorio y aprovisionamiento de Render** - La rama por defecto, el historial de secretos y el servicio en Render quedan resueltos antes de que alguien visite el proyecto
- [ ] **Phase 4: Verificación técnica del despliegue en producción** - El sistema desplegado se mantiene disponible, su arranque en frío está medido, y el escáner QR funciona desde celulares reales
- [ ] **Phase 5: Contenido de demo y documentación honesta** - La base desplegada tiene datos reales que mostrar y `docs/`/README describen el sistema tal como está, no como se planeó
- [ ] **Phase 6: Ensayo de la demo y plan de respaldo** - La sustentación corre de principio a fin, con calentamiento y una alternativa lista si falla la red del aula

## Phase Details

### Phase 1: Preparación del código para desplegar
**Goal**: El contenedor lee la configuración que le da cualquier PaaS en vez de valores fijos pensados para desarrollo local, arranca sin intervención manual, y no queda configuración muerta de la ruta HTTPS que se descartó (Caddy).
**Depends on**: Nothing (first phase)
**Requirements**: DEPLOY-03, DEPLOY-04, DEPLOY-05, CODE-02
**Success Criteria** (what must be TRUE):
  1. El comando de arranque del contenedor usa `$PORT` del entorno en vez de un puerto fijo — verificable leyendo el `Dockerfile`/entrypoint.
  2. uvicorn arranca con `--proxy-headers` y una lista de proxies de confianza acorde a Render — verificable en el comando de arranque del contenedor.
  3. Al levantar el contenedor (`docker-compose up` o equivalente), las migraciones de Alembic y la siembra corren solas antes de que el servidor acepte tráfico, sin ningún paso manual adicional.
  4. El repositorio no conserva la rama `feature/https-produccion` sin resolver ni configuración de Caddy residual — solo sobrevive lo que aplica bajo Render (`--proxy-headers`, `sslmode=require`).
**Plans**: TBD

### Phase 2: Base de datos gestionada y bloqueo de login
**Goal**: Existe un Postgres gestionado alcanzable por IPv4 vía Session Pooler, y el bloqueo de intentos fallidos de login —escrito pero nunca probado por falta de una base real— queda validado contra esa base y mergeado a `develop`.
**Depends on**: Phase 1
**Requirements**: DEPLOY-02, CODE-01
**Success Criteria** (what must be TRUE):
  1. Existe un proyecto Supabase cuya `DATABASE_URL` usa el Session Pooler (host `*.pooler.supabase.com`, puerto 5432, IPv4, `sslmode=require`) y no la conexión directa IPv6-only.
  2. Una conexión de prueba desde fuera de la red de Supabase (por ejemplo, la máquina local) contra esa cadena tiene éxito y permite correr `alembic upgrade head` hasta el head del repositorio.
  3. La rama `feature/sprint-5-limite-intentos` está mergeada a `develop`, con sus tests corriendo en verde contra esta base real, no mockeada.
  4. Repetir intentos de login con credenciales inválidas bloquea la cuenta temporalmente, verificable consultando directamente la base de prueba.
**Plans**: TBD

### Phase 3: Higiene del repositorio y aprovisionamiento de Render
**Goal**: quien visite el repositorio público o la URL desplegada encuentra el proyecto Python actual, sin secretos expuestos en el historial, y un servicio corriendo con HTTPS real.
**Depends on**: Phase 2
**Requirements**: REPO-01, REPO-02, DEPLOY-01
**Success Criteria** (what must be TRUE):
  1. La rama por defecto en la página de GitHub del repositorio es la que contiene el proyecto Python (`develop` o promovida a `main`), no la implementación .NET.
  2. Un escaneo del historial completo de git (ej. `gitleaks detect --source . --log-opts="--all"`) no reporta secretos vigentes, o los reportados quedan rotados y anotados.
  3. La URL pública del servicio (`https://…onrender.com`) responde con un certificado HTTPS válido, verificable en cualquier navegador.
  4. El dashboard de Render muestra el servicio corriendo la imagen Docker del repositorio, apuntando a la rama correcta.
**Plans**: TBD

### Phase 4: Verificación técnica del despliegue en producción
**Goal**: el sistema desplegado se comporta como se espera bajo condiciones reales — se mantiene disponible, su arranque en frío está medido en vez de asumido, y el escáner QR funciona desde celulares reales contra HTTPS real.
**Depends on**: Phase 3
**Requirements**: DEPLOY-06, DEPLOY-07, DEMO-02, DEMO-03
**Success Criteria** (what must be TRUE):
  1. `/salud` responde 200 en la URL desplegada, y existe un job programado (ej. GitHub Actions) que lo consulta cada ~10 minutos, verificable en el historial de ejecuciones del job.
  2. El tiempo de arranque en frío, cronometrado tras dejar dormir el servicio y volver a pedirle una página, queda anotado en el repositorio (no citado de una fuente externa).
  3. Un celular Android real, apuntando a la URL desplegada, abre la cámara y escanea el código QR de un dispositivo registrado con éxito.
  4. Un iPhone real en Safari, apuntando a la misma URL, o bien escanea igual, o la limitación observada queda escrita para incorporarse al guion de la demo.
**Plans**: TBD

### Phase 5: Contenido de demo y documentación honesta
**Goal**: el sistema desplegado tiene datos reales que mostrar durante la sustentación, y cada afirmación en `docs/` y el README describe el sistema tal como está desplegado, no como se planeó.
**Depends on**: Phase 4
**Requirements**: DEMO-01, DOC-01, DOC-02, DOC-03
**Success Criteria** (what must be TRUE):
  1. La base desplegada contiene varios dispositivos con estados mixtos de entrada/salida y un historial de movimientos repartido en el tiempo, visible al generar un reporte o consultar auditoría en el sistema real.
  2. Ninguna línea de `README.md` afirma algo del despliegue que no coincide con la URL y la base real (ej. la afirmación "producción en Supabase" corresponde a un despliegue que sí existe).
  3. `docs/plan-de-trabajo.md` ya no describe una semana 1 en curso, y los pendientes que lista son los que realmente faltan a esta altura del proyecto.
  4. Existe, dentro de `docs/`, un diagrama de despliegue (cliente → servicio en Render → PostgreSQL en Supabase).
**Plans**: TBD

### Phase 6: Ensayo de la demo y plan de respaldo
**Goal**: la sustentación se puede correr de principio a fin sin sorpresas, con el despliegue calentado de antemano y una alternativa lista si la red del aula falla.
**Depends on**: Phase 5
**Requirements**: DEMO-04, DEMO-05
**Success Criteria** (what must be TRUE):
  1. Existe un guion escrito con la secuencia exacta de calentamiento (abrir la URL, iniciar sesión) que precede a la demo frente al instructor.
  2. El guion se ensayó de principio a fin al menos una vez, cronometrado, contra el despliegue real, y el tiempo quedó anotado.
  3. Existe un plan de respaldo documentado y probado (ej. `docker-compose up` local con datos sembrados, o un clip grabado del escáner QR) para el caso en que la red del aula falle.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Preparación del código para desplegar | 0/TBD | Not started | - |
| 2. Base de datos gestionada y bloqueo de login | 0/TBD | Not started | - |
| 3. Higiene del repositorio y aprovisionamiento de Render | 0/TBD | Not started | - |
| 4. Verificación técnica del despliegue en producción | 0/TBD | Not started | - |
| 5. Contenido de demo y documentación honesta | 0/TBD | Not started | - |
| 6. Ensayo de la demo y plan de respaldo | 0/TBD | Not started | - |
