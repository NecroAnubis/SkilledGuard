# Manual de usuario

**Sistema:** Skilled Guard — Control de ingreso de equipos tecnológicos

Este manual explica cómo usar el sistema según el rol asignado. No requiere conocimientos técnicos.

---

## 1. Qué hace el sistema

Reemplaza el cuaderno de portería donde se anotan a mano los equipos que entran y salen. Cada equipo lleva un **código QR** pegado; el guarda de seguridad lo escanea y el sistema registra el movimiento en segundos.

El sistema también **impide errores**: si alguien intenta registrar la salida de un equipo que nunca entró, lo rechaza y avisa.

## 2. Ingresar al sistema

1. Abrir el navegador en la dirección del sistema (por ejemplo `http://localhost:8000/docs`)
2. Buscar la sección **Autenticación** y luego `POST /auth/login`
3. Presionar **Try it out**
4. Escribir:
   - **username**: el número de documento
   - **password**: la contraseña
5. Presionar **Execute**

La respuesta trae un `access_token`. Copiarlo, presionar el botón **Authorize** en la parte superior de la página y pegarlo. Desde ahí el sistema reconoce quién es en cada operación.

> **La sesión dura una hora.** Al vencerse, las operaciones responden `401` y hay que volver a iniciar sesión.

> **Si escribe mal la contraseña**, el sistema responde *"Documento o contraseña incorrectos"* sin decir cuál de los dos falló. Es a propósito: evita que alguien averigüe qué documentos están registrados.

---

## 3. Rol Administrador

### 3.1 Registrar un usuario

`POST /usuarios`

| Campo | Ejemplo | Notas |
|---|---|---|
| nombres | María | |
| apellidos | Gómez | |
| id_tipo_documento | 1 | 1 = Cédula, 2 = Tarjeta de identidad, 3 = Cédula de extranjería |
| documento | 1002003002 | No puede repetirse |
| direccion | Calle 56 #45-21 | Opcional |
| contrasena | (mínimo 8 caracteres) | |

**Errores frecuentes**

| Mensaje | Qué significa |
|---|---|
| `409 Ya existe un usuario con documento…` | Ese documento ya está registrado |
| `422 La contraseña supera 72 bytes` | Contraseña demasiado larga. Las tildes y la ñ cuentan doble |
| `422` en el campo contraseña | Tiene menos de 8 caracteres |

### 3.2 Asignar un rol

Un usuario recién creado **no puede hacer nada** hasta que se le asigne un rol.

`POST /usuarios/{id}/roles`

| Rol | id | Para quién |
|---|---|---|
| Administrador | 1 | Coordinación del centro |
| Seguridad | 2 | Personal de portería |
| Usuario | 3 | Aprendices e instructores |

### 3.3 Registrar un equipo

`POST /dispositivos`

| Campo | Ejemplo |
|---|---|
| serial | PC-12345 |
| marca | Lenovo |
| modelo | ThinkPad L14 |
| sistema | Windows 11 |
| id_tipo_dispositivo | 1 (Computador), 2 (Celular), 3 (Tablet) |
| id_usuario | El id del dueño del equipo |

Al guardarlo, el sistema **genera automáticamente su código QR**.

### 3.4 Imprimir el código QR

`GET /dispositivos/{id}/qr`

Descarga una imagen PNG. **Imprimirla y pegarla en un lugar visible del equipo**, preferiblemente donde no se despegue ni se raye: la tapa del portátil o la parte trasera del dispositivo.

> Si una calcomanía se daña, se vuelve a descargar e imprimir la misma imagen. El código no cambia.

### 3.5 Consultar la auditoría

`GET /logs` — muestra quién creó o modificó cada dato, cuándo, y qué cambió exactamente.

Filtros disponibles:

| Filtro | Ejemplo |
|---|---|
| `id_usuario` | Ver todo lo que hizo una persona |
| `tabla` | `dispositivo`, `usuario`, `auditoria_negocio` |

Solo el Administrador tiene acceso.

---

## 4. Rol Seguridad

Es el rol que se usa en portería, y su operación es la más simple del sistema.

### 4.1 Registrar el ingreso de un equipo

1. Escanear el código QR pegado al equipo (con la cámara del teléfono o un lector)
2. Ir a `POST /movimientos`
3. Llenar:
   - **qr**: el código que arrojó el escaneo
   - **tipo**: `Ingreso`
   - **observacion**: opcional, por ejemplo *"Entra a clase de la tarde"*
4. **Execute**

El sistema confirma con los datos del equipo, su responsable y la hora.

### 4.2 Registrar la salida

Igual, pero con **tipo**: `Salida`.

### 4.3 Cuando el sistema rechaza el movimiento

| Mensaje | Qué pasó | Qué hacer |
|---|---|---|
| `El equipo ya se encuentra dentro de las instalaciones` | Se intentó registrar un ingreso de un equipo que ya está adentro | Verificar si el equipo salió sin registrarse. Registrar la salida faltante y luego el ingreso |
| `El equipo no ha registrado ingreso: no puede salir` | Se intentó registrar una salida de un equipo que nunca entró | **Verificar físicamente el equipo.** Puede que haya entrado sin registro, o que el equipo no sea de quien lo lleva |
| `El código QR no corresponde a un equipo` | El código no está registrado | Enviar a la persona con el administrador para registrar el equipo |

> ⚠️ El segundo mensaje es el más importante del sistema. Un equipo que "sale" sin haber entrado es exactamente la situación que la minuta en papel no detectaba.

### 4.4 Consultar el estado de un equipo

`GET /dispositivos/{id}/estado`

Responde `dentro` o `fuera`, y la fecha del último movimiento.

### 4.5 Consultar el historial

`GET /movimientos`

| Filtro | Para qué |
|---|---|
| `id_dispositivo` | Historial de un equipo específico |
| `id_usuario` | Todos los equipos de una persona |
| `tipo` | Solo ingresos o solo salidas |
| `desde` / `hasta` | Rango de fechas (formato `2026-08-08`) |

Los movimientos aparecen del más reciente al más antiguo.

### 4.6 Descargar reportes

| Formato | Ruta |
|---|---|
| Excel | `GET /reportes/movimientos.xlsx` |
| PDF | `GET /reportes/movimientos.pdf` |

Aceptan los mismos filtros del historial. Ejemplo — movimientos de agosto en Excel:

```
/reportes/movimientos.xlsx?desde=2026-08-01&hasta=2026-08-31
```

El archivo se descarga con la fecha y hora en el nombre.

---

## 5. Rol Usuario

Consultar los equipos propios: `GET /dispositivos`

---

## 6. Preguntas frecuentes

**¿Qué pasa si se pierde la calcomanía del QR?**
El administrador vuelve a descargar la imagen desde `GET /dispositivos/{id}/qr` y la imprime otra vez. Es el mismo código.

**¿Se puede usar el sistema sin internet?**
Sí. En su configuración local, el sistema y su base de datos corren en el mismo servidor del centro de formación.

**¿Por qué el QR no es simplemente el serial del equipo?**
El serial está impreso en el chasis, a la vista de cualquiera. El código QR es un identificador propio del sistema, que puede reemplazarse sin cambiar nada del inventario.

**¿Alguien puede borrar un movimiento registrado?**
No. El sistema no ofrece forma de eliminar movimientos: el historial es un registro, no una lista editable.

**¿Qué pasa si dos guardas de seguridad escanean el mismo equipo al mismo tiempo?**
El sistema registra un solo movimiento y rechaza el segundo. Está previsto.

**¿La contraseña se puede recuperar?**
No. Las contraseñas se guardan cifradas y no pueden leerse ni siquiera desde la base de datos. Si se olvida, el administrador debe registrar una nueva.

---

## 7. Glosario rápido

| Término | Significado |
|---|---|
| **Token** | Credencial temporal que identifica la sesión. Dura una hora |
| **QR** | Código impreso que identifica al equipo |
| **Movimiento** | Un ingreso o una salida |
| **Trazabilidad** | El historial completo de un equipo |
| **401** | Sesión vencida o no iniciada |
| **403** | No tiene permiso para esa operación |
| **404** | No se encontró lo solicitado |
| **409** | La operación contradice el estado actual |
| **422** | Los datos enviados no son válidos |
