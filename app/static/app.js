/* Skilled Guard — lógica de la interfaz.
 *
 * Sin framework ni paso de compilación: el navegador carga este archivo tal
 * cual. La API la sirve el mismo origen, así que las rutas son relativas y no
 * hace falta configurar CORS.
 */

// El token vive en sessionStorage y no en localStorage: se borra al cerrar la
// pestaña, así que una sesión olvidada en un equipo compartido —la portería lo
// es— no queda abierta indefinidamente.
const SESION = {
  get token() {
    return sessionStorage.getItem("token");
  },
  set token(valor) {
    valor ? sessionStorage.setItem("token", valor) : sessionStorage.removeItem("token");
  },
};

const $ = (id) => document.getElementById(id);

let equipoActual = null;
let camara = null;
let animacion = null;

// ---------------------------------------------------------------- utilidades

async function api(ruta, opciones = {}) {
  const cabeceras = { ...(opciones.headers || {}) };
  if (SESION.token) cabeceras.Authorization = `Bearer ${SESION.token}`;
  // URLSearchParams ya declara application/x-www-form-urlencoded por sí solo;
  // forzarle JSON hacía que el login llegara sin campos y fallara con 422.
  if (opciones.body && !(opciones.body instanceof URLSearchParams) && !cabeceras["Content-Type"]) {
    cabeceras["Content-Type"] = "application/json";
  }

  const respuesta = await fetch(ruta, { ...opciones, headers: cabeceras });

  if (respuesta.status === 401) {
    cerrarSesion("La sesión expiró. Vuelva a ingresar.");
    throw new Error("sesión expirada");
  }

  if (!respuesta.ok) {
    let detalle = `Error ${respuesta.status}`;
    try {
      const cuerpo = await respuesta.json();
      // Pydantic devuelve una lista de errores; la API, un texto.
      if (typeof cuerpo.detail === "string") detalle = cuerpo.detail;
      else if (Array.isArray(cuerpo.detail)) detalle = cuerpo.detail[0]?.msg ?? detalle;
    } catch {
      /* la respuesta no traía JSON */
    }
    throw new Error(detalle);
  }

  return respuesta;
}

const json = (ruta, opciones) => api(ruta, opciones).then((r) => r.json());

function mostrarMensaje(idElemento, texto, tipo = "exito") {
  const caja = $(idElemento);
  caja.textContent = texto;
  caja.className = `mensaje ${tipo}`;
  caja.scrollIntoView({ block: "nearest", behavior: "smooth" });
}

function ocultarMensaje(idElemento) {
  $(idElemento).className = "mensaje oculto";
}

const fecha = (iso) =>
  iso ? new Date(iso).toLocaleString("es-CO", { dateStyle: "short", timeStyle: "short" }) : "—";

// ------------------------------------------------------------------- ingreso

$("form-login").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultarMensaje("error-login");
  $("boton-entrar").disabled = true;

  try {
    // El endpoint de login espera un formulario, no JSON (estándar OAuth2).
    const cuerpo = new URLSearchParams({
      username: $("documento").value.trim(),
      password: $("contrasena").value,
    });
    const datos = await json("/auth/login", { method: "POST", body: cuerpo });
    SESION.token = datos.access_token;
    $("contrasena").value = "";
    await iniciarAplicacion();
  } catch (error) {
    mostrarMensaje("error-login", error.message, "error");
  } finally {
    $("boton-entrar").disabled = false;
  }
});

function cerrarSesion(aviso) {
  SESION.token = null;
  detenerCamara();
  $("aplicacion").classList.add("oculto");
  $("pantalla-login").classList.remove("oculto");
  if (aviso) mostrarMensaje("error-login", aviso, "aviso");
}

$("boton-salir").addEventListener("click", () => cerrarSesion());

async function iniciarAplicacion() {
  const yo = await json("/auth/yo");
  $("usuario-sesion").textContent = `${yo.nombre_completo} · ${yo.roles.join(", ") || "sin rol"}`;
  $("pantalla-login").classList.add("oculto");
  $("aplicacion").classList.remove("oculto");
  cambiarVista("porteria");
}

// ----------------------------------------------------------------- navegación

function cambiarVista(vista) {
  for (const boton of document.querySelectorAll("nav button")) {
    boton.toggleAttribute("aria-current", boton.dataset.vista === vista);
    if (boton.dataset.vista === vista) boton.setAttribute("aria-current", "page");
  }
  for (const nombre of ["porteria", "equipos", "historial"]) {
    $(`vista-${nombre}`).classList.toggle("oculto", nombre !== vista);
  }
  // La cámara solo debe estar encendida mientras se está en portería.
  if (vista !== "porteria") detenerCamara();
  if (vista === "equipos") cargarEquipos();
  if (vista === "historial") cargarHistorial();
}

for (const boton of document.querySelectorAll("nav button")) {
  boton.addEventListener("click", () => cambiarVista(boton.dataset.vista));
}

// ------------------------------------------------------------------ portería

$("boton-camara").addEventListener("click", () => (camara ? detenerCamara() : iniciarCamara()));

async function iniciarCamara() {
  try {
    const flujo = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: "environment" },
    });
    camara = flujo;
    const video = $("video");
    video.srcObject = flujo;
    video.classList.remove("oculto");
    $("marco").classList.remove("oculto");
    $("aviso-camara").classList.add("oculto");
    $("boton-camara").textContent = "Apagar cámara";
    await video.play();
    escanear();
  } catch (error) {
    // getUserMedia falla si no hay permiso, no hay cámara, o el sitio no está
    // en HTTPS ni en localhost: el navegador exige contexto seguro.
    $("aviso-camara").innerHTML =
      "No se pudo acceder a la cámara.<br>Verifique los permisos, o escriba el código manualmente." +
      `<br><small>${error.name}</small>`;
  }
}

function detenerCamara() {
  if (animacion) cancelAnimationFrame(animacion);
  animacion = null;
  if (camara) camara.getTracks().forEach((pista) => pista.stop());
  camara = null;
  $("video").classList.add("oculto");
  $("marco").classList.add("oculto");
  $("aviso-camara").classList.remove("oculto");
  $("boton-camara").textContent = "Activar cámara";
}

function escanear() {
  const video = $("video");
  if (!camara || video.readyState !== video.HAVE_ENOUGH_DATA) {
    animacion = requestAnimationFrame(escanear);
    return;
  }

  const lienzo = document.createElement("canvas");
  lienzo.width = video.videoWidth;
  lienzo.height = video.videoHeight;
  const contexto = lienzo.getContext("2d", { willReadFrequently: true });
  contexto.drawImage(video, 0, 0, lienzo.width, lienzo.height);

  const imagen = contexto.getImageData(0, 0, lienzo.width, lienzo.height);
  const codigo = jsQR(imagen.data, imagen.width, imagen.height);

  if (codigo?.data) {
    detenerCamara();
    buscarEquipo(codigo.data);
    return;
  }
  animacion = requestAnimationFrame(escanear);
}

$("boton-buscar-qr").addEventListener("click", () => {
  const codigo = $("qr-manual").value.trim();
  if (codigo) buscarEquipo(codigo);
});

async function buscarEquipo(codigoQr) {
  ocultarMensaje("mensaje-porteria");
  try {
    // No hay endpoint de búsqueda por QR: se resuelve sobre el listado, que
    // ya está paginado y acotado en el servidor.
    const equipos = await json("/dispositivos?limite=200");
    const equipo = equipos.find((e) => e.qr === codigoQr);
    if (!equipo) {
      mostrarMensaje("mensaje-porteria", "El código QR no corresponde a un equipo registrado.", "error");
      $("equipo-detectado").classList.add("oculto");
      $("sin-equipo").classList.remove("oculto");
      return;
    }
    const estado = await json(`/dispositivos/${equipo.id}/estado`);
    equipoActual = { ...equipo, ...estado };
    pintarEquipo(equipoActual);
  } catch (error) {
    mostrarMensaje("mensaje-porteria", error.message, "error");
  }
}

async function pintarEquipo(equipo) {
  $("det-serial").textContent = equipo.serial;
  $("det-equipo").textContent = `${equipo.marca} ${equipo.modelo}`;
  $("det-ultimo").textContent = fecha(equipo.ultimo_movimiento);

  const pastilla = $("estado-equipo");
  pastilla.textContent = equipo.estado === "dentro" ? "Dentro de las instalaciones" : "Fuera";
  pastilla.className = `pastilla ${equipo.estado}`;

  // Deshabilitar el movimiento imposible evita el rechazo antes de pedirlo.
  // El servidor lo valida igual: esto es comodidad, no seguridad.
  $("boton-ingreso").disabled = equipo.estado === "dentro";
  $("boton-salida").disabled = equipo.estado === "fuera";

  $("det-responsable").textContent = "—";
  try {
    const usuarios = await json("/usuarios?limite=200");
    const responsable = usuarios.find((u) => u.id === equipo.id_usuario);
    if (responsable) {
      $("det-responsable").textContent = `${responsable.nombres} ${responsable.apellidos}`;
    }
  } catch {
    // El rol Seguridad no puede listar usuarios; el resto de la ficha sirve igual.
  }

  $("sin-equipo").classList.add("oculto");
  $("equipo-detectado").classList.remove("oculto");
}

for (const [boton, tipo] of [
  ["boton-ingreso", "Ingreso"],
  ["boton-salida", "Salida"],
]) {
  $(boton).addEventListener("click", () => registrarMovimiento(tipo));
}

async function registrarMovimiento(tipo) {
  if (!equipoActual) return;
  $("boton-ingreso").disabled = true;
  $("boton-salida").disabled = true;

  try {
    const movimiento = await json("/movimientos", {
      method: "POST",
      body: JSON.stringify({
        qr: equipoActual.qr,
        tipo,
        observacion: $("observacion").value.trim() || null,
      }),
    });
    mostrarMensaje(
      "mensaje-porteria",
      `${tipo} registrado: ${movimiento.equipo} (${movimiento.serial}) — ${fecha(movimiento.fecha)}`,
      "exito",
    );
    $("observacion").value = "";
    $("qr-manual").value = "";

    const estado = await json(`/dispositivos/${equipoActual.id}/estado`);
    equipoActual = { ...equipoActual, ...estado };
    pintarEquipo(equipoActual);
  } catch (error) {
    mostrarMensaje("mensaje-porteria", error.message, "error");
    // Repintar restaura el estado correcto de los botones tras el rechazo.
    if (equipoActual) pintarEquipo(equipoActual);
  }
}

// ------------------------------------------------------------------- equipos

async function cargarEquipos() {
  ocultarMensaje("mensaje-equipos");
  try {
    const [equipos, tipos, usuarios] = await Promise.all([
      json("/dispositivos?limite=200"),
      json("/tipos-dispositivo"),
      json("/usuarios?limite=200").catch(() => []),
    ]);

    rellenarSelector("eq-tipo", tipos, (t) => t.nombre);
    rellenarSelector("eq-usuario", usuarios, (u) => `${u.nombres} ${u.apellidos} — ${u.documento}`);
    // Sin permiso para listar usuarios no se puede registrar un equipo.
    $("tarjeta-registro").classList.toggle("oculto", usuarios.length === 0);

    const cuerpo = $("tabla-equipos");
    cuerpo.innerHTML = "";
    if (equipos.length === 0) {
      cuerpo.innerHTML = '<tr><td colspan="5" class="vacio">No hay equipos registrados.</td></tr>';
      return;
    }

    for (const equipo of equipos) {
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td>${equipo.serial}</td>
        <td>${equipo.marca} ${equipo.modelo}</td>
        <td>${equipo.sistema ?? "—"}</td>
        <td><span class="pastilla ${equipo.estado}">${equipo.estado}</span></td>
        <td></td>`;
      const boton = document.createElement("button");
      boton.className = "boton secundario";
      boton.textContent = "Ver e imprimir";
      boton.addEventListener("click", () => mostrarQr(equipo));
      fila.lastElementChild.appendChild(boton);
      cuerpo.appendChild(fila);
    }
  } catch (error) {
    mostrarMensaje("mensaje-equipos", error.message, "error");
  }
}

function rellenarSelector(id, elementos, etiqueta) {
  const selector = $(id);
  selector.innerHTML = "";
  for (const elemento of elementos) {
    const opcion = document.createElement("option");
    opcion.value = elemento.id;
    opcion.textContent = etiqueta(elemento);
    selector.appendChild(opcion);
  }
}

$("form-equipo").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultarMensaje("mensaje-equipos");
  try {
    const equipo = await json("/dispositivos", {
      method: "POST",
      body: JSON.stringify({
        serial: $("eq-serial").value.trim(),
        marca: $("eq-marca").value.trim(),
        modelo: $("eq-modelo").value.trim(),
        sistema: $("eq-sistema").value.trim() || null,
        id_tipo_dispositivo: Number($("eq-tipo").value),
        id_usuario: Number($("eq-usuario").value),
      }),
    });
    mostrarMensaje("mensaje-equipos", `Equipo ${equipo.serial} registrado. Ya tiene su código QR.`);
    $("form-equipo").reset();
    cargarEquipos();
  } catch (error) {
    mostrarMensaje("mensaje-equipos", error.message, "error");
  }
});

async function mostrarQr(equipo) {
  // La imagen exige el token, así que no sirve un <img src>: se descarga por
  // fetch y se convierte a un objeto en memoria.
  const respuesta = await api(`/dispositivos/${equipo.id}/qr`);
  const url = URL.createObjectURL(await respuesta.blob());

  const zona = $("zona-impresion");
  zona.className = "qr-caja";
  zona.innerHTML = `
    <h2>${equipo.marca} ${equipo.modelo}</h2>
    <p><strong>Serial: ${equipo.serial}</strong></p>
    <img src="${url}" alt="Código QR del equipo ${equipo.serial}">
    <p>${equipo.qr}</p>`;
  const imprimir = document.createElement("button");
  imprimir.className = "boton";
  imprimir.textContent = "Imprimir";
  imprimir.addEventListener("click", () => window.print());
  zona.appendChild(imprimir);
  zona.scrollIntoView({ behavior: "smooth" });
}

// ------------------------------------------------------------------ historial

function filtrosHistorial() {
  const parametros = new URLSearchParams();
  if ($("f-tipo").value) parametros.set("tipo", $("f-tipo").value);
  if ($("f-desde").value) parametros.set("desde", $("f-desde").value);
  if ($("f-hasta").value) parametros.set("hasta", $("f-hasta").value);
  return parametros;
}

async function cargarHistorial() {
  ocultarMensaje("mensaje-historial");
  try {
    const movimientos = await json(`/movimientos?${filtrosHistorial()}`);
    const cuerpo = $("tabla-historial");
    cuerpo.innerHTML = "";

    if (movimientos.length === 0) {
      cuerpo.innerHTML =
        '<tr><td colspan="7" class="vacio">No hay movimientos para estos filtros.</td></tr>';
      return;
    }

    for (const m of movimientos) {
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td class="numero">${fecha(m.fecha)}</td>
        <td><span class="pastilla ${m.tipo.toLowerCase()}">${m.tipo}</span></td>
        <td>${m.serial}</td>
        <td>${m.equipo}</td>
        <td>${m.responsable}</td>
        <td>${m.registrado_por}</td>
        <td>${m.observacion ?? "—"}</td>`;
      cuerpo.appendChild(fila);
    }
  } catch (error) {
    mostrarMensaje("mensaje-historial", error.message, "error");
  }
}

$("boton-filtrar").addEventListener("click", cargarHistorial);

for (const [boton, extension] of [
  ["boton-excel", "xlsx"],
  ["boton-pdf", "pdf"],
]) {
  $(boton).addEventListener("click", () => descargarReporte(extension));
}

async function descargarReporte(extension) {
  try {
    const respuesta = await api(`/reportes/movimientos.${extension}?${filtrosHistorial()}`);
    const url = URL.createObjectURL(await respuesta.blob());
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = `movimientos.${extension}`;
    enlace.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    mostrarMensaje("mensaje-historial", error.message, "error");
  }
}

// -------------------------------------------------------------------- arranque

if (SESION.token) {
  iniciarAplicacion().catch(() => cerrarSesion());
}
