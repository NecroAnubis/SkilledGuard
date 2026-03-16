# SkilledGuard – Frontend

Interfaz web del sistema de auditoría SkilledGuard. Este frontend consume la **API REST** del backend para login, gestión de usuarios, dispositivos, auditoría de negocio, reportes y logs.

**Stack:** HTML, CSS y JavaScript (vanilla). Sin framework; estructura clara y mantenible para entender y extender el proyecto.

---

## Tabla de contenidos

- [¿Qué debe hacer este frontend?](#qué-debe-hacer-este-frontend)
- [Requisitos previos](#requisitos-previos)
- [Estructura de carpetas recomendada](#estructura-de-carpetas-recomendada)
- [Guía de inicio paso a paso](#guía-de-inicio-paso-a-paso)
- [Integración con la API](#integración-con-la-api)
- [Pantallas y funcionalidades previstas](#pantallas-y-funcionalidades-previstas)
- [Recomendaciones HTML, CSS y JS](#recomendaciones-html-css-y-js)
- [Variables de entorno y configuración](#variables-de-entorno-y-configuración)
- [Referencias a la documentación](#referencias-a-la-documentación)

---

## ¿Qué debe hacer este frontend?

| Objetivo | Descripción |
|----------|-------------|
| **Interfaz web** | Permitir que usuarios y administradores usen el sistema de auditoría desde el navegador. |
| **Consumir la API** | Todas las operaciones de datos se hacen contra el backend (`CodigoBackend/Auditorias`). No hay lógica de negocio en el frontend. |
| **Autenticación** | Login con email y contraseña; guardar el token JWT y enviarlo en las peticiones que lo requieran. |
| **Según rol** | Mostrar u ocultar opciones según si el usuario es **Administrador** o **Usuario** (gestión de usuarios, reportes, etc.). |

La especificación completa está en la documentación del proyecto: [10_Frontend_Especificacion.md](../Documentacion/10_Frontend_Especificacion.md).

---

## Requisitos previos

| Requisito | Descripción |
|-----------|-------------|
| **Navegador moderno** | Chrome, Firefox, Edge o Safari actualizado (para `fetch`, ES6+, CSS Grid/Flexbox). |
| **Backend en ejecución** | La API debe estar corriendo para que el frontend pueda usarla. Ver [08_Guia_Desarrollo](../Documentacion/08_Guia_Desarrollo.md). |
| **Servidor local (recomendado)** | Para evitar problemas de CORS y de rutas, sirve la carpeta del frontend con un servidor (Live Server, `npx serve`, etc.). Ver [Guía de inicio](#guía-de-inicio-paso-a-paso). |

No es obligatorio tener Node.js para solo HTML/CSS/JS; si más adelante usas herramientas (bundler, linter), entonces sí.

---

## Estructura de carpetas recomendada

Organizar el código desde el principio facilita el crecimiento del proyecto. Propuesta para **HTML + CSS + JS**:

```
CodigoForntend/
├── index.html              # Punto de entrada (redirige a login o dashboard)
├── login.html              # Pantalla de login
├── css/
│   ├── reset.css           # (Opcional) Normalización de estilos
│   ├── variables.css       # Variables CSS (colores, fuentes, espaciado)
│   ├── layout.css          # Cabecera, menú, contenedor principal
│   ├── components.css      # Botones, cards, formularios, tablas
│   └── pages/
│       ├── login.css
│       ├── dashboard.css
│       ├── usuarios.css
│       └── ...
├── js/
│   ├── config.js           # URL base de la API (desde variable o constante)
│   ├── api.js              # Funciones que llaman a la API (fetch + token)
│   ├── auth.js             # Login, guardar/obtener token, logout, redirección
│   ├── router.js           # (Opcional) Cambio de “vistas” sin recargar
│   └── pages/
│       ├── login.js
│       ├── dashboard.js
│       ├── usuarios.js
│       └── ...
├── assets/                 # Imágenes, iconos, favicon
│   └── img/
├── .env.example            # Ejemplo de configuración (solo si usas build que lea .env)
├── README.md               # Este archivo
└── Documentacion/          # Enlace o copia de lo necesario (opcional)
```

- **HTML:** una página por pantalla principal (login, listado de usuarios, etc.) o una SPA ligera con un solo `index.html` y contenido inyectado por JS.
- **CSS:** separar variables, layout global y componentes reutilizables; por página solo lo específico.
- **JS:** un archivo de configuración, uno para la API (y token), uno para auth y luego un archivo por “pantalla” o módulo.

---

## Guía de inicio paso a paso

Sigue estos pasos para tener el frontend listo para trabajar y conectado a la API.

### Paso 1: Ubicación y servidor local

1. Abre la carpeta del proyecto en tu editor (por ejemplo, la raíz `SkilledGuard` o solo `CodigoForntend`).
2. La raíz del frontend es **`CodigoForntend/`** (junto a `CodigoBackend` y `Documentacion`).
3. Crea la estructura de carpetas anterior (al menos `css/`, `js/`, y si quieres `assets/img/`).

Para servir los archivos (recomendado):

- **Opción A – VS Code / Cursor:** instala la extensión **Live Server** y haz “Go Live” sobre `index.html` o la carpeta `CodigoForntend`. Suele usar `http://127.0.0.1:5500` o similar.
- **Opción B – Node.js:** desde `CodigoForntend` ejecuta:
  ```bash
  npx serve . -l 3000
  ```
  Abre `http://localhost:3000` en el navegador.
- **Opción C – Python:** `python -m http.server 8000` dentro de `CodigoForntend` y abre `http://localhost:8000`.

No abras directamente `file:///.../login.html`; es mejor usar siempre un origen `http://` para evitar restricciones con `fetch` y cookies.

### Paso 2: Configurar la URL de la API

1. Crea **`js/config.js`** con la URL base del backend (donde corre la API):

   ```javascript
   const API_BASE_URL = 'https://localhost:7xxx';  // Sustituir 7xxx por el puerto real (ej. 7000, 7045)
   ```

   Si más adelante usas variables de entorno (por ejemplo con un build), puedes leer desde ahí; por ahora una constante es suficiente.

2. Asegúrate de que el **backend** esté en ejecución y que esa URL sea la correcta (incluyendo `https` si tu API usa HTTPS). El puerto suele aparecer en la consola al levantar el proyecto ASP.NET Core.

### Paso 3: CORS

Si el frontend se sirve desde otro puerto u origen (por ejemplo `http://localhost:3000`) y la API en `https://localhost:7000`, el backend debe permitir ese origen en CORS. Está documentado en [09_Configuracion_Entornos](../Documentacion/09_Configuracion_Entornos.md). Si CORS no está bien configurado, el navegador bloqueará las peticiones.

### Paso 4: Primera página – Login

1. Crea **`login.html`** con un formulario: campo **email**, campo **contraseña** y botón “Iniciar sesión”.
2. Enlaza un CSS (por ejemplo `css/variables.css`, `css/components.css`, `css/pages/login.css`) y al final del `<body>` los scripts:
   - `js/config.js`
   - `js/api.js` (lo implementarás en el siguiente paso)
   - `js/auth.js`
   - `js/pages/login.js`
3. En **`js/api.js`** crea una función que haga `POST` a `API_BASE_URL + '/api/Auth/login'` con cuerpo:
   ```json
   { "email": "...", "contraseña": "..." }
   ```
   Devuelve la respuesta (o lanza si hay error).
4. En **`js/auth.js`** implementa:
   - Guardar el token (y opcionalmente el usuario) en `sessionStorage` o `localStorage` tras un login exitoso.
   - Función para obtener el token (para ponerlo en el header de las demás peticiones).
   - Función para cerrar sesión (borrar token y redirigir a `login.html`).
5. En **`js/pages/login.js`**:
   - Escucha el envío del formulario.
   - Llama a la función de login de la API con el email y la contraseña.
   - Si la respuesta es correcta, guarda token y usuario (usando `auth.js`) y redirige a la página principal (por ejemplo `index.html` o `dashboard.html`).
   - Si hay error (401 u otro), muestra un mensaje claro (“Credenciales incorrectas” o “Error de conexión”).

Con esto ya tienes el flujo de **login** funcionando y el token disponible para el resto de pantallas.

### Paso 5: Peticiones autenticadas

En **`js/api.js`** (o un módulo que uses para todas las llamadas):

- Crea una función auxiliar que haga `fetch` añadiendo el header:
  ```http
  Authorization: Bearer <token>
  ```
  El token lo obtienes de `auth.js`. Si no hay token, redirige a `login.html` y no hagas la petición.
- Si alguna petición devuelve **401**, considera que la sesión expiró: borra el token, muestra un mensaje si quieres y redirige a `login.html`.

Así todas las pantallas (usuarios, dispositivos, reportes, etc.) reutilizan la misma lógica de autenticación.

### Paso 6: Página principal y menú según rol

- Crea una página principal (por ejemplo **`index.html`** o **`dashboard.html`**) que solo se muestre si hay token (si no, redirigir a login).
- Incluye un menú o navegación con enlaces a:
  - Usuarios (si aplica por rol)
  - Dispositivos
  - Auditoría de negocio
  - Reportes
  - Cerrar sesión
- Usa el **rol** del usuario (guardado en auth) para mostrar u ocultar opciones (por ejemplo, gestión de usuarios solo para Administrador).

### Paso 7: Resto de pantallas

Implementa las demás pantallas de forma incremental, siempre usando la API:

- **Usuarios:** listar (GET `/api/Usuario`), ver detalle, crear, editar, eliminar, cambiar contraseña (endpoints en [06_API_Endpoints](../Documentacion/06_API_Endpoints.md)).
- **Dispositivos:** listar, crear, editar, eliminar (`/api/Dispositivo`).
- **Auditoría de negocio:** listar (`GET /api/AuditoriaNegocio`).
- **Reportes:** listar, ver detalle, crear (`/api/Reportes`).
- **Catálogos:** según necesites en formularios (roles, tipos de documento, tipos de dispositivo, sedes, etc.).

Cada pantalla puede ser un HTML propio (por ejemplo `usuarios.html`) con su CSS y JS, o un único `index.html` que cargue distintos “bloques” según la ruta o el menú.

---

## Integración con la API

Resumen de lo que debe cumplir el frontend:

| Aspecto | Requisito |
|---------|-----------|
| **URL base** | Configurable (constante en `config.js` o variable de entorno). Ejemplo: `https://localhost:7xxx`. |
| **Login** | `POST /api/Auth/login` con cuerpo `{ "email": "...", "contraseña": "..." }`. Respuesta: `token` y `usuario`. |
| **Peticiones autenticadas** | Header `Authorization: Bearer <token>` en todas las peticiones que lo requieran. |
| **Almacenamiento del token** | `sessionStorage` o `localStorage`; ante 401, cerrar sesión y redirigir a login. |
| **Endpoints** | Listado completo en [06_API_Endpoints](../Documentacion/06_API_Endpoints.md). |

No hardcodear la URL de la API en cada archivo; usar siempre `config.js` (o equivalente) para un solo punto de configuración.

---

## Pantallas y funcionalidades previstas

Checklist para implementación (detalle en [10_Frontend_Especificacion](../Documentacion/10_Frontend_Especificacion.md)):

| Área | Funcionalidad |
|------|----------------|
| **Login** | Formulario email/contraseña → `POST /api/Auth/login` → guardar token y usuario → redirigir. |
| **Usuarios** | Listar, ver, crear, editar, eliminar, cambiar contraseña (según permisos). |
| **Dispositivos** | Listar, ver, crear, editar, eliminar. |
| **Auditoría de negocio** | Listar registros. |
| **Reportes** | Listar, ver detalle, crear. |
| **Catálogos** | Roles, tipos de documento, tipos de dispositivo, tipos de registro, tipos de reporte, sedes (según formularios). |
| **Logs** | Consulta por id cuando la API lo exponga. |

Puedes seguir el orden: Login → Dashboard → Usuarios → Dispositivos → Auditoría → Reportes.

---

## Recomendaciones HTML, CSS y JS

### HTML

- Usar **HTML5 semántico:** `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<footer>`.
- Formularios: `label` asociado a cada `input` (por `for`/`id`), `type="email"` y `type="password"` donde corresponda, y `button type="submit"` para enviar.
- Dar **ids** o **data-*** estables a los elementos que vayas a usar desde JS (contenedores de listas, mensajes de error, etc.) para no acoplar demasiado el JS a clases solo de estilo.

### CSS

- **Variables CSS** en `:root` (colores, fuentes, espaciado) en `variables.css` para mantener consistencia y temas futuros.
- **Metodología:** BEM o bloques claros (por ejemplo `.card`, `.card__title`, `.card--highlight`) para evitar conflictos entre páginas.
- **Mobile first:** diseña primero para pantalla pequeña y luego con `min-width` en media queries para tablet y escritorio.
- **Un archivo de reset o normalización** (por ejemplo `reset.css` o Normalize.css) para homogeneizar estilos entre navegadores.
- **Un archivo de layout** común (cabecera, menú, contenedor principal) y archivos por página solo para lo específico.

### JavaScript

- **Un punto de configuración:** `config.js` con `API_BASE_URL` (y más adelante otras constantes).
- **Un módulo de API:** en `api.js` concentrar todas las llamadas `fetch` y la lógica de añadir el token y manejar 401.
- **Auth separado:** en `auth.js` solo lógica de login/logout, guardar/obtener token y usuario.
- **Manejo de errores:** mostrar mensajes claros al usuario (credenciales incorrectas, error de red, servidor no disponible).
- **Evitar repetir código:** funciones reutilizables para “GET con token”, “POST con token”, etc., en `api.js`.

Si más adelante quieres usar módulos ES6 (`import`/`export`), sirve los archivos con un servidor que soporte módulos (Live Server, `serve`, etc.) y usa `<script type="module" src="js/...">`.

---

## Variables de entorno y configuración

Con HTML/CSS/JS puro no hay proceso de build que lea `.env`. Puedes:

- Mantener la URL de la API en **`js/config.js`** como constante y cambiarla según entorno (desarrollo/producción) a mano o con un script de copia.
- Si en el futuro usas un build (por ejemplo con Node), puedes definir un `.env.example` con algo como:
  ```env
  API_BASE_URL=https://localhost:7xxx
  ```
  y que el build inyecte el valor en `config.js`.

Para desarrollo, suele bastar con editar `API_BASE_URL` en `config.js` y asegurarse de que el backend esté en ese puerto.

---

## Referencias a la documentación

| Documento | Contenido |
|-----------|-----------|
| [README principal](../README.md) | Visión del proyecto, tecnologías, arquitectura. |
| [10_Frontend_Especificacion](../Documentacion/10_Frontend_Especificacion.md) | Especificación completa del frontend y checklist. |
| [11_Frontend_Guia_Instalacion](../Documentacion/11_Frontend_Guia_Instalacion.md) | Instalación y ejecución (útil si añades Node/build). |
| [06_API_Endpoints](../Documentacion/06_API_Endpoints.md) | Listado de endpoints de la API. |
| [04_Arquitectura_Sistema](../Documentacion/04_Arquitectura_Sistema.md) | Flujo JWT y capas del backend. |
| [09_Configuracion_Entornos](../Documentacion/09_Configuracion_Entornos.md) | CORS y configuración por entorno. |

---

## Resumen rápido: por dónde empezar

1. Crear la estructura de carpetas (`css/`, `js/`, `assets/`).
2. Crear `js/config.js` con la URL del backend.
3. Implementar `js/api.js` (login y luego peticiones con token) y `js/auth.js` (guardar/obtener token, logout).
4. Crear `login.html` y `js/pages/login.js` y probar el login contra la API.
5. Crear la página principal (dashboard) con menú y protección por token.
6. Ir añadiendo pantallas (usuarios, dispositivos, auditoría, reportes) usando siempre la API y el token.

Si sigues esta guía y la documentación enlazada, tendrás una base clara y ordenada para desarrollar el frontend en HTML, CSS y JavaScript.
