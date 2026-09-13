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
  SESION.roles = yo.roles;
  // La tablet de autoservicio vive en una sola pantalla: escanear e ingresar.
  // Ocultar el resto es comodidad; los permisos reales los exige el servidor.
  SESION.kiosco = yo.roles.includes("Entrada") && !yo.roles.includes("Administrador") && !yo.roles.includes("Seguridad");
  document.body.classList.toggle("kiosco", SESION.kiosco);
  $("nav-usuarios").classList.toggle("oculto", !yo.roles.includes("Administrador"));
  if (SESION.kiosco) {
    document.querySelector("#vista-porteria h1").textContent = "Registre su ingreso";
    document.querySelector("#vista-porteria .subtitulo").textContent =
      "Escanee el código QR pegado en su equipo. La salida la registra el personal de seguridad.";
  }
  $("usuario-sesion").textContent = yo.nombre_completo;
  $("saludo-nombre").textContent = `¡Hola, ${yo.nombre_completo.split(" ")[0]}!`;
  $("saludo-rol").textContent = yo.roles.join(", ") || "Sin rol";
  $("fecha-hoy").textContent = new Date().toLocaleDateString("es-CO", {
    weekday: "long", day: "numeric", month: "long", year: "numeric",
  });
  $("pantalla-login").classList.add("oculto");
  $("aplicacion").classList.remove("oculto");
  const inicial = SESION.kiosco ? "porteria" : "inicio";
  cambiarVista(inicial, false);
  history.replaceState({ vista: inicial }, "", `#${inicial}`);
}

// ----------------------------------------------------------------- navegación

function cambiarVista(vista, registrar = true) {
  if (SESION.kiosco) vista = "porteria";
  for (const boton of document.querySelectorAll("nav button")) {
    boton.toggleAttribute("aria-current", boton.dataset.vista === vista);
    if (boton.dataset.vista === vista) boton.setAttribute("aria-current", "page");
  }
  for (const nombre of ["inicio", "porteria", "equipos", "historial", "usuarios"]) {
    $(`vista-${nombre}`).classList.toggle("oculto", nombre !== vista);
  }
  // Cada vista es una entrada del historial: el botón atrás del navegador (y
  // del teléfono) navega entre vistas en vez de sacar al usuario de la app.
  $("boton-volver").classList.toggle("oculto", vista === "inicio");
  if (registrar && location.hash !== `#${vista}`) {
    history.pushState({ vista }, "", `#${vista}`);
  }
  // La cámara solo debe estar encendida mientras se está en portería.
  if (vista !== "porteria") detenerCamara();
  if (vista === "porteria") cargarPorterias();
  if (vista === "inicio") cargarInicio();
  if (vista === "equipos") cargarEquipos();
  if (vista === "usuarios") cargarUsuarios();
  if (vista === "historial") cargarHistorial();
}

window.addEventListener("popstate", (evento) => {
  if (!SESION.token) return;
  cambiarVista(evento.state?.vista || "inicio", false);
});

$("boton-volver").addEventListener("click", () => history.back());

// Las tarjetas de acción del inicio son atajos de navegación.
for (const accion of document.querySelectorAll(".accion")) {
  accion.addEventListener("click", () => cambiarVista(accion.dataset.vista));
}

// ------------------------------------------------------------------- inicio

function hace(iso) {
  const minutos = Math.round((Date.now() - new Date(iso)) / 60000);
  if (minutos < 1) return "Hace un momento";
  if (minutos < 60) return `Hace ${minutos} min`;
  const horas = Math.round(minutos / 60);
  if (horas < 24) return `Hace ${horas} h`;
  return fecha(iso);
}

// La tablet vive en una entrada fija: se recuerda cuál en este dispositivo
// para que nadie tenga que elegirla en cada movimiento. Es una comodidad
// local, no un permiso: el servidor valida la portería que llegue.
const PORTERIA_RECORDADA = "porteria";

async function cargarPorterias() {
  const selector = $("sel-porteria");
  if (selector.options.length) return;
  try {
    const porterias = await json("/porterias");
    rellenarSelector("sel-porteria", porterias, (p) => p.nombre);
    let recordada = null;
    try {
      recordada = localStorage.getItem(PORTERIA_RECORDADA);
    } catch {
      /* el navegador puede tener el almacenamiento bloqueado */
    }
    if (recordada && porterias.some((p) => String(p.id) === recordada)) {
      selector.value = recordada;
    }
    selector.addEventListener("change", () => {
      try {
        localStorage.setItem(PORTERIA_RECORDADA, selector.value);
      } catch {
        /* sin almacenamiento se elige en cada sesión; el registro no se frena */
      }
    });
  } catch {
    // Sin catálogo de porterías el movimiento se registra igual, sin declararla.
    $("pista-porteria").textContent = "No se pudo cargar la lista de porterías.";
  }
}

async function cargarInicio() {
  try {
    // La fecha local, no UTC: a las 8 pm en Colombia "hoy" todavía es hoy.
    const hoy = new Date().toLocaleDateString("en-CA");
    const [equipos, deHoy, recientes] = await Promise.all([
      json("/dispositivos?limite=200"),
      json(`/movimientos?desde=${hoy}&hasta=${hoy}&limite=200`),
      json("/movimientos?limite=5"),
    ]);

    $("stat-equipos").textContent = equipos.length;
    $("stat-dentro").textContent = equipos.filter((e) => e.estado === "dentro").length;
    $("stat-hoy").textContent = deHoy.length;

    const lista = $("lista-actividad");
    lista.innerHTML = "";
    if (recientes.length === 0) {
      lista.innerHTML = '<li class="vacio">Sin movimientos todavía.</li>';
      return;
    }
    for (const m of recientes) {
      const fila = document.createElement("li");
      const detalle = document.createElement("span");
      detalle.innerHTML = `<strong>${m.tipo}</strong> · ${m.equipo} — ${m.responsable}`;
      const cuando = document.createElement("span");
      cuando.className = "cuando";
      cuando.textContent = hace(m.fecha);
      fila.append(detalle, cuando);
      lista.appendChild(fila);
    }
  } catch {
    // El tablero es informativo: si una cifra falla, la navegación sigue viva.
  }
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
  $("chk-cotejo").checked = false;
  actualizarBotonSalida();

  $("det-responsable").textContent = equipo.responsable;

  $("sin-equipo").classList.add("oculto");
  $("equipo-detectado").classList.remove("oculto");
}

for (const [boton, tipo] of [
  ["boton-ingreso", "Ingreso"],
  ["boton-salida", "Salida"],
]) {
  $(boton).addEventListener("click", () => registrarMovimiento(tipo));
}

// La salida exige que el vigilante confirme el cotejo físico del equipo.
function actualizarBotonSalida() {
  const puede = equipoActual && equipoActual.estado === "dentro" && $("chk-cotejo").checked;
  $("boton-salida").disabled = !puede;
}
$("chk-cotejo").addEventListener("change", actualizarBotonSalida);

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
        id_porteria: Number($("sel-porteria").value) || null,
        observacion:
          tipo === "Salida"
            ? ["Serial cotejado físicamente", $("observacion").value.trim()].filter(Boolean).join(" — ")
            : $("observacion").value.trim() || null,
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
    const [equipos, tipos] = await Promise.all([
      json("/dispositivos?limite=200"),
      json("/tipos-dispositivo"),
    ]);

    rellenarSelector("eq-tipo", tipos, (t) => t.nombre);
    // Solo el administrador puede registrar equipos; el servidor lo exige igual.
    $("tarjeta-registro").classList.toggle("oculto", !SESION.roles?.includes("Administrador"));

    const cuerpo = $("tabla-equipos");
    cuerpo.innerHTML = "";
    if (equipos.length === 0) {
      cuerpo.innerHTML = '<tr><td colspan="6" class="vacio">No hay equipos registrados.</td></tr>';
      return;
    }

    for (const equipo of equipos) {
      const fila = document.createElement("tr");
      fila.innerHTML = `
        <td>${equipo.serial}</td>
        <td>${equipo.marca} ${equipo.modelo}</td>
        <td>${equipo.responsable}</td>
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
        responsable: $("eq-responsable").value.trim(),
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
  zona.innerHTML = `
    <div class="qr-tarjeta" role="dialog" aria-modal="true" aria-label="Código QR del equipo ${equipo.serial}">
      <h2>${equipo.marca} ${equipo.modelo}</h2>
      <p><strong>Serial: ${equipo.serial}</strong></p>
      <img src="${url}" alt="Código QR del equipo ${equipo.serial}">
      <p class="codigo">${equipo.qr}</p>
      <div class="qr-acciones">
        <button class="boton" id="qr-imprimir">Imprimir</button>
        <a class="boton secundario" id="qr-descargar" href="${url}" download="qr-${equipo.serial}.png">Descargar imagen</a>
        <button class="boton secundario" id="qr-cerrar">Cerrar</button>
      </div>
    </div>`;
  zona.classList.remove("oculto");

  const alPresionarTecla = (evento) => {
    if (evento.key === "Escape") cerrar();
  };
  function cerrar() {
    zona.classList.add("oculto");
    zona.innerHTML = "";
    URL.revokeObjectURL(url);
    document.removeEventListener("keydown", alPresionarTecla);
  }
  document.addEventListener("keydown", alPresionarTecla);
  // Asignación (no addEventListener): abrir otro QR no acumula manejadores.
  zona.onclick = (evento) => {
    if (evento.target === zona) cerrar();
  };
  $("qr-imprimir").addEventListener("click", () => window.print());
  $("qr-cerrar").addEventListener("click", cerrar);
  $("qr-cerrar").focus();
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
        '<tr><td colspan="8" class="vacio">No hay movimientos para estos filtros.</td></tr>';
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
        <td>${m.porteria ?? "—"}</td>
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

// ------------------------------------------------------------------ usuarios

let ROLES = [];

async function cargarUsuarios() {
  ocultarMensaje("mensaje-usuarios");
  try {
    const [usuarios, tiposDoc, roles] = await Promise.all([
      json("/usuarios?limite=200"),
      json("/tipos-documento"),
      json("/roles"),
    ]);
    ROLES = roles;
    rellenarSelector("us-tipo-doc", tiposDoc, (t) => t.nombre);
    rellenarSelector("us-rol", roles, (r) => r.nombre);

    const cuerpo = $("tabla-usuarios");
    cuerpo.innerHTML = "";
    for (const u of usuarios) {
      const fila = document.createElement("tr");
      const pastillas = u.roles.length
        ? u.roles.map((r) => `<span class="pastilla rol">${r}</span>`).join("")
        : '<span class="pastilla fuera">Sin rol</span>';
      fila.innerHTML = `
        <td>${u.nombres} ${u.apellidos}</td>
        <td>${u.documento}</td>
        <td>${pastillas}</td>
        <td></td>`;

      // Solo se ofrecen los roles que el usuario aún no tiene.
      const faltantes = roles.filter((r) => !u.roles.includes(r.nombre));
      if (faltantes.length) {
        const zona = document.createElement("div");
        zona.className = "agregar-rol";
        const selector = document.createElement("select");
        for (const r of faltantes) {
          const opcion = document.createElement("option");
          opcion.value = r.id;
          opcion.textContent = r.nombre;
          selector.appendChild(opcion);
        }
        const boton = document.createElement("button");
        boton.className = "boton secundario";
        boton.textContent = "Agregar";
        boton.addEventListener("click", () => asignarRol(u, Number(selector.value)));
        zona.append(selector, boton);
        fila.lastElementChild.appendChild(zona);
      }
      cuerpo.appendChild(fila);
    }
  } catch (error) {
    mostrarMensaje("mensaje-usuarios", error.message, "error");
  }
}

async function asignarRol(usuario, idRol) {
  ocultarMensaje("mensaje-usuarios");
  try {
    await api(`/usuarios/${usuario.id}/roles`, {
      method: "POST",
      body: JSON.stringify({ id_rol: idRol }),
    });
    const rol = ROLES.find((r) => r.id === idRol);
    mostrarMensaje("mensaje-usuarios", `Rol ${rol?.nombre ?? ""} asignado a ${usuario.nombres}.`);
    cargarUsuarios();
  } catch (error) {
    mostrarMensaje("mensaje-usuarios", error.message, "error");
  }
}

$("form-usuario").addEventListener("submit", async (evento) => {
  evento.preventDefault();
  ocultarMensaje("mensaje-usuarios");
  try {
    const usuario = await json("/usuarios", {
      method: "POST",
      body: JSON.stringify({
        nombres: $("us-nombres").value.trim(),
        apellidos: $("us-apellidos").value.trim(),
        id_tipo_documento: Number($("us-tipo-doc").value),
        documento: $("us-documento").value.trim(),
        contrasena: $("us-contrasena").value,
      }),
    });
    await api(`/usuarios/${usuario.id}/roles`, {
      method: "POST",
      body: JSON.stringify({ id_rol: Number($("us-rol").value) }),
    });
    mostrarMensaje("mensaje-usuarios", `Usuario ${usuario.documento} registrado con su rol.`);
    $("form-usuario").reset();
    cargarUsuarios();
  } catch (error) {
    mostrarMensaje("mensaje-usuarios", error.message, "error");
  }
});

if (SESION.token) {
  iniciarAplicacion().catch(() => cerrarSesion());
}
