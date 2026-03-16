/**
 * Lógica de la pantalla de login.
 * Escucha el envío del formulario, llama a la API, guarda sesión y redirige.
 */
(function () {
  const form = document.getElementById('formLogin');
  const emailInput = document.getElementById('email');
  const passwordInput = document.getElementById('contraseña');
  const errorDiv = document.getElementById('loginError');
  const btnLogin = document.getElementById('btnLogin');

  function mostrarError(mensaje) {
    errorDiv.textContent = mensaje || '';
    errorDiv.classList.toggle('alert--error', !!mensaje);
    if (mensaje) errorDiv.setAttribute('aria-live', 'assertive');
  }

  function setLoading(loading) {
    btnLogin.disabled = loading;
    btnLogin.textContent = loading ? 'Entrando…' : 'Entrar';
  }

  if (authEstaAutenticado()) {
    window.location.href = 'index.html';
    return;
  }

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    mostrarError('');

    const email = (emailInput.value || '').trim();
    const contraseña = passwordInput.value || '';

    if (!email) {
      mostrarError('Ingresa tu usuario.');
      emailInput.focus();
      return;
    }
    if (!contraseña) {
      mostrarError('Ingresa tu contraseña.');
      passwordInput.focus();
      return;
    }

    setLoading(true);
    try {
      const data = await apiLogin(email, contraseña);
      authGuardarSesion(data.token, data.usuario);
      window.location.href = 'index.html';
    } catch (err) {
      mostrarError(err.message || 'Error al iniciar sesión. Revisa tu conexión.');
      setLoading(false);
    }
  });
})();
