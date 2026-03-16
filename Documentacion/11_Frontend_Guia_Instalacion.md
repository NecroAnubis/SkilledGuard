# 11 – Frontend: guía de instalación y ejecución

**Proyecto:** SkilledGuard  
**Documento:** Guía de instalación, variables de entorno y build del frontend  
**Referencia:** [10_Frontend_Especificacion](10_Frontend_Especificacion.md). Cuando el frontend esté implementado, completar este documento con los comandos y pasos reales del proyecto.

---

## 1. Estado actual

El frontend en **CodigoForntend** **aún no está implementado**. Esta guía describe los pasos genéricos que se seguirán cuando exista la aplicación y debe **actualizarse** con los comandos y nombres exactos del stack elegido (ver [10_Frontend_Especificacion](10_Frontend_Especificacion.md)).

---

## 2. Requisitos previos

| Requisito | Descripción |
|-----------|-------------|
| **Node.js** | Versión LTS recomendada (p. ej. 18.x o 20.x). Comprobar con `node --version`. |
| **npm** o **yarn** | Incluidos con Node.js (`npm --version`, `yarn --version`). |
| **Backend en ejecución** | La API debe estar corriendo para que el frontend pueda consumirla (ver [08_Guia_Desarrollo](08_Guia_Desarrollo.md)). En desarrollo suele ser `https://localhost:7xxx` o similar. |

---

## 3. Ubicación del proyecto frontend

- Carpeta: **`CodigoForntend/`** (en la raíz del repositorio, junto a `CodigoBackend` y `Base_de_Datos`).
- Desde la raíz del repositorio: `cd CodigoForntend` (o abrir la carpeta en el IDE).

---

## 4. Instalación de dependencias

Cuando exista un `package.json` en `CodigoForntend/`:

**Con npm:**

```bash
cd CodigoForntend
npm install
```

**Con yarn:**

```bash
cd CodigoForntend
yarn install
```

**Con pnpm (si se usa):**

```bash
cd CodigoForntend
pnpm install
```

*Actualizar esta sección con el gestor de paquetes real del proyecto.*

---

## 5. Variables de entorno

El frontend debe conocer la **URL base de la API** (y, si aplica, otras configuraciones). Se recomienda usar un archivo de entorno que no se versiona y un ejemplo que sí se versione.

**Archivo de ejemplo (versionado):** `CodigoForntend/.env.example`

```env
# URL base de la API (sin barra final)
# Desarrollo: URL donde corre el backend (ej. https://localhost:7xxx)
VITE_API_BASE_URL=https://localhost:7xxx
```

*Nota: con Vite el prefijo es `VITE_`; con Create React App es `REACT_APP_`; con Angular suelen usarse `environment.ts` y `environment.prod.ts`. Ajustar según el stack.*

**Archivo real (no versionar):** `CodigoForntend/.env`

- Copiar `.env.example` a `.env` y cambiar los valores según el entorno local.
- Añadir `.env` al `.gitignore` si no está ya.

**Uso en código:** leer la variable en el cliente HTTP (ej. `import.meta.env.VITE_API_BASE_URL` en Vite) para construir la URL base de las peticiones.

---

## 6. Ejecutar en modo desarrollo

Tras instalar dependencias y configurar `.env`, arrancar el servidor de desarrollo. Los comandos típicos (a sustituir por los del proyecto cuando exista):

| Stack (ejemplo) | Comando típico |
|-----------------|----------------|
| Vite (React/Vue) | `npm run dev` |
| Create React App | `npm start` |
| Angular | `ng serve` o `npm start` |
| Vue CLI | `npm run serve` |

Ejemplo genérico:

```bash
cd CodigoForntend
npm run dev
```

El terminal mostrará la URL local (p. ej. `http://localhost:5173`). Abrirla en el navegador. Asegurarse de que el backend está en ejecución y de que la URL de la API en `.env` es correcta.

*Actualizar con el comando real del `package.json`.*

---

## 7. Build de producción

Para generar los archivos estáticos que se desplegarán en un servidor web o CDN:

**Comando típico:**

```bash
cd CodigoForntend
npm run build
```

La salida suele quedar en una carpeta como `dist/` o `build/`. El contenido de esa carpeta es el que se sirve en producción.

**Variables de entorno en producción:** configurar la URL de la API del entorno de producción (variables del host, archivo `.env.production` o similar según el stack). No usar la URL de localhost en producción.

*Actualizar con el script real de build y la carpeta de salida.*

---

## 8. Resumen rápido (a completar cuando exista frontend)

| Paso | Acción |
|------|--------|
| 1 | Tener Node.js (LTS) y npm/yarn. |
| 2 | Backend en ejecución (ver [08_Guia_Desarrollo](08_Guia_Desarrollo.md)). |
| 3 | `cd CodigoForntend`. |
| 4 | Copiar `.env.example` a `.env` y configurar `VITE_API_BASE_URL` (o equivalente). |
| 5 | `npm install` (o yarn/pnpm). |
| 6 | `npm run dev` (o comando de desarrollo del proyecto). |
| 7 | Abrir en el navegador la URL que indique el servidor de desarrollo. |
| Build | `npm run build` para generar la carpeta de producción. |

---

## 9. Actualización de este documento

Cuando el frontend esté implementado:

1. Completar las secciones **4**, **6** y **7** con los comandos exactos del `package.json` y la carpeta de salida del build.
2. Ajustar la sección **5** al sistema de variables de entorno del stack (Vite, CRA, Angular, etc.).
3. Añadir, si aplica, requisitos adicionales (versión mínima de Node, uso de yarn/pnpm).
4. Opcional: enlazar o duplicar esta guía en un `README.md` dentro de `CodigoForntend/` para que quien abra solo esa carpeta tenga los pasos a mano.

---

## Referencias

- [10_Frontend_Especificacion](10_Frontend_Especificacion.md) – Especificación e integración con la API
- [08_Guia_Desarrollo](08_Guia_Desarrollo.md) – Ejecución del backend
- [06_API_Endpoints](06_API_Endpoints.md) – Endpoints que consumirá el frontend
- Carpeta del proyecto: `CodigoForntend/`
