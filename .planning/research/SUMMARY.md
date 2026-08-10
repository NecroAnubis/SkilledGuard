# Project Research Summary

**Project:** SkilledGuard
**Domain:** Entrega y sustentación de proyecto de grado SENA ADSO — despliegue gratuito de una app FastAPI + PostgreSQL ya construida, con demo en vivo
**Researched:** 2026-08-09/10
**Confidence:** MEDIUM-HIGH

## Executive Summary

Este no es un proyecto de construcción de producto — es un proyecto de **entrega**: el sistema (FastAPI + PostgreSQL, 5 sprints ya mergeados en `develop`) ya cumple el alcance funcional. Lo que falta para aprobar la sustentación es desplegarlo en una URL pública gratuita con HTTPS real, corregir la documentación para que describa el sistema tal como está (no como se planeó), y ensayar una demo en vivo con datos realistas y un plan B. Tres de los cuatro investigadores (Stack, Architecture, Pitfalls) convergieron de forma independiente en la misma combinación — **Render (compute, free web service) + Supabase (Postgres gestionado, free)** — y los tres coinciden también en el detalle técnico más fino y menos obvio: usar el **Session Pooler de Supabase (IPv4, puerto 5432)** en `DATABASE_URL`, nunca la cadena "Direct connection" que muestra primero el dashboard de Supabase, porque esa es IPv6-only y Render no tiene salida IPv6. Esa convergencia entre tres pasadas de investigación independientes es una señal fuerte, no una coincidencia — es el punto de fallo más probable si se ignora.

El riesgo dominante no es técnico-de-código, es **operativo-del-día-de-la-demo**: el free tier de Render duerme el contenedor a los 15 minutos de inactividad (cold start ~30-60s) y el Postgres de Supabase se pausa a los 7 días de inactividad (requiere un clic manual de "resume" en el dashboard, no se reactiva solo). Ninguno de los dos es un bug que haya que "arreglar" con infraestructura extra — la investigación de Architecture es explícita en que intentar mantenerlo siempre despierto con un pinger externo permanente viola el presupuesto cero sin necesidad; el enfoque correcto es un calentamiento manual (abrir la URL, hacer login) unos minutos antes de la sustentación, más un pinger de GitHub Actions activado solo el día de la defensa. El segundo riesgo crítico es específico del caso de uso: el escáner QR (`getUserMedia`) exige contexto seguro (HTTPS real, no IP local ni certificado autofirmado) — sin el HTTPS del PaaS funcionando, el sprint 5 (la pieza más demostrable del proyecto) no es demostrable desde un celular.

El tercer eje, distinto de los dos anteriores, es de **honestidad documental**: el README ya afirma "producción en Supabase" sobre un despliegue que hoy no existe, y `plan-de-trabajo.md` describe una semana 1 ya superada. La investigación de Features es clara en que esto no es un detalle cosmético — un evaluador que detecta una afirmación falsa en la documentación pierde confianza en todo el documento, no solo en esa línea. A esto se suma que la rama `main` de GitHub sigue siendo la implementación .NET retirada; cualquiera que abra el repo público aterriza en el proyecto equivocado. Ninguno de estos dos problemas requiere código nuevo — son correcciones de bajo esfuerzo y alto impacto en la percepción del evaluador.

## Key Findings

### Recommended Stack

Render (Web Service, Docker, free) para cómputo + Supabase (Postgres 16 gestionado, free) para base de datos, más un ping de mantenimiento activado solo el día de la defensa. No se agrega ningún paquete nuevo al proyecto — es configuración de plataforma sobre el `Dockerfile` y `docker-compose.yml` que ya existen.

**Core technologies:**
- **Render — Web Service (Docker)**: corre el `Dockerfile` existente, termina TLS, da subdominio `*.onrender.com` con HTTPS automático — único PaaS Docker mainstream que en agosto 2026 sigue abierto a cuentas nuevas con un tier realmente gratuito indefinido (Fly.io y Railway ya no lo tienen; Koyeb cerró altas nuevas tras ser adquirida por Mistral AI)
- **Supabase — Postgres (free)**: Postgres 16 gestionado, coincide con lo que el README ya declara; a diferencia del Postgres gratuito propio de Render (que expira a los 30 días, se borra a los 44), Supabase solo se **pausa** tras 7 días de inactividad y es recuperable con un clic hasta por un año
- **GitHub Actions cron (o cron-job.org) contra `/salud`**: mitiga a la vez el sleep de Render (15 min) y la pausa de Supabase (7 días) con un único ping; activarlo solo durante la ventana de la sustentación, no dejarlo corriendo semanas

**Detalle crítico no obvio:** el `DATABASE_URL` debe usar la cadena de **Session Pooler** de Supabase (host `*.pooler.supabase.com`, puerto 5432, IPv4), no la "Direct connection" (IPv6-only, falla en Render sin el add-on de pago). Session Pooler preserva semántica de sesión completa, necesaria para que Alembic corra DDL correctamente — la Transaction Pooler (puerto 6543) no sirve para eso.

### Expected Features

El SENA no tiene un formato único nacional de proyecto de grado ADSO — la evaluación real depende del centro y del instructor, y la rúbrica oficial (probablemente una variante de `GFPI-F-149`) todavía no está en manos del equipo. Esto no bloquea el trabajo: lo accionable ahora es corregir lo que ya existe para que sea honesto, no esperar la rúbrica para tocar `docs/`.

**Must have (table stakes):**
- Sistema desplegado y accesible por URL pública con HTTPS
- Documentación técnica base (ya existe en `docs/`) sin afirmaciones falsas frente al estado real
- Rama por defecto de GitHub mostrando el proyecto Python actual, no el .NET retirado
- Demo en vivo ensayada, con datos sembrados realistas y plan B sin red
- Conseguir el formato/rúbrica real del instructor (en paralelo, no bloquea el resto)
- Evidencia de proceso ya existente (historial de PRs, CI verde) — presentarla, no construirla

**Should have (diferenciadores, bajo esfuerzo porque ya existen):**
- Demo funcionando desde un celular real contra el despliegue (no solo el proyector)
- Narrativa explícita del "por qué" de decisiones técnicas (ya está en Key Decisions de PROJECT.md)
- CI verde (ruff + pytest) mostrado como evidencia de calidad
- Auditoría de cambios demostrada en vivo

**Defer / anti-features (no perseguir):**
- Funcionalidad de negocio nueva — el alcance ya está cubierto, agregar algo sin ensayar es más riesgo que ganancia
- Plantilla de documento "estilo SENA" genérica de internet presentada como si fuera la rúbrica oficial
- VPS propio con Caddy — contradice presupuesto cero, ya descartado
- App móvil nativa — el navegador con `getUserMedia` ya cubre el caso de uso
- Estudio de viabilidad financiera estilo `GFPI-F-144` — este es un proyecto de software, no de emprendimiento; no construir especulativamente

### Architecture Approach

Topología de dos nodos: cliente → Render (proxy de borde + contenedor único, free) → Supabase (Postgres gestionado, vía Session Pooler). No hay CDN ni host estático separado — la misma app FastAPI sirve `/api/*` y los estáticos vía `StaticFiles`; separar el frontend agregaría CORS y un segundo servicio a mantener sin ningún beneficio a esta escala. Las migraciones y el seed corren encadenados en el entrypoint del contenedor (`alembic upgrade head && python -m app.seed && uvicorn ...`) porque el free tier de Render no ofrece "pre-deploy command" ni shell/SSH — es la única opción disponible, y es segura porque el free tier limita a una sola instancia (sin condición de carrera en las migraciones).

**Major components:**
1. **Render Edge (proxy)** — termina TLS, reenvía `X-Forwarded-*`; requiere que uvicorn arranque con `--proxy-headers --forwarded-allow-ips="*"` o el app ve todo como HTTP interno
2. **Render Web Service (1 instancia, free)** — corre el Docker existente, cambia solo el comando de arranque (lee `$PORT`, encadena migración+seed antes de `uvicorn`)
3. **FastAPI app (sin cambios de código más allá de leer `$PORT`)** — routers, lógica de negocio, `StaticFiles`
4. **Supabase Session Pooler + Postgres** — endpoint IPv4 persistente, 14 tablas, esquema gobernado por Alembic

### Critical Pitfalls

1. **El servicio está dormido cuando el instructor hace clic en el link** — Render duerme a los 15 min, cold start de 30-60s. Mitigación: calentamiento manual (abrir la URL, hacer login) 5-10 min antes de la defensa, más un ping activado solo ese día.
2. **La cámara nunca abre porque la página no es un contexto seguro** — `getUserMedia` requiere HTTPS real (no IP local, no certificado autofirmado). Mitigación: nunca demostrar el escáner contra IP local o `http://`; confirmar HTTPS real del despliegue antes de cualquier ensayo con celular.
3. **La base de datos está pausada mientras el instructor mira** — Supabase pausa a los 7 días de inactividad y requiere clic manual de "resume" (no se despierta sola con una petición, a diferencia del cómputo). Mitigación: revisar el dashboard de Supabase el día antes de la defensa, no la hora antes.
4. **El sistema desplegado tiene un login de admin y nada más que mostrar** — el `seed.py` actual solo siembra catálogos + un admin, cero dispositivos ni historial. Mitigación: construir un seed de demo separado con datos realistas (dispositivos con nombres reales, estados mixtos entrada/salida, historial repartido en el tiempo, un usuario vigilante no-admin).
5. **La documentación afirma cosas que el sistema no hace, y el evaluador encuentra el hueco** — el README ya dice "producción en Supabase" sobre algo que no existe; una afirmación falsa detectada destruye la credibilidad de todo el documento, no solo de esa línea. Mitigación: pasada línea por línea de `docs/` y README contra el sistema real, justo antes de la entrega.

## Implications for Roadmap

Basado en la investigación combinada, estructura de fases sugerida, ordenada por dependencia real (no por calendario, ya que no hay fecha de sustentación fija):

### Phase 1: Preparar el código para desplegar (sin dependencia externa)
**Rationale:** Es lo único verificable localmente contra el `docker-compose.yml` existente, antes de tocar ninguna cuenta en la nube — cambios pequeños y de bajo riesgo que todo lo demás necesita.
**Delivers:** entrypoint que lee `$PORT`, agrega `--proxy-headers --forwarded-allow-ips="*"` a uvicorn, encadena `alembic upgrade head && python -m app.seed && uvicorn ...` como comando de arranque único.
**Addresses:** requisito Active "el sistema corre desplegado... sobre PostgreSQL gestionada" (habilitador).
**Avoids:** Pitfall 9 (headers de proxy mal configurados, falla silenciosa) y parte de Pitfall 6 (migraciones que nunca corren en el deploy).

### Phase 2: Provisionar Supabase y verificar conectividad IPv4
**Rationale:** Hay que confirmar que la cadena de conexión Session Pooler funciona *antes* de que Render entre en escena — así un fallo de conectividad no se confunde con un problema de la plataforma de cómputo.
**Delivers:** proyecto Supabase creado, cadena de conexión Session Pooler (IPv4, puerto 5432, `sslmode=require`) verificada desde fuera de la red de Supabase.
**Uses:** Supabase Postgres free tier (STACK.md).
**Implements:** componente "Supabase Session Pooler" de ARCHITECTURE.md.

### Phase 3: Higiene de repositorio y provisión de Render
**Rationale:** Cambiar la rama por defecto de GitHub tiene que pasar antes de o junto con el deploy — de lo contrario Render puede apuntar a la rama equivocada por defecto, y un evaluador que abra el repo en paralelo aterriza en el .NET retirado.
**Delivers:** rama default = `develop` (o promovida a `main`); servicio web en Render apuntando a la rama correcta; variables de entorno (`DATABASE_URL` con el pooler, `JWT_SECRET` nuevo y único, `ADMIN_DOCUMENTO`, `ADMIN_CONTRASENA`) configuradas solo en el dashboard, nunca commiteadas.
**Addresses:** requisitos Active "rama por defecto" y "URL pública con HTTPS".
**Avoids:** Pitfall 11 (evaluador aterriza en .NET retirado) y Pitfall 7 (secretos en el repo público — correr gitleaks contra todo el historial antes de esta fase o inmediatamente después).

### Phase 4: Primer deploy y verificación técnica
**Rationale:** Solo ahora hay algo real contra qué verificar — migraciones, salud, y el escáner QR desde un celular real, que es el check que valida el HTTPS de punta a punta.
**Delivers:** `/salud` responde 200, `alembic current` coincide con el head del repo, login del admin sembrado funciona, escáner QR probado desde un celular real (Android y, si es posible, iPhone en pestaña Safari normal) contra la URL `https://…onrender.com`.
**Addresses:** requisito Active "el escáner QR funciona desde un celular contra el sistema desplegado".
**Avoids:** Pitfall 2 (contexto inseguro) y Pitfall 3 (particularidades de iOS Safari) y Pitfall 6 (migraciones fallidas o no corridas).

### Phase 5: Datos de demo realistas
**Rationale:** Debe ejecutarse después de que el deploy es estable (el seed apunta a la DB real) y antes del ensayo (para que el ensayo ocurra contra datos creíbles, no un shell vacío).
**Delivers:** script de seed de demo (extensión de `seed.py` o script separado) con dispositivos de nombres realistas, estados mixtos entrada/salida, historial de auditoría repartido en varios días, y un usuario vigilante no-admin memorizable.
**Addresses:** diferenciador "demo funcionando... contra el despliegue" y evidencia de "control de acceso por rol".
**Avoids:** Pitfall 5 (sistema desplegado vacío, sin nada que mostrar).

### Phase 6: Corrección de documentación (auditoría de honestidad)
**Rationale:** Solo tiene sentido después de que el deploy es estable — verificar cada afirmación contra el sistema real requiere que el sistema real ya exista.
**Delivers:** pasada línea por línea de `README.md`, `plan-de-trabajo.md` y el resto de `docs/` eliminando o corrigiendo cualquier afirmación que la realidad no respalde (empezando por "producción en Supabase" y el estado de semana 1).
**Addresses:** requisito Active "la documentación describe el sistema tal como está, sin afirmaciones que la realidad no respalde".
**Avoids:** Pitfall 10 (documentación que afirma cosas falsas, credibilidad comprometida).

### Phase 7: Ensayo de demo y plan B
**Rationale:** Última fase — necesita todo lo anterior resuelto (deploy estable, datos realistas, documentación honesta) para ensayarse contra el estado final real.
**Delivers:** guion de demo ensayado de principio a fin, incluyendo secuencia de calentamiento (web service + DB, en orden), prueba del fallback local (`docker-compose up`) bajo presión de tiempo, y verificación de que el escáner tiene un plan B (cámara del portátil del presentador, o clip grabado) si la red del aula falla.
**Addresses:** requisito Active "la demo está ensayada de principio a fin, con datos sembrados y un plan de respaldo si falla la red del aula".
**Avoids:** Pitfall 1 (cold start durante la demo), Pitfall 4 (DB pausada), Pitfall 8 (red del aula cae sin plan B).

### Phase Ordering Rationale

- El código (Phase 1) no depende de ninguna cuenta externa y es lo primero verificable localmente — no tiene sentido provisionar infraestructura antes de que el entrypoint esté listo para recibirla.
- Supabase (Phase 2) se provisiona antes que Render (Phase 3) para aislar el problema de conectividad IPv4 del pooler de cualquier variable introducida por la plataforma de cómputo.
- La higiene de repo (rama default, gitleaks) se agrupa con la provisión de Render porque ambas son configuración de "primera impresión pública" y deben resolverse antes de que cualquiera —incluido un evaluador curioso— visite el repo o la URL.
- Los datos de demo (Phase 5) y la corrección de documentación (Phase 6) dependen explícitamente de que el deploy (Phase 4) sea estable — sembrar o documentar contra un sistema que todavía no despliega es doble trabajo si algo cambia.
- El ensayo (Phase 7) es literalmente el último paso porque es el único que requiere que todo lo anterior ya sea verdad al mismo tiempo.

### Research Flags

Phases likely needing deeper research during planning:
- **Ninguna** — la investigación ya cubrió los cuatro ejes (stack, features, arquitectura, pitfalls) con suficiente profundidad técnica para planificar directamente; los huecos que quedan (ver Gaps) son de naturaleza no investigable por web (hay que preguntarle al instructor o cronometrar en el dispositivo real), no de documentación técnica faltante.

Phases with standard patterns (skip research-phase):
- **Phase 1-4 (deploy técnico):** patrones bien documentados y verificados contra fuentes oficiales (Render, Supabase, uvicorn) — no requieren research-phase adicional.
- **Phase 5-7 (datos, documentación, ensayo):** son trabajo de contenido/proceso propio del proyecto, no de tecnología externa — no aplica research-phase.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Límites de plataforma verificados contra documentación oficial/changelogs de Render y Supabase; algunas cifras secundarias (ej. "$1/mes tras trial" de Railway) solo corroboradas por fuentes secundarias, no citadas verbatim |
| Features | MEDIUM | Triangulado entre múltiples fuentes secundarias (Studocu, blogs de instructores, PDFs republicados) — ninguna es la rúbrica oficial real de este instructor; el hallazgo central ("no hay formato único ADSO") está bien corroborado, pero el desglose de criterios/ponderación sigue sin verificar |
| Architecture | HIGH | Mecánica de plataforma verificada contra docs/changelogs actuales (2024-2026); patrones de despliegue (migrar-y-sembrar-al-arrancar, pooler de Supabase) confirmados con evidencia oficial y con inspección directa del código de este repo |
| Pitfalls | MEDIUM | Hechos centrales (expiración de 30 días en Render Postgres, regla de contexto seguro de `getUserMedia`, pausa de Supabase) confirmados contra documentación/changelogs oficiales; varios detalles de plataforma (segundos exactos de cold start, comportamiento específico de iOS PWA) vienen de una sola fuente de blog y deben re-verificarse cronometrando el platform real, no solo citando |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Cifras exactas de cold start (Render, Supabase) y comportamiento de iOS Safari/PWA:** marcadas explícitamente como LOW confidence en PITFALLS.md — vienen de fuentes secundarias de blog, no de documentación oficial cronometrada. No se resuelven investigando más por web; se resuelven en Phase 4/7 haciendo una prueba real cronometrada ("pause → wake → time it") en el dispositivo/plataforma efectivamente elegidos, antes de construir el guion de calentamiento de la demo sobre un número no verificado.
- **Rúbrica/formato oficial del instructor:** no investigable por web (vive en Territorium/Sofia Plus, específico del centro e instructor). Acción concreta: preguntarle directamente al instructor (ver sección "Cómo obtener el formato/rúbrica real" de FEATURES.md); en paralelo, no bloquea el resto del roadmap.
- **Si "evidencia de proceso" (Git history, CI) es un criterio formal evaluado o solo buena práctica:** sin fuente SENA que lo confirme como entregable obligatorio; de bajo costo presentarlo de todas formas (ya existe), así que no bloquea nada.
- **Disponibilidad de "pre-deploy command" de Render en el tier gratuito:** documentado solo para servicios de pago; STACK.md y ARCHITECTURE.md concluyen conservadoramente que no está disponible en free y usan el patrón de entrypoint como alternativa segura — no hace falta resolver este gap porque la alternativa ya es la elegida.

## Sources

### Primary (HIGH confidence)
- [Render — Deploy for Free](https://render.com/docs/free)
- [Render — Free PostgreSQL instances now expire after 30 days](https://render.com/changelog/free-postgresql-instances-now-expire-after-30-days-previously-90)
- [Render — Outbound IP Addresses](https://render.com/docs/outbound-ip-addresses)
- [Render — SSH and Shell Access](https://render.com/docs/ssh)
- [Render — Web Services](https://render.com/docs/web-services)
- [Supabase — Free Project Pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Supabase — Connect to your database](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Supabase — Dedicated IPv4 Address for Ingress](https://supabase.com/docs/guides/platform/ipv4-address)
- [Supabase — Supavisor troubleshooting/FAQ](https://supabase.com/docs/guides/troubleshooting/supavisor-faq-YyP5tI)
- [Uvicorn — Settings](https://uvicorn.dev/settings/)
- [FastAPI — Behind a Proxy](https://fastapi.tiangolo.com/advanced/behind-a-proxy/)
- [MDN — Secure contexts](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Secure_Contexts)
- [MDN — MediaDevices.getUserMedia()](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- [Fly.io — Resource Pricing](https://fly.io/docs/about/pricing/)
- [Railway — Free Trial](https://docs.railway.com/pricing/free-trial)
- [Hugging Face — Docker Spaces](https://huggingface.co/docs/hub/en/spaces-sdks-docker)
- [GitHub Docs — Branches](https://docs.github.com/en/pull-requests/reference/branches)
- Inspección directa del repositorio `/home/nekro/SkilledGuard`: `docker-compose.yml`, `app/seed.py`, `app/config.py`, `.env.example`, `README.md`, historial de ramas (`git branch -a`)

### Secondary (MEDIUM confidence)
- [TechCrunch — Mistral AI buys Koyeb (Feb 2026)](https://techcrunch.com/2026/02/17/mistral-ai-buys-koyeb-in-first-acquisition-to-back-its-cloud-ambitions/)
- [Koyeb — Scale-to-Zero docs](https://www.koyeb.com/docs/run-and-scale/scale-to-zero)
- [Etapa Productiva — sena.edu.co](https://ejecucionformacion.sena.edu.co/etapa-productiva)
- [Proyecto productivo — sena.edu.co](https://ejecucionformacion.sena.edu.co/etapa-productiva/alternativas/proyecto-productivo)
- [Requisitos y protocolo para sustentación del proyecto productivo (PDF republicado)](https://planetaeducacion.wordpress.com/wp-content/uploads/2021/06/requisitos-y-protocolo-para-realizar-la-sustentacion-del-proyecto-productivo-1.pdf)
- [Snyk — Why 28 million credentials leaked on GitHub in 2025](https://snyk.io/articles/state-of-secrets/)

### Tertiary (LOW confidence)
- [Runhooks — Koyeb free tier cold start](https://runhooks.app/blog/keeping-koyeb-free-tier-awake/) — no re-verificado por temporización real
- [Neon free tier review, Medium](https://medium.com/@philmcc/neon-postgres-review-serverless-postgresql-that-actually-scales-to-zero-ee14d4e109ba) — cifras de cold start de Neon (300-800ms) sin verificar de forma independiente
- [VideoSDK — WebRTC Safari 2025 Developer's Guide](https://www.videosdk.live/developer-hub/webrtc/webrtc-safari) — comportamiento de iOS Safari/PWA, necesita prueba en dispositivo real
- [Apple Developer Forums — WebRTC getUserMedia en standalone](https://developer.apple.com/forums/thread/89981) — foro no oficial
- Studocu / Scribd / SlideShare (múltiples entradas en FEATURES.md) — evidencia de otros aprendices ADSO, no formato oficial del instructor de este proyecto

---
*Research completed: 2026-08-10*
*Ready for roadmap: yes*
