using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;
using Auditorias.utils;

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

        [HttpGet]
        public async Task<ActionResult<IEnumerable<TipoReporte>>> GetTiposReporte()
        {
            var tipos = await _context.TipoReportes.ToListAsync();
            if (!tipos.Any())
                return NotFound("No se encontraron tipos de reporte.");

            return Ok(tipos);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<TipoReporte>> GetTipoReporteById(Guid id)
        {
            var tipo = await _context.TipoReportes.FindAsync(id);
            if (tipo == null)
                return NotFound("Tipo de reporte no encontrado.");

            return Ok(tipo);
        }

        [HttpPost]
        public async Task<ActionResult<TipoReporte>> CreateTipoReporte([FromBody] TipoReporte tipoReporte)
        {
            tipoReporte.Id = Guid.NewGuid();
            _context.TipoReportes.Add(tipoReporte);
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetTipoReporteById), new { id = tipoReporte.Id }, tipoReporte);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateTipoReporte(Guid id, [FromBody] TipoReporte tipoReporte)
        {
            if (id != tipoReporte.Id)
                return BadRequest("El ID no coincide.");

            var existente = await _context.TipoReportes.FindAsync(id);
            if (existente == null)
                return NotFound("Tipo de reporte no encontrado.");

            existente.Nombre = tipoReporte.Nombre;

            await _context.SaveChangesAsync();
            return Ok("Tipo de reporte actualizado correctamente.");
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteTipoReporte(Guid id)
        {
            var tipo = await _context.TipoReportes.FindAsync(id);
            if (tipo == null)
                return NotFound("Tipo de reporte no encontrado.");

            _context.TipoReportes.Remove(tipo);
            await _context.SaveChangesAsync();

            return Ok("Tipo de reporte eliminado correctamente.");
        }
    }
}
