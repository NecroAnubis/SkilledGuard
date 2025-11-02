using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TipoAccionController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoAccionController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET: api/tipoaccion
        [HttpGet]
        public async Task<ActionResult<IEnumerable<TipoAccion>>> GetTipoAcciones()
        {
            var acciones = await _context.TipoAcciones.ToListAsync();
            return Ok(acciones);
        }
    }
}
