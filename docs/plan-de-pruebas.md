# Plan de pruebas de software

**Proyecto:** Skilled Guard — Sistema de Automatización para el Control de Ingreso de Equipos Tecnológicos (SENA)
**Repo:** https://github.com/MrOlaya666/SkilledGuard
**Fecha:** 2026-08-07

---

## Historial de versiones

| Fecha | Versión | Autor | Organización | Descripción |
|---|---|---|---|---|
| 2026-08-07 | 0.1 | Johan Salas | — | Primer borrador, basado en el README y el código actual del repo |

## Información del proyecto

| Campo | Valor |
|---|---|
| Empresa / Organización | SENA — Análisis y Desarrollo de Software (ADSO) |
| Proyecto | Skilled Guard |
| Fecha de preparación | 2026-08-07 |
| Cliente | Portería / administración del centro SENA |
| Patrocinador principal | *(instructor del programa, no está en el repo)* |
| Gerente / Líder de proyecto | MrOlaya666 — titular actual del repositorio |
| Gerente / Líder de pruebas de software | Johan Salas (`NecroAnubis`) — autor original del repo, cedido a MrOlaya666 |

> El README todavía apunta al origen anterior (`git clone .../NecroAnubis/SkilledGuard.git`); el repositorio vive hoy en `MrOlaya666/SkilledGuard`. Corregir esa URL es un pendiente de documentación.

## Aprobaciones

| Nombre y Apellido | Cargo | Departamento u organización | Fecha | Firma |
|---|---|---|---|---|
| MrOlaya666 | Titular del repositorio / desarrollo | Grupo ADSO — SENA | | |
| Johan Salas | Autor original / pruebas | Grupo ADSO — SENA | | |
| *(instructor)* | Instructor del programa | SENA | | |

---

## Resumen ejecutivo

Skilled Guard reemplaza el registro manual en minutas del ingreso/salida de equipos tecnológicos por un sistema digital. Problema que ataca, según el README: registro lento (~10 min por usuario), pérdida de trazabilidad, riesgo de fraude o pérdida de bienes. Solución: registro digital de usuarios y equipos + validación en portería por código QR.

Este es un **plan detallado**, no maestro — el proyecto está en etapa temprana, así que el alcance real de pruebas hoy es acotado:

| | Estado (según README) |
|---|---|
| Backend en .NET 9 / ASP.NET Core | ✅ iniciado |
| Arquitectura base | ✅ |
| Compilación y ejecución local | ✅ |
| Base de datos configurada | ❌ pendiente |
| Frontend | ❌ sin desarrollar |
| Módulo QR | ❌ pendiente |

De ~14 entidades modeladas en la base de datos, **solo una tiene endpoint implementado** (`TipoAccion`, solo `GET`). El resto del alcance descrito abajo es mayormente backlog, no funcionalidad probable hoy.

---

## Alcance de las pruebas

### Elementos de pruebas
- Esquema de base de datos (`Base_de_Datos/DDL base de datos.sql`, `DML base de datos.sql`) — SQL Server.
- API `Auditorias` (.NET 9 / ASP.NET Core + EF Core): único endpoint implementado — `GET /api/tipoaccion`.
- Modelos definidos sin controlador aún: `Usuario`, `Rol`, `UsuarioRol`, `Dispositivo`, `TipoDispositivo`, `TipoDocumento`, `TipoRegistro`, `AuditoriaNegocio`, `LogSistema`, `LogDetalle`, `Reporte`, `TipoReporte`, `ConsultaReporte`, `ObjetoAfectado`.

### Nuevas funcionalidades a probar (roadmap declarado en el README, aún no implementadas)
- Registro de usuarios con roles (Administrador / Seguridad / Usuario).
- Registro de equipos (serial, marca, modelo, descripción).
- Validación en portería mediante código QR.
- Trazabilidad completa de entradas y salidas.
- Generación de reportes (PDF / Excel).
- Autenticación y autorización JWT + Roles.

### Pruebas de regresión
No aplica todavía — no hay una versión previa en producción sobre la cual regresar.

### Funcionalidades a no probar
No hay nada declarado explícitamente fuera de alcance en el repo. No existen hoy frontend ni app móvil que probar.

### Enfoque de pruebas (estrategia)
- **Pruebas de esquema de BD:** ejecutar el DDL/DML en un entorno SQL Server limpio y validar que corre sin errores, que las FKs son consistentes y que los tipos de dato son válidos.
- **Pruebas de API:** por endpoint, contra Swagger/Postman (herramientas que el propio README declara como plan de pruebas).
- **Pruebas unitarias .NET** (xUnit/NUnit) para lógica de controllers a medida que se agreguen.
- **Pruebas funcionales de QR** una vez esté implementado el módulo.
- **Pruebas de seguridad** de JWT + Roles una vez esté implementada la autenticación (los 3 roles del README deben tener permisos diferenciados).

---

## Criterios de aceptación o rechazo

### Criterios de aceptación o rechazo
- El script DDL debe ejecutar sin errores en SQL Server. **Hoy no cumple** — ver hallazgo abajo.
- Cada endpoint implementado responde 200 en su caso feliz y está documentado en Swagger.
- Los reportes generados (cuando existan) corresponden a los filtros aplicados.

### Criterios de suspensión
- La base de datos no está configurada/accesible en el entorno de pruebas (hoy es el caso, según el README).
- El backend no compila.

### Criterios de reanudación
- BD configurada y accesible; backend compila y levanta localmente.

---

## Hallazgo encontrado al revisar el repo

🔴 **El DDL no es válido tal como está.** Las 14 tablas declaran la columna `id` como `INT uniqueidentifier PRIMARY KEY` (`Base_de_Datos/DDL base de datos.sql`) — `INT` y `UNIQUEIDENTIFIER` son tipos incompatibles en SQL Server; ese script fallaría al ejecutarse. Esto bloquea cualquier prueba de integración o de API que dependa de la base de datos hasta que se corrija (elegir uno de los dos tipos, consistente con cómo los IDs se referencian en el resto del DDL y en el DML).

---

## Entregables
- Este documento.
- Reporte del hallazgo sobre el DDL (arriba).
- Casos de prueba para `TipoAccionController`.
- Checklist de endpoints pendientes vs. funcionalidades declaradas en el README.

---

## Recursos

### Requerimientos de entornos – Hardware
Máquina de desarrollo estándar con .NET 9 SDK y acceso a una instancia de SQL Server (local o de prueba).

### Requerimientos de entornos – Software
- .NET 9 / ASP.NET Core Web API
- Entity Framework Core (paquetes ya declarados en `CódigoBackend/Dependencias.txt`: `Microsoft.EntityFrameworkCore`, `.SqlServer`, `.Tools`, `Swashbuckle.AspNetCore`)
- SQL Server
- Swagger (ya integrado vía Swashbuckle) + Postman

### Herramientas de pruebas requeridas
- Postman + Swagger (declaradas en el README como el plan de pruebas del proyecto).
- Framework de pruebas unitarias .NET (xUnit, por convención del ecosistema — no está en el repo todavía).

### Personal
- 1 tester — Johan Salas (`NecroAnubis`), autor original del proyecto: conoce el modelo de datos de primera mano.
- MrOlaya666 como titular actual del repo, para acordar correcciones y merges.

### Entrenamiento
Familiarización con Entity Framework Core y con el modelo de datos de auditoría (`AuditoriaContext`).

---

## Planificación y organización

### Procedimientos para las pruebas
1. Ejecutar DDL + DML en un entorno limpio (corregir el hallazgo del tipo de dato primero).
2. Levantar el backend localmente y validar Swagger.
3. Probar `GET /api/tipoaccion` contra los datos del DML.
4. Repetir para cada controlador nuevo a medida que se implemente.

### Matriz de responsabilidades

| Actividad | Responsable | Aprobador | Consultado | Informado |
|---|---|---|---|---|
| Diseño y corrección del esquema de BD | Johan Salas | MrOlaya666 | — | Grupo |
| Ejecución de pruebas (API, BD) | Johan Salas | MrOlaya666 | — | Instructor |
| Desarrollo de controladores pendientes | MrOlaya666 | — | Johan Salas | Grupo |
| Aceptación final del plan | — | Instructor | MrOlaya666, Johan Salas | Grupo |

*Los demás integrantes del grupo no están identificados en el repo — completar antes de firmar.*

### Cronograma
Atado al roadmap declarado en el README: BD configurada → resto de controladores → frontend → módulo QR → reportes. Sin fechas comprometidas en el repo; deben acordarse con el instructor según el calendario de la formación.

### Premisas
El repo sigue evolucionando según el roadmap declarado; las funcionalidades "planeadas" del README no tienen fecha comprometida.

### Dependencias y riesgos
- 🔴 **Bloqueante:** el DDL no ejecuta tal cual (ver hallazgo). Ninguna prueba contra base de datos real es posible hasta corregirlo.
- 🟡 Solo 1 de 14 entidades modeladas tiene endpoint — la mayoría del alcance funcional del README es backlog, no superficie probable hoy.
- Dependencia: disponibilidad de una instancia de SQL Server para pruebas.

---

## Referencias
- README del repo: https://github.com/MrOlaya666/SkilledGuard
- `Base_de_Datos/DDL base de datos.sql`, `Base_de_Datos/DML base de datos.sql`
- `CódigoBackend/Auditorias/Controllers/TipoAccionController.cs`

## Glosario
- **QR:** código de respuesta rápida, usado para validación de equipos en portería.
- **JWT:** JSON Web Token, mecanismo de autenticación planeado.
- **DDL / DML:** Data Definition / Data Manipulation Language (SQL).
- **Minuta:** registro manual en papel que el proyecto reemplaza.
