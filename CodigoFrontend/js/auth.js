/**
 * Módulo de autenticación: token, usuario y redirección.
 * Usa sessionStorage (sesión cerrada al cerrar pestaña) o cambiar a localStorage si se prefiere persistencia.
 */

const AUTH_TOKEN_KEY = 'skilledguard_token';
const AUTH_USER_KEY = 'skilledguard_user';

/**
 * Guarda token y datos del usuario tras login exitoso.
 * @param {string} token - JWT devuelto por la API
 * @param {object} usuario - { id, nombres, apellidos, email, rol, ... }
 */
function authGuardarSesion(token, usuario) {
  sessionStorage.setItem(AUTH_TOKEN_KEY, token);
  sessionStorage.setItem(AUTH_USER_KEY, JSON.stringify(usuario));
}

/**
 * Obtiene el token JWT actual (null si no hay sesión).
 * @returns {string|null}
 */
function authObtenerToken() {
  return sessionStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Obtiene el usuario actual (null si no hay sesión).
 * @returns {object|null}
 */
function authObtenerUsuario() {
  const raw = sessionStorage.getItem(AUTH_USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

/**
 * Indica si hay una sesión activa.
 * @returns {boolean}
 */
function authEstaAutenticado() {
  return !!authObtenerToken();
}

/**
 * Cierra sesión: borra token y usuario, redirige a login.
 * @param {string} [paginaLogin='login.html']
 */
function authCerrarSesion(paginaLogin = 'login.html') {
  sessionStorage.removeItem(AUTH_TOKEN_KEY);
  sessionStorage.removeItem(AUTH_USER_KEY);
  window.location.href = paginaLogin;
}

/**
 * Si no hay token, redirige a login y devuelve false.
 * Útil al inicio de páginas protegidas.
 * @param {string} [paginaLogin='login.html']
 * @returns {boolean} true si hay sesión, false si redirigió
 */
function authRequerirSesion(paginaLogin = 'login.html') {
  if (!authEstaAutenticado()) {
    window.location.href = paginaLogin;
    return false;
  }
  return true;
}
