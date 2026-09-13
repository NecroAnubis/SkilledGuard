# Levantamiento de información

**Proyecto:** Skilled Guard — Sistema de Automatización para el Control de Ingreso de Equipos Tecnológicos
**Autor:** Johan S. Restrepo
**Programa:** Tecnólogo en Análisis y Desarrollo de Software (ADSO) — SENA

---

## 1. Contexto

En el centro de formación, aprendices e instructores ingresan a diario con equipos tecnológicos propios: computadores portátiles, tabletas y teléfonos. Para evitar que un equipo salga en manos de quien no lo trajo, el personal de portería anota manualmente cada entrada y cada salida en una **minuta** en papel.

## 2. Situación actual

El registro manual consiste en anotar, por cada persona:

- Nombre y documento de identidad
- Descripción del equipo (marca, modelo, serial)
- Hora de ingreso y, más tarde, hora de salida
- Firma

### Problemas identificados

| # | Problema | Consecuencia |
|---|---|---|
| 1 | **Lentitud.** El registro toma en promedio 10 minutos por persona | Filas en la entrada, especialmente en horas pico |
| 2 | **Pérdida de trazabilidad.** Consultar el historial de un equipo exige revisar cuadernos hoja por hoja | En la práctica, nadie consulta el historial |
| 3 | **Riesgo de fraude.** No hay forma de verificar que el equipo que sale es el mismo que entró | Un equipo puede salir en manos equivocadas sin que el registro lo evidencie |
| 4 | **Errores de transcripción.** Los seriales se copian a mano | Un serial mal anotado invalida el registro completo |
| 5 | **Deterioro y pérdida física.** El papel se moja, se pierde o se llena | La información desaparece |

### Causa raíz

El registro depende por completo de la escritura manual y de la memoria del guarda de seguridad. **No existe un identificador confiable del equipo** que pueda verificarse en segundos.

## 3. Técnicas de recolección aplicadas

| Técnica | Aplicación |
|---|---|
| **Observación directa** | Registro del proceso en portería en horario de ingreso |
| **Entrevista** | Conversación con personal de seguridad sobre el procedimiento y sus dificultades |
| **Análisis documental** | Revisión de las minutas existentes para identificar qué datos se capturan |

## 4. Hallazgos

1. Los datos que realmente se necesitan son pocos: **quién**, **qué equipo**, **cuándo** y **en qué sentido** (entra o sale).
2. El serial del equipo ya identifica al equipo de forma única, pero **transcribirlo a mano es justo el paso lento y propenso a error**.
3. El personal de portería rota. Un sistema que dependa de recordar procedimientos complejos no funcionará.
4. **Nadie revisa las minutas.** La información se captura pero no se usa, porque consultarla cuesta más de lo que vale.
5. El error más costoso no es registrar mal una entrada, sino **registrar una salida que no corresponde**: ahí es donde se pierde un equipo.

## 5. Necesidades derivadas

De los hallazgos se desprende que el sistema debe:

- **Identificar el equipo sin escribir nada** → código QR impreso y pegado al equipo.
- **Registrar el movimiento en segundos** → un escaneo y un botón.
- **Impedir movimientos imposibles** → un equipo que ya está adentro no puede volver a entrar; uno que no ha entrado no puede salir. Esto ataca directamente el hallazgo 5.
- **Hacer la consulta barata** → historial filtrable por equipo, persona y fecha, con exportación a Excel y PDF.
- **Dejar rastro de quién registró cada movimiento** → responsabilidad individual.
- **Ser simple de operar** → el personal rota; la interfaz debe explicarse sola.

## 6. Alcance del sistema

### Incluido

- Registro de usuarios con tres roles diferenciados
- Registro de equipos con generación de código QR
- Validación de ingreso y salida mediante escaneo
- Consulta de trazabilidad e historial
- Reportes descargables en Excel y PDF
- Rastro de auditoría de las operaciones sobre los datos

### No incluido

- Control de acceso de **personas** (torniquetes, biometría). El sistema controla equipos, no personas.
- Inventario de activos del centro de formación. Los equipos registrados son propiedad de sus dueños.
- Integración con sistemas del SENA (Sofía Plus u otros).
- Aplicación móvil nativa. El escaneo se hace desde el navegador.

## 7. Usuarios del sistema

| Usuario | Rol en el sistema | Qué hace |
|---|---|---|
| Administrador del centro | `Administrador` | Registra usuarios y equipos, consulta reportes y auditoría |
| Personal de portería | `Seguridad` | Escanea los QR y registra ingresos y salidas |
| Aprendiz / instructor | `Usuario` | Consulta el historial de sus propios equipos |

## 8. Restricciones

| Tipo | Restricción |
|---|---|
| **Presupuesto** | El proyecto debe operar sobre servicios gratuitos |
| **Tiempo** | Ocho semanas, divididas en cuatro sprints |
| **Equipo** | Un solo desarrollador |
| **Conectividad** | La portería puede quedarse sin internet; el sistema debe poder ejecutarse localmente |
| **Hardware** | No se dispone de lectores QR dedicados; se usa la cámara de un teléfono o computador |

## 9. Justificación

Reemplazar la minuta por un registro digital reduce el tiempo de atención de **10 minutos a segundos**, elimina los errores de transcripción y hace que la trazabilidad — hoy teóricamente posible pero prácticamente inexistente — se vuelva una consulta de un clic.

El beneficio determinante no es la velocidad sino la **validación**: el sistema impide registrar una salida de un equipo que nunca ingresó, que es exactamente el escenario en el que hoy se pierde un bien sin que quede evidencia.
