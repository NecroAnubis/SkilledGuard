/**
 * Dashboard / layout compartido.
 * Comprueba sesión, muestra usuario en header, menú según rol, y cierra sesión.
 * En index.html también muestra métricas, fecha y acciones.
 */
(function () {
//if (!authRequerirSesion()) return;

  const user = authObtenerUsuario();
  const navUsuarios = document.getElementById('navUsuarios');

  function getNombre() {
    if (!user) return 'Usuario';
    return [user.nombres, user.apellidos].filter(Boolean).join(' ') || user.email || 'Usuario';
  }
  function getRol() { return (user && user.rol) || 'Usuario'; }

  /* Header: nuevo (dropdown) o antiguo (userInfo) */
  const userNameEl = document.getElementById('userName');
  const userRoleEl = document.getElementById('userRole');
  const userInfoEl = document.getElementById('userInfo');

  if (userNameEl) userNameEl.textContent = getNombre();
  if (userRoleEl) userRoleEl.textContent = getRol();
  if (userInfoEl) userInfoEl.textContent = getNombre() + ' (' + getRol() + ')';

  /* Dashboard: bienvenida y acciones */
  const welcomeTitleEl = document.getElementById('welcomeTitle');
  const roleBadgeEl = document.getElementById('roleBadge');
  const userEmailEl = document.getElementById('userEmail');
  const actionsSubtitleEl = document.getElementById('actionsSubtitle');

  if (welcomeTitleEl) welcomeTitleEl.textContent = '¡Hola, ' + getNombre() + '!';
  if (roleBadgeEl) roleBadgeEl.textContent = getRol();
  if (userEmailEl && user) userEmailEl.textContent = user.email || '';
  if (actionsSubtitleEl) actionsSubtitleEl.textContent = 'Funciones habilitadas para tu rol de ' + getRol().toLowerCase();

  /* Mostrar "Usuarios" solo para rol Administrador */
  if (navUsuarios && user && user.rol) {
    if (String(user.rol).toLowerCase().includes('admin')) navUsuarios.style.display = '';
  }

  /* Fecha actual (solo en dashboard) */
  const dateEl = document.getElementById('currentDate');
  if (dateEl) {
    const opts = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateEl.textContent = new Date().toLocaleDateString('es-CO', opts);
  }

  /* Métricas (solo en dashboard) */
  const totalDispositivosEl = document.getElementById('totalDispositivos');
  const usuariosActivosEl = document.getElementById('usuariosActivos');
  const accesosHoyEl = document.getElementById('accesosHoy');

  if (totalDispositivosEl) totalDispositivosEl.textContent = '0';
  if (usuariosActivosEl) usuariosActivosEl.textContent = '0';
  if (accesosHoyEl) accesosHoyEl.textContent = '0';

  if (typeof apiGet === 'function' && authObtenerToken()) {
    Promise.all([
      apiGet('/api/Dispositivo/count').catch(() => null),
      apiGet('/api/Usuario/count').catch(() => null)
    ]).then(function (results) {
      if (results[0] != null && totalDispositivosEl) totalDispositivosEl.textContent = results[0];
      if (results[1] != null && usuariosActivosEl) usuariosActivosEl.textContent = results[1];
    });
  }

  /* Cerrar sesión: dropdown o botón */
  const userDropdown = document.getElementById('userDropdown');
  const btnCerrarSesion = document.getElementById('btnCerrarSesion');

  if (userDropdown) userDropdown.addEventListener('click', function (e) { e.preventDefault(); authCerrarSesion(); });
  if (btnCerrarSesion) btnCerrarSesion.addEventListener('click', function (e) { e.preventDefault(); authCerrarSesion(); });
})();
