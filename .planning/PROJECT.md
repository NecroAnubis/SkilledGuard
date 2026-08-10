# Skilled Guard

## What This Is

Sistema que digitaliza el control de ingreso y salida de equipos tecnológicos en
portería, reemplazando la minuta en papel: los equipos se identifican con un
código QR y cada movimiento queda registrado, auditado y consultable. Sus
usuarios son el vigilante que escanea en la puerta y el administrador que
gestiona usuarios, equipos y reportes.

Es el proyecto de grado de Johan S. Restrepo para el Tecnólogo en Análisis y
Desarrollo de Software (ADSO) del SENA. El producto ya funciona; este ciclo no
es de construir, es de **entregar y sustentar**.

## Core Value

Que el proyecto se pueda sustentar y aprobar: un sistema desplegado y accesible,
la documentación que exige el programa, y una demo que funcione en vivo delante
del instructor.

## Requirements

### Validated

Capacidades ya construidas y mergeadas en `develop` (sprints 1–5):

- ✓ Autenticación con JWT y control de acceso por rol — sprint 1
- ✓ Gestión de usuarios, roles y tipos de documento — sprint 1
- ✓ Contraseñas con hash bcrypt (antes viajaban en texto plano) — sprint 1
- ✓ Esquema versionado con Alembic sobre PostgreSQL, 14 entidades — sprint 1
- ✓ Registro de dispositivos y generación de su código QR — sprint 2
- ✓ Registro de entrada y salida en portería, con validación de estado que
  impide doble ingreso o doble salida — sprint 2
- ✓ Auditoría de cada cambio de datos, con usuario y detalle — sprint 3
- ✓ Reportes descargables en Excel y PDF, filtrables — sprint 3
- ✓ Documentación del proyecto y diagramas UML — sprint 4
- ✓ Interfaz web con escáner de QR por cámara — sprint 5
- ✓ Integración continua (ruff + pytest) en cada Pull Request — sprint 1
- ✓ Empaquetado con Docker y docker-compose — sprint 1

### Active

- [ ] El sistema corre desplegado en una URL pública con HTTPS, sobre una base
      PostgreSQL gestionada
- [ ] Existe el formato oficial de documentación del programa, y la
      documentación del repositorio está ajustada a él
- [ ] La documentación del repositorio describe el sistema tal como está, sin
      afirmaciones que la realidad no respalde
- [ ] El escáner QR funciona desde un celular contra el sistema desplegado
- [ ] Los riesgos que `CONCERNS.md` marque como reales de cara a la
      sustentación están atendidos o documentados como decisión consciente
- [ ] La rama por defecto del repositorio muestra el proyecto actual y no la
      implementación .NET retirada
- [ ] La demo está ensayada de principio a fin, con datos sembrados y un plan
      de respaldo si falla la red del aula

### Out of Scope

- **Funcionalidad nueva de negocio** — el producto ya cubre el alcance
  planteado; agregar módulos ahora compite con la entrega y no suma a la nota
- **Servidor propio (VPS) con Caddy** — se optó por PaaS gratuito, que ya
  termina el TLS; mantener un proxy propio sería infraestructura sin dueño
- **Aplicación móvil nativa** — la interfaz web con cámara cubre el caso de la
  portería; una app nativa es un proyecto aparte
- **Cualquier costo recurrente** — presupuesto cero estricto

## Context

**Estado del código.** Cinco sprints mergeados por Pull Request a `develop`.
Backend FastAPI 0.115 sobre Python 3.12, SQLAlchemy 2.0, Alembic, PostgreSQL 16,
JWT + bcrypt, frontend estático servido por la misma app. Mapa completo del
codebase en `.planning/codebase/`.

**Historia del repositorio.** El proyecto nació en C#/ASP.NET Core y se
reescribió en Python en el sprint 1. Queda residuo del código viejo en el árbol
(`SkilledGuard.sln`, `CódigoBackend/`, `Base_de_Datos/`) y, más importante, la
rama `main` de GitHub **sigue siendo la versión .NET**: todo el trabajo actual
vive en `develop`. El repositorio es público, así que cualquiera que lo abra
aterriza hoy en el proyecto retirado.

**Trabajo escrito pero sin mergear.** Dos ramas locales: bloqueo temporal del
login tras intentos fallidos (`feature/sprint-5-limite-intentos`, con su
migración, sin tests ejecutados por falta de un Postgres local) y HTTPS con
Caddy (`feature/https-produccion`). Con la decisión de ir a PaaS, de esta última
solo conservan sentido `--proxy-headers` en uvicorn y `sslmode=require` para la
base gestionada; el proxy Caddy sobra.

**Documentación.** `docs/` tiene levantamiento, requerimientos, ficha técnica,
diagramas UML, manuales y planes de trabajo y pruebas — pero la lista de
entregables se dedujo de la estructura típica de ADSO, no de la rúbrica de la
ficha. `plan-de-trabajo.md` describe un proyecto en la semana 1 y todavía lista
como pendientes cosas ya resueltas. El README afirma "producción en Supabase"
sobre un despliegue que no existe.

**Riesgo del escáner.** `getUserMedia` solo entrega la cámara en contexto
seguro. Funciona en `localhost` por excepción del navegador, pero desde un
celular apuntando a una IP o a un sitio sin HTTPS, se niega. El HTTPS del
despliegue no es cosmético: es lo que hace demostrable el sprint 5.

## Constraints

- **Presupuesto**: cero estricto — solo capas gratuitas; el proyecto no puede
  depender de nada que se cobre
- **Timeline**: sin fecha de sustentación definida — el roadmap se ordena por
  dependencias, no por calendario
- **Despliegue**: PaaS gratuito + PostgreSQL gestionado, sin servidor propio
  que administrar
- **Stack**: Python 3.12 / FastAPI / PostgreSQL — ya decidido y construido; no
  se reabre
- **Evaluación**: el criterio real lo fija la rúbrica del instructor, que
  todavía no está en nuestras manos
- **Idioma**: código, comentarios y documentación en español, por convención
  del repositorio y porque el evaluador lee en español

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Este ciclo es de entrega, no de producto | El sistema ya cumple el alcance; lo que falta para aprobar es despliegue, documentación y demo | — Pending |
| PaaS gratuito en vez de VPS con Caddy | Presupuesto cero y sin servidor que administrar; el PaaS ya da HTTPS y subdominio | — Pending |
| La demo corre contra la nube | Es más convincente y el escáner QR necesita HTTPS real para funcionar desde un celular | — Pending |
| Se atiende lo que `CONCERNS.md` señale | El mapa automático puede exagerar o equivocarse; se filtra por impacto real en la sustentación | — Pending |
| Migración .NET → Python (sprint 1) | El esquema original no ejecutaba y las contraseñas se guardaban en texto plano | ✓ Good |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-08-09 after initialization*
