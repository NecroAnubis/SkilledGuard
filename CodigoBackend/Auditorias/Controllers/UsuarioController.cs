// Ruta: /api/Usuario
// Propósito: CRUD de usuarios, cambio de contraseña. Crear usuario permite primer usuario sin token; el resto requiere JWT.
using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;
using Auditorias.utils;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar usuarios (listar, obtener por id, crear, actualizar, eliminar, cambiar contraseña).
    /// Requiere token salvo POST CreateUsuario: permite crear el primer usuario sin token; los siguientes requieren autenticación.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize] // Todos los endpoints requieren token JWT en los headers, excepto los marcados con [AllowAnonymous]
    public class UsuarioController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public UsuarioController(AuditoriaContext context)
        {
            _context = context;
        }

        /// <summary>
        /// GET /api/Usuario - Lista todos los usuarios con Rol y TipoDocumento (objeto anónimo sin contraseña).
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<object>>> GetUsuarios()
        {
            try
            {
                var usuarios = await _context.Usuarios
                    .Include(u => u.Rol) // le indica a entity framework que cargue tambien la informacion del rol asociado a cada usuario
                    .Include(u => u.TipoDocumento) // carga informacion del tipo de documento 
                    .Select(u => new // creacion del objeto anonimo para devolver solo los campos que se requieren en la respuesta 
                    {
                        u.Id,
                        u.Nombres,
                        u.Apellidos,
                        u.Email,
                        u.Documento,
                        u.TipoUsuario,
                        u.Direccion,
                        u.FechaCreado,
                        u.FechaActualizado,
                        Rol = u.Rol != null ? u.Rol.Nombre : null,
                        TipoDocumento = u.TipoDocumento != null ? u.TipoDocumento.Nombre : null
                    })
                    .ToListAsync(); // devuelve los objetos creados a partir de las funciones lambda o anonimas 

                if (usuarios == null || !usuarios.Any())
                    return NotFound("No se encontraron usuarios.");

                return Ok(usuarios);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Error al obtener los usuarios: {ex.Message}");
            }
        }

        /// <summary>
        /// GET /api/Usuario/{id} - Obtiene un usuario por ID con Rol y TipoDocumento (sin exponer contraseña).
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> GetUsuarioById(Guid id)
        {
            var usuario = await _context.Usuarios
                .Include(u => u.Rol)
                .Include(u => u.TipoDocumento)
                .Where(u => u.Id == id)
                .Select(u => new
                {
                    u.Id,
                    u.Nombres,
                    u.Apellidos,
                    u.Email,
                    u.Documento,
                    u.TipoUsuario,
                    u.Direccion,
                    u.FechaCreado,
                    u.FechaActualizado,
                    Rol = u.Rol != null ? u.Rol.Nombre : null,
                    TipoDocumento = u.TipoDocumento != null ? u.TipoDocumento.Nombre : null
                })
                .FirstOrDefaultAsync();

            if (usuario == null)
                return NotFound("Usuario no encontrado.");

            return Ok(usuario);
        }

        /// <summary>
        /// POST /api/Usuario - Crea un usuario. Permite crear el primer usuario sin token; si ya hay usuarios, requiere autenticación.
        /// Valida que email y documento no estén ya registrados. La contraseña se hashea antes de guardar.
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        [AllowAnonymous] // indica que no es necesario token de autorizacion para su invocacion
        public async Task<ActionResult<object>> CreateUsuario([FromBody] Usuario usuario)
        {
            if (usuario == null)
                return BadRequest("Datos inválidos.");

            // Comprobar que no exista ya un usuario con el mismo email o documento
            var usuarioExistente = await _context.Usuarios
                .Where(u => u.Email == usuario.Email || u.Documento == usuario.Documento)
                .Select(u => new { u.Email, u.Documento })
                .FirstOrDefaultAsync();

            if (usuarioExistente != null)
            {
                if (usuarioExistente.Email == usuario.Email)
                    return BadRequest("El correo ya está registrado.");
                if (usuarioExistente.Documento == usuario.Documento)
                    return BadRequest("El documento ya está registrado.");
            }

            // Si ya hay usuarios en la BD, exige token; solo el primer usuario se puede crear sin autenticación
            if (await _context.Usuarios.AnyAsync() && !(User.Identity?.IsAuthenticated ?? false))
                return Unauthorized("Debes estar autenticado para crear más usuarios.");

            usuario.Id = Guid.NewGuid();
            usuario.FechaCreado = DateTime.Now;
            usuario.Contraseña = PasswordHelper.HashPassword(usuario.Contraseña); // Nunca se guarda la contraseña en texto plano

            _context.Usuarios.Add(usuario);
            await _context.SaveChangesAsync();

            var usuarioCreado = await _context.Usuarios
                .Include(u => u.Rol)
                .Include(u => u.TipoDocumento)
                .Where(u => u.Id == usuario.Id)
                .Select(u => new
                {
                    u.Id,
                    u.Nombres,
                    u.Apellidos,
                    u.Email,
                    u.Documento,
                    u.TipoUsuario,
                    u.Direccion,
                    u.FechaCreado,
                    u.FechaActualizado,
                    Rol = u.Rol != null ? u.Rol.Nombre : null,
                    TipoDocumento = u.TipoDocumento != null ? u.TipoDocumento.Nombre : null
                })
                .FirstOrDefaultAsync();

            return CreatedAtAction(nameof(GetUsuarioById), new { id = usuario.Id }, usuarioCreado);
        }

        /// <summary>
        /// PUT /api/Usuario/{id} - Actualiza datos del usuario. Si se envía contraseña no vacía, se actualiza (hasheada).
        /// </summary>
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> UpdateUsuario(Guid id, [FromBody] Usuario usuario)
        {
            if (usuario == null || id != usuario.Id)
                return BadRequest("Datos inválidos.");

            var usuarioExistente = await _context.Usuarios.FindAsync(id);
            if (usuarioExistente == null)
                return NotFound("Usuario no encontrado.");

            usuarioExistente.Nombres = usuario.Nombres;
            usuarioExistente.Apellidos = usuario.Apellidos;
            usuarioExistente.Email = usuario.Email;
            usuarioExistente.Documento = usuario.Documento;
            usuarioExistente.TipoUsuario = usuario.TipoUsuario;
            usuarioExistente.Direccion = usuario.Direccion;
            usuarioExistente.IdRol = usuario.IdRol;
            usuarioExistente.IdTipoDocumento = usuario.IdTipoDocumento;
            usuarioExistente.FechaActualizado = DateTime.Now;

            // Actualiza la contraseña solo si se envía una nueva en el cuerpo (opcional)
            if (!string.IsNullOrWhiteSpace(usuario.Contraseña))
                usuarioExistente.Contraseña = PasswordHelper.HashPassword(usuario.Contraseña);

            await _context.SaveChangesAsync();
            return Ok("Usuario actualizado exitosamente.");
        }

        /// <summary>
        /// DELETE /api/Usuario/{id} - Elimina el usuario y todas sus dependencias (logs, dispositivos, auditorías, reportes) para evitar errores de FK.
        /// </summary>
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> DeleteUsuario(Guid id)
        {
            var usuario = await _context.Usuarios.FindAsync(id);
            if (usuario == null)
                return NotFound("Usuario no encontrado.");

            // Eliminar en cascada manual: primero registros que referencian al usuario
            var logs = _context.LogsSistema.Where(l => l.IdUsuario == id);
            _context.LogsSistema.RemoveRange(logs);

            var dispositivos = _context.Dispositivos.Where(d => d.IdUsuario == id);
            _context.Dispositivos.RemoveRange(dispositivos);

            var auditorias = _context.AuditoriasNegocio.Where(a => a.RegistradoPor == id);
            _context.AuditoriasNegocio.RemoveRange(auditorias);

            var reportes = _context.Reportes.Where(r => r.GeneradoPor == id);
            _context.Reportes.RemoveRange(reportes);

            _context.Usuarios.Remove(usuario);
            await _context.SaveChangesAsync();
            return Ok("Usuario eliminado exitosamente.");
        }

        /// <summary>
        /// POST /api/Usuario/changePassword - Cambia la contraseña del usuario; exige contraseña actual correcta.
        /// </summary>
        [HttpPost("changePassword")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> CambiarContraseña([FromBody] CambiarContraseñaRequest request)
        {
            var usuario = await _context.Usuarios.FindAsync(request.IdUsuario);
            if (usuario == null)
                return NotFound("Usuario no encontrado.");

            if (string.IsNullOrWhiteSpace(request.NuevaContraseña))
                return BadRequest("La nueva contraseña no puede estar vacía.");

            if (!PasswordHelper.VerifyPassword(request.ContraseñaActual, usuario.Contraseña))
                return BadRequest("La contraseña actual es incorrecta.");

            usuario.Contraseña = PasswordHelper.HashPassword(request.NuevaContraseña);
            usuario.FechaActualizado = DateTime.Now;

            await _context.SaveChangesAsync();
            return Ok("Contraseña actualizada exitosamente.");
        }
    }
}