using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;

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
                var tipos = await _context.TipoReportes
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .ToListAsync();

                if (!tipos.Any())
                    return NotFound("No se encontraron tipos de reporte.");

                return Ok(tipos);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al obtener los tipos de reporte.");
            }
        }

        // GET por ID
        [HttpGet("{id}")]
        public async Task<ActionResult<object>> GetTipoReporteById(Guid id)
        {
            try
            {
                var tipo = await _context.TipoReportes
                    .Where(t => t.Id == id)
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .FirstOrDefaultAsync();

                if (tipo == null)
                    return NotFound("Tipo de reporte no encontrado.");

                return Ok(tipo);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al obtener el tipo de reporte.");
            }
        }

        // POST
        [HttpPost]
        public async Task<ActionResult<object>> CreateTipoReporte([FromBody] TipoReporte tipo)
        {
            try
            {
                if (tipo == null)
                    return BadRequest("Datos inválidos.");

                tipo.Id = Guid.NewGuid();
                tipo.FechaCreado = DateTime.Now;

                _context.TipoReportes.Add(tipo);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoReporteById), new { id = tipo.Id }, tipo);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al crear el tipo de reporte.");
            }
        }

        // PUT
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateTipoReporte(Guid id, [FromBody] TipoReporte tipo)
        {
            try
            {
                if (id != tipo.Id)
                    return BadRequest("Los IDs no coinciden.");

                var existente = await _context.TipoReportes.FindAsync(id);
                if (existente == null)
                    return NotFound("Tipo de reporte no encontrado.");

                existente.Nombre = tipo.Nombre;
                existente.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();

                return Ok("Tipo de reporte actualizado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al actualizar el tipo de reporte.");
            }
        }

        // DELETE
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteTipoReporte(Guid id)
        {
            try
            {
                var tipo = await _context.TipoReportes.FindAsync(id);
                if (tipo == null)
                    return NotFound("Tipo de reporte no encontrado.");
                    
                var reportes = _context.Reportes.Where(r => r.IdTipoReporte == id);
                _context.Reportes.RemoveRange(reportes);

                _context.TipoReportes.Remove(tipo);
                await _context.SaveChangesAsync();

                return Ok("Tipo de reporte eliminado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al eliminar el tipo de reporte.");
            }
        }
    }
}
