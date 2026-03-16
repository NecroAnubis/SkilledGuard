/**
 * Cliente API: login y peticiones autenticadas.
 * Todas las URLs se construyen con API_BASE_URL definido en config.js.
 */

/**
 * Login: POST /api/Auth/login
 * @param {string} email
 * @param {string} contraseña
 * @returns {Promise<{ token: string, usuario: object }>}
 * @throws Error si la respuesta no es ok (ej. 401 credenciales inválidas)
 */
async function apiLogin(email, contraseña) {
  const url = API_BASE_URL + '/api/Auth/login';
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, contraseña }),
  });

  if (!res.ok) {
    const text = await res.text();
    let mensaje = 'Error al iniciar sesión';
    if (res.status === 401) mensaje = 'Credenciales incorrectas';
    else if (text) {
      try {
        const data = JSON.parse(text);
        if (data.message) mensaje = data.message;
      } catch {
        if (text.length < 200) mensaje = text;
      }
    }
    throw new Error(mensaje);
  }

  return res.json();
}

/**
 * Realiza una petición autenticada (GET, POST, PUT, DELETE).
 * Añade Authorization: Bearer <token>. Si no hay token o la API devuelve 401, redirige a login.
 * @param {string} path - Ruta relativa (ej. '/api/Usuario')
 * @param {RequestInit} [opts] - Opciones de fetch (method, body, headers, etc.)
 * @returns {Promise<Response>} - Respuesta de fetch (sin parsear JSON)
 */
async function apiRequest(path, opts = {}) {
  const token = authObtenerToken();
  if (!token) {
    authCerrarSesion();
    return;
  }

  const url = path.startsWith('http') ? path : API_BASE_URL + path;
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token,
    ...(opts.headers || {}),
  };

  const res = await fetch(url, { ...opts, headers });

  if (res.status === 401) {
    authCerrarSesion();
    return;
  }

  return res;
}

/**
 * GET autenticado y parseo JSON.
 * @param {string} path - Ej. '/api/Usuario'
 * @returns {Promise<any>}
 */
async function apiGet(path) {
  const res = await apiRequest(path, { method: 'GET' });
  if (!res) return null;
  if (!res.ok) throw new Error(res.statusText || 'Error en la petición');
  return res.json();
}

/**
 * POST autenticado con cuerpo JSON.
 * @param {string} path
 * @param {object} body
 * @returns {Promise<any>}
 */
async function apiPost(path, body) {
  const res = await apiRequest(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
  if (!res) return null;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) return res.json();
  return res.text();
}

/**
 * PUT autenticado con cuerpo JSON.
 * @param {string} path - Ej. '/api/Usuario/123'
 * @param {object} body
 * @returns {Promise<any>}
 */
async function apiPut(path, body) {
  const res = await apiRequest(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
  if (!res) return null;
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || res.statusText);
  }
  const contentType = res.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) return res.json();
  return res.text();
}

/**
 * DELETE autenticado.
 * @param {string} path - Ej. '/api/Usuario/123'
 * @returns {Promise<void>}
 */
async function apiDelete(path) {
  const res = await apiRequest(path, { method: 'DELETE' });
  if (!res) return;
  if (!res.ok) throw new Error(res.statusText || 'Error al eliminar');
}
