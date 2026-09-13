# Requerimientos del sistema

**Proyecto:** Skilled Guard
**Autor:** Johan S. Restrepo

Cada requerimiento indica el sprint en que se implementó y cómo se verifica. Los que dicen "prueba automatizada" tienen una prueba que falla si el requerimiento deja de cumplirse.

---

## Requerimientos funcionales

### Gestión de usuarios y acceso

| ID | Requerimiento | Sprint | Verificación |
|---|---|---|---|
| RF-01 | El sistema debe permitir registrar usuarios con nombres, apellidos, tipo y número de documento | 1 | `test_crear_usuario` |
| RF-02 | El número de documento debe ser único | 1 | `test_documento_duplicado_da_409` |
| RF-03 | Las contraseñas deben almacenarse cifradas, nunca en texto plano | 1 | `test_la_contrasena_se_guarda_hasheada` |
| RF-04 | El sistema debe autenticar al usuario por documento y contraseña, entregando un token de sesión | 1 | `test_login_correcto_devuelve_token` |
| RF-05 | El sistema debe manejar tres roles: Administrador, Seguridad y Usuario | 1 | `test_yo_devuelve_los_roles` |
| RF-06 | Cada operación debe restringirse a los roles autorizados | 1 | `test_usuario_sin_rol_admin_no_puede_listar` |

### Gestión de equipos

| ID | Requerimiento | Sprint | Verificación |
|---|---|---|---|
| RF-07 | El sistema debe permitir registrar equipos con serial, marca, modelo, sistema operativo, tipo y responsable | 2 | `test_crear_dispositivo_genera_su_codigo_qr` |
| RF-08 | El serial de cada equipo debe ser único | 2 | `test_serial_duplicado_da_409` |
| RF-09 | El sistema debe generar un código QR único por equipo al registrarlo | 2 | `test_dos_equipos_no_comparten_codigo_qr` |
| RF-10 | El código QR debe poder descargarse como imagen para imprimir | 2 | `test_el_endpoint_de_qr_devuelve_una_imagen_png` |
| RF-11 | El sistema debe indicar si un equipo está dentro o fuera de las instalaciones | 2 | `test_estado_inicial_del_equipo_es_fuera` |

### Control de ingreso

| ID | Requerimiento | Sprint | Verificación |
|---|---|---|---|
| RF-12 | El personal de seguridad debe poder registrar el ingreso de un equipo escaneando su QR | 2 | `test_registrar_ingreso_por_qr` |
| RF-13 | El personal de seguridad debe poder registrar la salida de un equipo | 2 | `test_ciclo_completo_ingreso_salida_ingreso` |
| RF-14 | **El sistema debe impedir el ingreso de un equipo que ya está dentro** | 2 | `test_no_permite_dos_ingresos_seguidos` |
| RF-15 | **El sistema debe impedir la salida de un equipo que no ha ingresado** | 2 | `test_no_permite_salir_sin_haber_ingresado` |
| RF-16 | Un código QR no registrado debe ser rechazado | 2 | `test_qr_desconocido_da_404` |
| RF-17 | Cada movimiento debe quedar asociado al guarda de seguridad que lo registró | 2 | `test_registrar_ingreso_por_qr` |

> **RF-14 y RF-15 son el núcleo del sistema.** Son la diferencia entre una minuta digital y un control real: sin ellas el registro acepta cualquier cosa, igual que el papel.

### Trazabilidad y reportes

| ID | Requerimiento | Sprint | Verificación |
|---|---|---|---|
| RF-18 | El sistema debe listar el historial de movimientos, del más reciente al más antiguo | 2 | `test_la_trazabilidad_lista_del_mas_reciente_al_mas_antiguo` |
| RF-19 | El historial debe poder filtrarse por equipo, responsable, tipo y rango de fechas | 3 | `test_la_trazabilidad_se_filtra_por_equipo` |
| RF-20 | El sistema debe exportar el historial a Excel | 3 | `test_reporte_excel_contiene_los_movimientos` |
| RF-21 | El sistema debe exportar el historial a PDF | 3 | `test_reporte_pdf_es_un_pdf_valido` |
| RF-22 | Los reportes deben respetar los mismos filtros del listado | 3 | `test_el_reporte_respeta_el_filtro_por_tipo` |

### Auditoría

| ID | Requerimiento | Sprint | Verificación |
|---|---|---|---|
| RF-23 | El sistema debe registrar quién creó o modificó cada dato, y cuándo | 3 | `test_crear_un_equipo_deja_rastro` |
| RF-24 | El rastro debe incluir el detalle de los campos afectados | 3 | `test_crear_un_equipo_deja_rastro` |
| RF-25 | Solo el Administrador puede consultar el rastro de auditoría | 3 | `test_el_rastro_solo_lo_ve_el_administrador` |
| RF-26 | Una operación rechazada no debe dejar rastro como si hubiera ocurrido | 3 | `test_una_operacion_fallida_no_deja_rastro` |

---

## Requerimientos no funcionales

### Seguridad

| ID | Requerimiento | Verificación |
|---|---|---|
| RNF-01 | Las contraseñas deben almacenarse con un algoritmo de hash lento y con salt (bcrypt) | `test_la_contrasena_se_guarda_hasheada` |
| RNF-02 | El sistema debe rechazar tokens manipulados, mal firmados o malformados | `test_token_malformado_da_401_y_no_500` |
| RNF-03 | El sistema debe rechazar tokens con algoritmo `none` | `test_token_con_algoritmo_none_es_rechazado` |
| RNF-04 | Los mensajes de error de autenticación no deben revelar si un documento existe | `test_login_de_usuario_inexistente_da_el_mismo_error` |
| RNF-05 | Las contraseñas nunca deben aparecer en las respuestas de la API | `test_la_respuesta_nunca_expone_la_contrasena` |
| RNF-06 | Las contraseñas nunca deben quedar registradas en el rastro de auditoría | `test_el_rastro_nunca_guarda_la_contrasena` |
| RNF-07 | Los parámetros de consulta no deben permitir inyección SQL | `test_los_filtros_no_permiten_inyeccion_sql` |
| RNF-08 | El secreto de firma de tokens no debe estar en el repositorio | El arranque falla si no se define `JWT_SECRET` |
| RNF-09 | La contraseña debe rechazarse si supera el límite real del algoritmo (72 bytes) | `test_contrasena_de_mas_de_72_bytes_es_rechazada` |
| RNF-10 | 🔜 El sistema debe limitar los intentos de inicio de sesión | Pendiente — requiere infraestructura adicional |

### Integridad de datos

| ID | Requerimiento | Verificación |
|---|---|---|
| RNF-11 | Dos peticiones simultáneas del mismo equipo no deben duplicar un movimiento | `test_dos_ingresos_simultaneos_solo_registran_uno` |
| RNF-12 | Los catálogos no deben admitir nombres duplicados | `test_no_permite_catalogos_duplicados` |
| RNF-13 | Todo cambio del esquema debe quedar versionado y ser reversible | Migraciones Alembic, probadas en ciclo `upgrade`/`downgrade` |

### Rendimiento

| ID | Requerimiento | Verificación |
|---|---|---|
| RNF-14 | Las consultas de listado no deben incurrir en el problema N+1 | `test_la_consulta_no_dispara_una_avalancha_de_queries` |
| RNF-15 | Los listados deben paginarse, con un tope máximo por petición | `test_el_limite_de_paginacion_esta_acotado` |
| RNF-16 | Los reportes deben tener un tope de filas | Constante `MAXIMO_FILAS` en `app/routers/reportes.py` |

### Disponibilidad y despliegue

| ID | Requerimiento | Verificación |
|---|---|---|
| RNF-17 | El sistema debe levantarse con un solo comando | `docker compose up` |
| RNF-18 | La API debe esperar a que la base de datos esté lista antes de arrancar | `depends_on: service_healthy` |
| RNF-19 | El sistema debe reportar su estado de salud, incluida la conexión a la base | `test_salud_reporta_el_estado_de_la_base` |
| RNF-20 | El sistema debe poder ejecutarse sin internet, para no depender de la conectividad de la portería | Postgres local en `docker-compose.yml` |

### Mantenibilidad

| ID | Requerimiento | Verificación |
|---|---|---|
| RNF-21 | Todo cambio debe pasar por integración continua antes de integrarse | GitHub Actions en cada Pull Request |
| RNF-22 | El código debe cumplir un estándar de estilo verificado automáticamente | `ruff check` y `ruff format --check` en CI |
| RNF-23 | La API debe estar documentada de forma interactiva | Swagger en `/docs`, generado desde el código |
| RNF-24 | Las reglas de negocio deben poder probarse sin levantar la API | `app/porteria.py`, probado en `tests/test_porteria.py` |

### Usabilidad

| ID | Requerimiento |
|---|---|
| RNF-25 | El registro de un movimiento debe requerir un escaneo y una sola acción más |
| RNF-26 | Los mensajes de error deben explicar la causa en lenguaje comprensible ("El equipo ya se encuentra dentro de las instalaciones") |
| RNF-27 | El sistema debe operar desde el navegador, sin instalar aplicaciones |

---

## Resumen de cobertura

| | Cantidad | Con prueba automatizada |
|---|---|---|
| Requerimientos funcionales | 26 | 26 |
| Requerimientos no funcionales | 27 | 19 |

Los no funcionales sin prueba automatizada son de despliegue, usabilidad o documentación: se verifican por inspección, no por código. La única excepción es **RNF-10 (límite de intentos de login)**, que está pendiente de implementación.
