using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class TipoRegistroController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoRegistroController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET
        [HttpGet]
        public async Task<ActionResult<IEnumerable<object>>> GetTiposRegistro()
        {
            try
            {
                var data = await _context.TiposRegistro
                    .Include(tr => tr.TipoDocumento)
                    .Select(tr => new
                    {
                        tr.Id,
                        tr.Nombre,
                        tr.Descripcion,
                        tr.FechaCreado,
                        tr.FechaActualizado,
                        TipoDocumento = tr.TipoDocumento != null ? tr.TipoDocumento.Nombre : null
                    })
                    .ToListAsync();

                if (!data.Any())
                    return NotFound("No existen registros en TipoRegistro");

                return Ok(data);
            }
            catch
            {
                return StatusCode(500, "Error obteniendo los tipos de registro");
            }
        }

        // GET BY ID
        [HttpGet("{id}")]
        public async Task<ActionResult<object>> GetTipoRegistro(Guid id)
        {
            try
            {
                var registro = await _context.TiposRegistro
                    .Include(tr => tr.TipoDocumento)
                    .Where(tr => tr.Id == id)
                    .Select(tr => new
                    {
                        tr.Id,
                        tr.Nombre,
                        tr.Descripcion,
                        tr.FechaCreado,
                        tr.FechaActualizado,
                        TipoDocumento = tr.TipoDocumento != null ? tr.TipoDocumento.Nombre : null
                    })
                    .FirstOrDefaultAsync();

                if (registro == null)
                    return NotFound("No se encontró el tipo de registro");

                return Ok(registro);
            }
            catch
            {
                return StatusCode(500, "Error obteniendo el registro");
            }
        }

        // POST
        [HttpPost]
        public async Task<ActionResult<object>> CreateTipoRegistro([FromBody] TipoRegistro obj)
        {
            if (obj == null)
                return BadRequest("El objeto enviado es nulo");

            try
            {
                obj.Id = Guid.NewGuid();
                obj.FechaCreado = DateTime.Now;

                _context.TiposRegistro.Add(obj);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoRegistro), new { id = obj.Id }, obj);
            }
            catch
            {
                return StatusCode(500, "Error creando el tipo de registro");
            }
        }
    }
}



