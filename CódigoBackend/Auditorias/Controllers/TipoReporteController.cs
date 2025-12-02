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
    public class TipoReporteController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoReporteController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET
        [HttpGet]
        public async Task<ActionResult<IEnumerable<object>>> GetTiposReporte()
        {
            try
            {
                var data = await _context.TiposReporte
                    .Include(tp => tp.TipoRegistro)
                    .Select(tp => new
                    {
                        tp.Id,
                        tp.Nombre,
                        tp.Descripcion,
                        tp.FechaCreado,
                        tp.FechaActualizado,
                        TipoRegistro = tp.TipoRegistro != null ? tp.TipoRegistro.Nombre : null
                    })
                    .ToListAsync();

                if (!data.Any())
                    return NotFound("No existen registros en TipoReporte");

                return Ok(data);
            }
            catch
            {
                return StatusCode(500, "Error obteniendo los tipos de reporte");
            }
        }

        // GET BY ID
        [HttpGet("{id}")]
        public async Task<ActionResult<object>> GetTipoReporte(Guid id)
        {
            try
            {
                var reporte = await _context.TiposReporte
                    .Include(tp => tp.TipoRegistro)
                    .Where(tp => tp.Id == id)
                    .Select(tp => new
                    {
                        tp.Id,
                        tp.Nombre,
                        tp.Descripcion,
                        tp.FechaCreado,
                        tp.FechaActualizado,
                        TipoRegistro = tp.TipoRegistro != null ? tp.TipoRegistro.Nombre : null
                    })
                    .FirstOrDefaultAsync();

                if (reporte == null)
                    return NotFound("No se encontró el tipo de reporte");

                return Ok(reporte);
            }
            catch
            {
                return StatusCode(500, "Error obteniendo el registro");
            }
        }

        // POST
        [HttpPost]
        public async Task<ActionResult<object>> CreateTipoReporte([FromBody] TipoReporte obj)
        {
            if (obj == null)
                return BadRequest("El objeto enviado es nulo");

            try
            {
                obj.Id = Guid.NewGuid();
                obj.FechaCreado = DateTime.Now;

                _context.TiposReporte.Add(obj);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoReporte), new { id = obj.Id }, obj);
            }
            catch
            {
                return StatusCode(500, "Error creando el tipo de reporte");
            }
        }
    }
}
