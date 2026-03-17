// Ruta: /api/LogSistema
// Propósito: Consulta de logs de nivel de sistema (errores, advertencias, info).
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para consultar logs del sistema.
    /// Expone un endpoint GET por id para obtener un log específico.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class LogSistemaController : ControllerBase
    {
        // Contexto de BD para acceder a la tabla LogsSistema
        private readonly AuditoriaContext _context;

        // Inyección del contexto en el constructor
        public LogSistemaController(AuditoriaContext context)
        {
            _context = context;
        }

        /// <summary>
        /// GET /api/LogSistema/{id} - Obtiene un log de sistema por su identificador (Guid).
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<LogSistema>> GetLogsSistema(Guid id)
        {
            // Busca el log por clave primaria
            var log = await _context.LogsSistema.FindAsync(id);

            if (log == null)
                return NotFound();

            return Ok(log);
        }
    }
}