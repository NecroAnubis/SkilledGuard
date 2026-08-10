# Feature Research

**Domain:** SENA ADSO (Tecnólogo en Análisis y Desarrollo de Software) — entrega y sustentación de proyecto de grado
**Researched:** 2026-08-09
**Confidence:** MEDIUM overall (triangulated across multiple independent secondary sources — Studocu, blogs de instructores, PDFs institucionales republicados — none son la fuente primaria de sena.edu.co ni la rúbrica del instructor real de este proyecto)

## Hallazgo central (léelo antes de las tablas)

**El SENA no tiene un "formato único nacional de proyecto de grado ADSO"** al estilo tesis universitaria. Lo que existe es:

1. Un **proyecto formativo** transversal a todo el programa (14–27 meses), que se evalúa por **competencias y resultados de aprendizaje**, no por una sola nota final. Cada resultado de aprendizaje se demuestra con evidencias de **conocimiento**, **desempeño** y **producto**, y el instructor emite un **juicio de evaluación** (Aprobado / Aún no aprobado / Por evaluar) — no un porcentaje único. [MEDIUM]
2. Una **etapa productiva** final (≈864 horas) con **cinco modalidades posibles**: contrato de aprendizaje, vínculo laboral, monitoría, apoyo a instituciones, o **proyecto productivo** (seguir desarrollando tu propio proyecto). SkilledGuard encaja en esta última. La documentación y evaluación de esta etapa **varía por centro de formación y por instructor** — no hay una rúbrica única confirmada para todos los centros. [MEDIUM, confirmado por 2 fuentes independientes que dicen explícitamente "varía por centro"]
3. Formatos SENA con código **GFPI-*** que sí son oficiales y estandarizados a nivel nacional, pero cubren procesos administrativos, no el contenido técnico del software:
   - `GFPI-F-149` (v2) — Rúbrica de evaluación final del proyecto / sustentación de transferencia. Umbral de aprobación reportado: **80% de cumplimiento**. [MEDIUM — no se pudo obtener el desglose de criterios/ponderación]
   - `GFPI-F-144` — Plantilla de proyecto productivo **bajo enfoque empresarial** (estudio de mercado, técnico, organizacional, viabilidad financiera). Aplica a proyectos de emprendimiento, no necesariamente a un proyecto de software puro — **no asumir que aplica a SkilledGuard sin confirmarlo con el instructor**.
   - `GFPI-F-023` / `GFPI-F-024` — Planeación, seguimiento y evaluación de la etapa productiva.
   - `GFPI-F-147` — Bitácora de etapa productiva.
   - `GC-F-004` — Plantilla de presentación PowerPoint para la sustentación (el instructor la entrega antes de la defensa).
   - Todo se sube al LMS **Territorium** (`sena.territorio.la`), no a un repositorio ni a un portal aparte.

**Consecuencia directa para este proyecto:** la carpeta `docs/` actual (levantamiento, requerimientos, ficha técnica, UML, manuales, plan de pruebas, plan de trabajo) es una **buena apuesta genérica de SDLC** — coincide razonablemente con lo que un proyecto de software SENA produce en la práctica (evidencia recurrente en Studocu de otros aprendices ADSO: MER, diagrama de clases, casos de uso, manual técnico, manual de usuario, plan de pruebas sí aparecen como entregables típicos) — pero **no está validada contra la rúbrica real de este instructor**, y el README que dice "producción en Supabase" sobre algo que no existe es exactamente el tipo de afirmación que un evaluador que lee la documentación va a detectar y penalizar.

## Feature Landscape

### Table Stakes (sin esto el proyecto no se aprueba)

| Entregable / Acción | Por qué es obligatorio | Esfuerzo | Notas |
|---------|--------------|------------|-------|
| Sistema desplegado y accesible (URL pública) | La sustentación SENA para software es una demo funcional en vivo — "explicar avances funcionales con comunicación técnica"; sin despliegue no hay demo, hay slideshow | MEDIUM | Ya es un `[ ]` Active en PROJECT.md. HTTPS no es cosmético: el escáner QR por cámara (`getUserMedia`) lo exige desde celular |
| Documentación técnica base (requerimientos, diagramas UML, manual técnico, manual de usuario, plan de pruebas) | Aparece de forma consistente como entregable típico en evidencias de otros aprendices ADSO (Studocu) y es lo mínimo que cualquier instructor de software va a pedir para verificar que hubo análisis y diseño, no solo código | ALREADY DONE | Ya existe en `docs/`. El riesgo no es la ausencia, es que **describa el sistema real** y no una versión aspiracional |
| Documentación sin afirmaciones falsas | Un evaluador que lee "producción en Supabase" y luego ve que no existe pierde confianza en TODO el documento, no solo en esa línea — mismo principio que "un comentario que afirma algo falso manda por el camino equivocado" | LOW | Ya es un `[ ]` Active. Auditoría línea por línea de `docs/` contra el estado real |
| Repositorio con la rama por defecto mostrando el proyecto actual | El repo es público; si `main` sigue en .NET, cualquiera (incluido el evaluador si lo revisa) aterriza en el proyecto retirado — contradice la narrativa de la sustentación | LOW | `[ ]` Active — probablemente un `git checkout` + merge o cambio de default branch en GitHub, no reescritura |
| Demo en vivo ensayada, con datos sembrados y plan B sin red | Formato constante en toda sustentación colombiana (SENA y universitaria): la exposición formal seguida de preguntas del evaluador; fallar la demo en vivo es el riesgo #1 reportado en fuentes sobre sustentaciones | MEDIUM | `[ ]` Active. El plan B (video de respaldo, entorno local si falla la red del aula) es barato y cubre el mayor riesgo del día |
| Conseguir el formato/rúbrica real del instructor | Es la única forma de saber si `docs/` está completo o le falta/sobra algo — todo lo demás en esta lista es la mejor apuesta sin esa rúbrica | LOW (una conversación) | Ver sección "Cómo obtenerlo" abajo. Esto no es investigable por web: varía por centro e instructor |
| Evidencia de que el proceso fue real (no solo el resultado) | El modelo SENA evalúa competencias por evidencia de **desempeño**, no solo de **producto** — un sistema que funciona sin rastro de cómo se construyó no demuestra competencia de proceso | LOW — ya existe | Historial de PRs por sprint, CI (ruff+pytest) en cada PR, y commits ya narran el proceso. Falta solo **presentarlo** explícitamente en la sustentación/documentación, no recrearlo |

### Differentiators (lo que hace destacar una entrega, no lo mínimo)

| Entregable / Acción | Por qué suma | Esfuerzo | Notas |
|---------|-------------------|------------|-------|
| Demo funcionando desde un celular real contra el despliegue | Va más allá de "funciona en el proyector" — demuestra que el caso de uso real (vigilante escaneando en portería) opera fuera de `localhost` | LOW (una vez desplegado con HTTPS) | Ya es `[ ]` Active — este es exactamente el punto donde HTTPS deja de ser checkbox y se vuelve demostración |
| Narrativa de "por qué" en las decisiones técnicas (ej. migración .NET→Python, JWT+bcrypt sobre texto plano) | Un evaluador de tecnólogo valora criterio, no solo ejecución — ya existe en Key Decisions de PROJECT.md, falta que llegue a la documentación/sustentación | LOW | Reusar lo que ya está en PROJECT.md → Key Decisions, no inventar nada nuevo |
| CI verde visible (ruff + pytest en cada PR) mostrado como evidencia de calidad | Pocos proyectos de estudiante de tecnólogo tienen integración continua real; es una señal de nivel por encima del promedio sin esfuerzo adicional (ya existe) | ALREADY DONE | Solo hace falta mencionarlo/mostrarlo en la sustentación, no construirlo |
| Auditoría de cambios (quién hizo qué) demostrada en vivo | Ya construida (sprint 3); mostrarla en la demo conecta directamente con el "por qué" del proyecto (trazabilidad de equipos en portería) | LOW | Reforzar el guion de demo para que la toque, no desarrollo nuevo |

### Anti-Features (esfuerzo que no mueve la nota)

| Actividad | Por qué parece buena idea | Por qué no ayuda aquí | Alternativa |
|---------|---------------|------------------|-------------|
| Construir funcionalidad de negocio nueva | "Más features = mejor proyecto" | El alcance ya está cubierto (sprints 1–5); una feature nueva sin ensayar es más riesgo de que algo se rompa el día de la demo que ganancia de nota — ya está marcado como Out of Scope en PROJECT.md | Pulir y ensayar lo que ya existe |
| Inventar/copiar una plantilla de documento "estilo SENA" genérica de internet y presentarla como si fuera la rúbrica oficial | Cierra la ansiedad de "no tengo el formato" | Si no coincide con lo que pide el instructor real, es trabajo de documentación que no cuenta para la nota y puede generar contradicciones (como el actual `plan-de-trabajo.md` que describe una semana 1 que ya pasó) | Pedir el formato real (ver abajo); mientras tanto, mantener `docs/` honesto sobre el estado real en vez de aspiracional |
| VPS propio con Caddy para HTTPS | Se siente "más profesional" tener servidor propio | Contradice presupuesto cero y constraint de "sin servidor propio que administrar"; ya descartado en PROJECT.md | PaaS gratuito con HTTPS incluido |
| App móvil nativa para el escáner | El caso de uso es "un celular en portería" | Un navegador con `getUserMedia` sobre HTTPS ya cubre la cámara; una app nativa es un proyecto de build aparte, no de entrega | Interfaz web ya construida en sprint 5 |
| Reescribir documentación existente de cero antes de tener la rúbrica | Sensación de estar "avanzando" en documentación | Si se reescribe dos veces (una a ciegas, otra cuando llegue la rúbrica real) es doble esfuerzo; lo urgente hoy es que sea *honesta*, no que tenga una estructura distinta | Auditar y corregir falsedades en `docs/` ahora; reestructurar solo cuando/si la rúbrica real lo exija |

## Feature Dependencies

```
Rúbrica real del instructor (conseguirla)
    └──informa──> Estructura final de docs/ (qué falta/sobra)

Despliegue con HTTPS + PostgreSQL gestionada
    └──requiere──> Escáner QR funcional desde celular (getUserMedia exige contexto seguro)
                       └──habilita──> Demo en vivo desde celular real

Rama default = proyecto actual (no .NET)
    └──previene──> Evaluador aterriza en versión retirada si revisa el repo

Documentación honesta (sin afirmaciones falsas)
    └──requiere──> Auditoría línea por línea de docs/ contra el estado real del código

Historial de PRs + CI ya existente
    └──enhances──> Narrativa de "evidencia de proceso" en la sustentación (no construir nada nuevo, presentar lo que ya hay)
```

### Dependency Notes

- **Despliegue requiere HTTPS antes que la demo del escáner tenga sentido:** `getUserMedia` se niega en un sitio no seguro desde un celular apuntando a IP o HTTP plano; sin esto, el sprint 5 (interfaz con cámara) no es demostrable fuera de `localhost`. Esto ya está identificado como riesgo en PROJECT.md → "Riesgo del escáner".
- **La rúbrica real informa la estructura de `docs/`, pero no la bloquea:** mientras no llegue, lo accionable es corregir falsedades (bajo esfuerzo, alto impacto) en vez de esperar para tocar la documentación.
- **Evidencia de proceso ya existe, solo falta exponerla:** no hay dependencia de construir nada — el PR/CI history de los 5 sprints ya es la evidencia; la tarea es narrativa/presentación, no desarrollo.

## MVP Definition

### Para aprobar la sustentación (obligatorio)

- [ ] Sistema desplegado en URL pública con HTTPS sobre PostgreSQL gestionada — sin esto no hay demo real
- [ ] Rama default de GitHub = proyecto Python actual, no .NET — bajo esfuerzo, alto riesgo si se ignora
- [ ] `docs/` auditado y corregido para no afirmar nada que la realidad no respalde
- [ ] Escáner QR probado desde un celular real contra el despliegue
- [ ] Demo ensayada de principio a fin con datos sembrados y plan B sin red
- [ ] Conversación con el instructor para obtener el formato/rúbrica oficial (paralelo, no bloquea lo anterior)

### Agregar si la rúbrica real lo exige (v1.x)

- [ ] Reestructurar `docs/` a la plantilla oficial del instructor, si difiere de lo actual
- [ ] Documento adicional específico (ej. GFPI-F-144 si el centro exige enfoque empresarial) — solo si se confirma que aplica

### No perseguir salvo pedido explícito del instructor (v2+ / fuera de alcance)

- [ ] Estudio de viabilidad financiera / mercado estilo GFPI-F-144 — este proyecto no es una propuesta de emprendimiento, es un proyecto de software; no construir esto especulativamente
- [ ] Cualquier entregable "por si acaso" sin confirmación de que el centro/instructor lo pide

## Cómo obtener el formato/rúbrica real (acción concreta, no investigable por web)

1. **Nombre a preguntarle al instructor:** "¿cuál es el formato/rúbrica de evaluación final del proyecto que va a usar?" — es probable que sea una variante de `GFPI-F-149` (rúbrica de evaluación final / sustentación) o un formato propio del centro de formación. También preguntar si hay una plantilla de presentación obligatoria (equivalente a `GC-F-004`).
2. **Dónde suele vivir:** la plataforma **Territorium** (LMS de la etapa productiva, `sena.territorio.la`) o **Sofia Plus**, dentro de la carpeta del proyecto/etapa productiva asignada al aprendiz — no en un repositorio de GitHub ni en documentación pública.
3. **Qué preguntar específicamente además del formato:**
   - ¿Cuál de las 5 modalidades de etapa productiva aplica aquí (probablemente "proyecto productivo")?
   - ¿Se evalúa con una sola rúbrica final o por resultados de aprendizaje independientes?
   - ¿Hay una plantilla de PowerPoint obligatoria para la sustentación?
   - ¿Qué evidencia de proceso quiere ver (historial de Git, tablero Scrum, bitácora)?
4. **Mientras tanto:** no reescribir `docs/` sobre una plantilla genérica encontrada en internet — corregir lo que ya existe para que sea honesto, que es válido bajo cualquier rúbrica que llegue.

## Gaps explícitos (no se pudo verificar sin la rúbrica real del instructor)

- **Desglose de criterios y ponderación de `GFPI-F-149`** (o de cualquier rúbrica que use el centro/instructor de este aprendiz): se confirmó que existe y que el umbral reportado en una fuente es 80% de cumplimiento, pero no se pudo obtener qué pesa cada criterio (funcionalidad vs. documentación vs. proceso vs. sustentación oral).
- **Si aplica un formato tipo GFPI-F-144 (enfoque empresarial)** a este proyecto específico — depende de si el centro clasifica el "proyecto productivo" de este aprendiz como emprendimiento o como desarrollo de software puro.
- **Duración y formato exacto de la sustentación para ADSO específicamente** (solo se encontró la norma general colombiana de sustentaciones: ~20 min de exposición + preguntas del jurado/instructor; no una cifra oficial SENA-ADSO).
- **Si "evidencia de proceso" (Git history, CI, tablero) es un criterio formal evaluado** o solo una buena práctica — no se encontró una fuente SENA que lo liste como entregable obligatorio; se recomienda igual porque el costo de presentarlo es casi cero (ya existe) y el modelo de evaluación por competencias sí valora evidencia de desempeño, no solo de producto.
- **Confirmación de que este proyecto usa la modalidad "proyecto productivo"** de la etapa productiva (vs. estar enmarcado como proyecto formativo transversal sin etapa productiva aún) — afecta qué formatos GFPI aplican.

## Sources

- [Requisitos y protocolo para sustentación del proyecto productivo (PDF republicado)](https://planetaeducacion.wordpress.com/wp-content/uploads/2021/06/requisitos-y-protocolo-para-realizar-la-sustentacion-del-proyecto-productivo-1.pdf) — MEDIUM, menciona GFPI-F-149 v2, umbral 80%, carga en LMS
- [Etapa Productiva — sena.edu.co (ejecucionformacion.sena.edu.co)](https://ejecucionformacion.sena.edu.co/etapa-productiva) — MEDIUM-HIGH (dominio institucional SENA)
- [Proyecto productivo — sena.edu.co](https://ejecucionformacion.sena.edu.co/etapa-productiva/alternativas/proyecto-productivo) — MEDIUM-HIGH (dominio institucional SENA)
- [Qué es la Etapa Productiva en el SENA (5 modalidades)](https://sena-sofia-plus.com.co/productive-stage-sena/) — MEDIUM, confirma que documentación/evaluación varía por centro
- [GFPI-F-144 Formato Plantilla del Proyecto Productivo bajo enfoque Empresarial](https://es.scribd.com/document/603928148/GFPI-F-144-Formato-Plantilla-del-Proyecto-Productivo-bajo-enfoque-Empresarial-1-2) — MEDIUM, secundaria (Scribd), confirma alcance empresarial del formato
- [GFPI-F-023 / GFPI-F-024 Formato de Planeación, Seguimiento y Evaluación de Etapa Productiva (Studocu)](https://www.studocu.com/co/document/sena-sofiaplus/adso/formato-de-planeacion-seguimiento-y-evaluacion-de-etapa-productiva-gfpi-f-023/149244468) — LOW-MEDIUM, secundaria de aprendiz, no oficial
- [Lista de Chequeo para Evaluación de Proyectos SENA ADSO (Studocu)](https://www.studocu.com/co/document/sena-sofiaplus/adso/lista-de-chequeo-para-evaluacion-de-proyectos-sena-2562074/133732127) — no accesible en detalle (contenido bloqueado por login), referenciado solo por título
- [Evidencia Especificación de requisitos software — SENA ADSO (Studocu, ejemplo de aprendiz real)](https://www.studocu.com/co/document/servicio-nacional-de-aprendizaje/tecnologo-en-analisis-y-desarrollo-de-software/evidencia-especificacion-de-requisitos-software-sena-adso/67080107) — LOW-MEDIUM, evidencia real de otro aprendiz, no formato oficial
- [Proyecto Formativo — metodología de 4 fases (Análisis, Planeación, Ejecución, Evaluación) — SlideShare/blogs SENA](https://www.slideshare.net/slideshow/presentacion-sena-proyecto-formativo-pptx/272093514) — MEDIUM, consistente entre múltiples fuentes independientes
- [Guía para la sustentación de una tesis o proyecto de grado — Uniandes LEO](https://leo.uniandes.edu.co/guia-para-la-sustentacion-de-una-tesis/) — MEDIUM, norma general colombiana de sustentación (no SENA-específica)

---
*Feature research for: SENA ADSO — entrega y sustentación de proyecto de grado*
*Researched: 2026-08-09*
