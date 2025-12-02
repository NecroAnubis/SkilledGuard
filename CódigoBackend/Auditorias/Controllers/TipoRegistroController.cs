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
    public class TipoDocumentoController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoDocumentoController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET
        [HttpGet]
        public async Task<ActionResult<IEnumerable<object>>> GetTiposDocumento()
        {
            try
            {
                var data = await _context.TiposDocumento
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.Descripcion,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .ToListAsync();

                if (!data.Any())
                    return NotFound("No existen registros en TipoDocumento");

                return Ok(data);
            }
            catch
            {
                return StatusCode(500, "Error obteniendo los tipos de documento");
            }
        }

        // GET BY ID
        [HttpGet("{id}")]
        public async Task<ActionResult<object>> GetTipoDocumento(Guid id)
        {
            try
            {
                var tipo = await _context.TiposDocumento
                    .Where(t => t.Id == id)
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.Descripcion,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .FirstOrDefaultAsync();

                if (tipo == null)
                    return NotFound("No se encontró el tipo de documento");

                return Ok(tipo);
            }
            catch
            {
                return StatusCode(500, "Error obteniendo el registro");
            }
        }

        // POST
        [HttpPost]
        public async Task<ActionResult<object>> CreateTipoDocumento([FromBody] TipoDocumento obj)
        {
            if (obj == null)
                return BadRequest("El objeto enviado es nulo");

            try
            {
                obj.Id = Guid.NewGuid();
                obj.FechaCreado = DateTime.Now;

                _context.TiposDocumento.Add(obj);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoDocumento), new { id = obj.Id }, obj);
            }
            catch
            {
                return StatusCode(500, "Error creando el tipo de documento");
            }
        }
    }
}


