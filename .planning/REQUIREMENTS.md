# Requerimientos — Milestone de entrega y sustentación

**Definido:** 2026-08-09
**Contexto:** el software ya está construido (sprints 1–5). Este ciclo entrega y
sustenta lo que existe. Ver `.planning/PROJECT.md` y `.planning/research/SUMMARY.md`.

---

## v1 Requirements

### Despliegue (DEPLOY)

- [ ] **DEPLOY-01**: La aplicación se ejecuta en Render como servicio Docker y
      responde en una URL pública con HTTPS
- [ ] **DEPLOY-02**: La aplicación persiste sus datos en una base PostgreSQL
      gestionada en Supabase, conectada por el Session Pooler (IPv4) con
      `sslmode=require`
- [ ] **DEPLOY-03**: El contenedor escucha en el puerto que le indica la
      plataforma (`$PORT`) en vez del 8000 fijo del Dockerfile
- [ ] **DEPLOY-04**: uvicorn corre con `--proxy-headers` y una lista de proxies
      de confianza acorde a Render, de modo que la bitácora de intentos de
      login registre la IP real del cliente y no la del proxy
- [ ] **DEPLOY-05**: Las migraciones de Alembic y la siembra idempotente se
      ejecutan solas al arrancar el contenedor, sin intervención manual
- [ ] **DEPLOY-06**: Un trabajo programado consulta `/salud` cada ~10 minutos,
      evitando que Render duerma el servicio y que Supabase pause el proyecto
- [ ] **DEPLOY-07**: El tiempo real de arranque en frío está medido y anotado,
      en vez de asumido a partir de fuentes secundarias

### Demostrabilidad (DEMO)

- [ ] **DEMO-01**: La base desplegada contiene equipos y un historial de
      movimientos suficientes para que reportes y auditoría muestren contenido
      real durante la demo
- [ ] **DEMO-02**: El escáner de QR funciona desde un celular Android real
      contra el despliegue
- [ ] **DEMO-03**: El escáner de QR funciona desde iOS Safari real, o su
      limitación está documentada y contemplada en el guion
- [ ] **DEMO-04**: Existe un guion de sustentación ensayado de principio a fin,
      con la secuencia de calentamiento previa incluida
- [ ] **DEMO-05**: Existe un plan de respaldo documentado y probado para el caso
      de que falle la red del aula — el único riesgo del día que el keep-alive
      no cubre

### Documentación (DOC)

- [ ] **DOC-01**: Ninguna afirmación de `docs/` ni del README describe algo que
      el sistema no hace o no tiene desplegado
- [ ] **DOC-02**: `docs/plan-de-trabajo.md` refleja el estado real del proyecto
      y sus pendientes vigentes
- [ ] **DOC-03**: Existe el diagrama de despliegue del sistema desplegado
      (cliente → servicio en Render → PostgreSQL en Supabase)

### Higiene del repositorio (REPO)

- [ ] **REPO-01**: La rama por defecto de GitHub muestra el proyecto Python
      actual y no la implementación .NET retirada
- [ ] **REPO-02**: El historial completo de git está escaneado y libre de
      secretos expuestos

### Código pendiente (CODE)

- [ ] **CODE-01**: El bloqueo temporal del login tras intentos fallidos está
      probado contra una base real y mergeado a `develop`
- [ ] **CODE-02**: Del trabajo de HTTPS se conserva únicamente lo que aplica
      bajo Render, y el proxy Caddy queda descartado sin dejar configuración
      muerta en el repositorio

---

## v2 Requirements (aplazados)

- **Obtener la rúbrica oficial del instructor** — deseleccionado en v1. Sin
  ella, la estructura de `docs/` sigue siendo una apuesta razonable pero no
  verificada; la investigación confirmó que el formato lo define cada centro e
  instructor, así que no hay forma de deducirlo. Todo lo que está en v1 vale
  bajo cualquier rúbrica, de modo que esto no bloquea nada.
- **Reestructurar `docs/` a la plantilla oficial** — depende de la anterior.

---

## Out of Scope

- **Funcionalidad de negocio nueva** — el alcance ya está cubierto; una feature
  sin ensayar es más riesgo el día de la demo que ganancia de nota
- **VPS propio con Caddy** — contradice el presupuesto cero y agrega un
  servidor que administrar; el PaaS ya termina el TLS
- **Base de datos gratuita de Render** — se elimina a los ~44 días de creada, y
  este milestone no tiene fecha de cierre
- **Aplicación móvil nativa** — el navegador con `getUserMedia` sobre HTTPS ya
  cubre el caso de la portería
- **Estudio de viabilidad financiera o de mercado** — este es un proyecto de
  software, no una propuesta de emprendimiento; construirlo especulativamente
  es trabajo que no cuenta
- **Reescribir la documentación de cero antes de tener la rúbrica** — sería
  hacerla dos veces; lo urgente es que sea honesta, no que cambie de estructura

---

## Trazabilidad

| REQ-ID | Fase |
|--------|------|
| DEPLOY-01 | Phase 3 |
| DEPLOY-02 | Phase 2 |
| DEPLOY-03 | Phase 1 |
| DEPLOY-04 | Phase 1 |
| DEPLOY-05 | Phase 1 |
| DEPLOY-06 | Phase 4 |
| DEPLOY-07 | Phase 4 |
| DEMO-01 | Phase 5 |
| DEMO-02 | Phase 4 |
| DEMO-03 | Phase 4 |
| DEMO-04 | Phase 6 |
| DEMO-05 | Phase 6 |
| DOC-01 | Phase 5 |
| DOC-02 | Phase 5 |
| DOC-03 | Phase 5 |
| REPO-01 | Phase 3 |
| REPO-02 | Phase 3 |
| CODE-01 | Phase 2 |
| CODE-02 | Phase 1 |
