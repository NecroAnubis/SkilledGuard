# Glosario

Términos técnicos y del negocio usados en la documentación y el código del proyecto.

---

## Problema N+1

Un patrón de consulta ineficiente: para traer una lista de N elementos se ejecuta **una** consulta inicial, y luego **una consulta adicional por cada elemento** para completar sus datos relacionados. De ahí el nombre: 1 + N consultas.

**Ejemplo real de este proyecto.** El listado de movimientos de portería trae 50 registros. Al mostrar cada uno se necesita el equipo, el responsable del equipo, el vigilante y el tipo de movimiento — cuatro datos que viven en otras tablas:

| Enfoque | Consultas |
|---|---|
| Ingenuo (N+1) | 1 + (50 × 4) = **201** |
| Con carga anticipada | **1** |

La aplicación *parece* funcionar: los datos salen correctos. Por eso el N+1 es traicionero — no falla, solo se vuelve lento. Con 10 registros de prueba nadie lo nota; con 10.000 movimientos reales la pantalla tarda medio minuto.

**Cómo se resolvió aquí.** Con `joinedload` de SQLAlchemy (`app/consultas.py`), que le dice al ORM que traiga las tablas relacionadas en la misma consulta mediante un JOIN. La prueba `test_la_consulta_no_dispara_una_avalancha_de_queries` cuenta las consultas ejecutadas y falla si vuelven a ser más de una.

---

## Términos técnicos

**API REST** — Interfaz que permite a otros programas usar el sistema mediante peticiones HTTP (`GET`, `POST`, …), sin pasar por una pantalla.

**Alembic** — Herramienta que versiona los cambios del esquema de la base de datos. Cada cambio queda como un archivo con instrucciones para aplicarlo (`upgrade`) y para revertirlo (`downgrade`).

**bcrypt** — Algoritmo para almacenar contraseñas. Aplica un cálculo deliberadamente lento y agrega un valor aleatorio (*salt*) a cada una, de modo que dos usuarios con la misma contraseña producen resultados distintos y probar millones de combinaciones resulta costoso.

**CI (Integración Continua)** — Ejecución automática de pruebas y revisiones cada vez que se sube código. Aquí corre en GitHub Actions.

**Docker** — Empaqueta la aplicación con todo lo que necesita para funcionar, de modo que se ejecuta igual en cualquier computador.

**docker-compose** — Coordina varios contenedores a la vez. En este proyecto levanta la base de datos y la API con un solo comando.

**Endpoint** — Una dirección concreta de la API que hace algo específico. Ejemplo: `POST /movimientos` registra un ingreso o una salida.

**FastAPI** — Framework de Python para construir APIs. Genera la documentación interactiva (Swagger) automáticamente a partir del código.

**Hash** — Resultado de transformar un texto en una cadena de longitud fija mediante un proceso que no puede revertirse. Permite verificar una contraseña sin almacenarla.

**JWT (JSON Web Token)** — Credencial firmada que el sistema entrega al iniciar sesión. El usuario la envía en cada petición siguiente para demostrar quién es, sin repetir la contraseña.

**Migración** — Un cambio versionado del esquema de la base de datos (crear una tabla, agregar una columna).

**ORM (Mapeo Objeto-Relacional)** — Capa que representa las tablas de la base de datos como clases de Python. Aquí es SQLAlchemy.

**Paginación** — Entregar los resultados por bloques (`limite`, `desplazamiento`) en lugar de todos a la vez.

**PBKDF2** — Otro algoritmo de derivación de contraseñas, usado en la versión anterior del proyecto en C#.

**pytest** — Herramienta con la que se escriben y ejecutan las pruebas automatizadas.

**QR (Quick Response)** — Código de barras bidimensional. Aquí se imprime y se pega en cada equipo para identificarlo en portería.

**Seed (datos semilla)** — Datos mínimos que el sistema necesita para arrancar: roles, tipos de documento y el primer administrador.

**SQLAlchemy** — El ORM que usa el proyecto.

**Swagger / OpenAPI** — Documentación interactiva de la API, generada automáticamente. Disponible en `/docs`.

**Token** — Cadena que identifica algo de forma única. En este proyecto hay dos: el JWT de sesión y el código aleatorio que lleva el QR de cada equipo.

---

## Términos del negocio

**Auditoría de negocio** — El registro de movimientos de equipos por portería. Es el reemplazo digital de la minuta.

**Log del sistema** — El registro de cambios sobre los *datos*: quién creó un usuario, quién modificó un equipo. Distinto de la auditoría de negocio.

**Minuta** — El cuaderno en papel donde hoy se anota manualmente la entrada y salida de equipos. Es lo que este proyecto reemplaza.

**Movimiento** — Un ingreso o una salida de un equipo.

**Portería** — El punto de control físico donde se validan los equipos al entrar y salir.

**Trazabilidad** — Poder reconstruir el historial completo de un equipo: cuándo entró, cuándo salió y quién lo registró cada vez.

---

## Roles del sistema

| Rol | Qué puede hacer |
|---|---|
| **Administrador** | Todo: usuarios, roles, equipos, reportes y consulta del rastro de auditoría |
| **Seguridad** | Registrar ingresos y salidas, consultar equipos y generar reportes |
| **Usuario** | Consultar sus propios equipos |

---

## Metodología

**Scrum** — Marco de trabajo que divide el proyecto en ciclos cortos (*sprints*) con un entregable funcional al final de cada uno.

**Sprint** — Ciclo de trabajo. En este proyecto dura dos semanas.

**Product Backlog** — Lista priorizada de todo lo que falta por construir.

**Definition of Done** — Las condiciones que debe cumplir una tarea para considerarse terminada. Aquí: entra por Pull Request, con pruebas, CI en verde, documentada en Swagger y con su migración versionada.

**Pull Request (PR)** — Propuesta de cambio que se revisa antes de integrarse a la rama principal.
