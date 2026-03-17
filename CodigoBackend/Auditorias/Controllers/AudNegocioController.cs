// Ruta: GET /api/AuditoriaNegocio
// Propósito: Consultar logs de negocio (auditorías a nivel de negocio).
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para consultar auditorías de negocio.
    /// Expone un único endpoint GET que devuelve todos los registros de auditoría.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class AuditoriaNegocioController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public AuditoriaNegocioController(AuditoriaContext context)
        {
            _context = context;
        }

        /// <summary>
        /// GET /api/AuditoriaNegocio - Obtiene la lista completa de auditorías de negocio.
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        public async Task<ActionResult<IEnumerable<AuditoriaNegocio>>> GetAuditorias()
        {
            try
            {
                var results = await _context.AuditoriasNegocio.ToListAsync();
                return Ok(results);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError);
            }
        }
    }
}