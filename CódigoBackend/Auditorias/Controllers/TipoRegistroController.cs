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
    public class TipoRegistroController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoRegistroController(AuditoriaContext context)
        {
            _context = context;
        }

        [HttpGet]
        public async Task<ActionResult<IEnumerable<TipoRegistro>>> GetTiposRegistro()
        {
            var tipos = await _context.TipoRegistros.ToListAsync();
            if (!tipos.Any())
                return NotFound("No se encontraron tipos de registro.");

            return Ok(tipos);
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<TipoRegistro>> GetTipoRegistroById(Guid id)
        {
            var tipo = await _context.TipoRegistros.FindAsync(id);
            if (tipo == null)
                return NotFound("Tipo de registro no encontrado.");

            return Ok(tipo);
        }

        [HttpPost]
        public async Task<ActionResult<TipoRegistro>> CreateTipoRegistro([FromBody] TipoRegistro tipoRegistro)
        {
            tipoRegistro.Id = Guid.NewGuid();
            _context.TipoRegistros.Add(tipoRegistro);
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetTipoRegistroById), new { id = tipoRegistro.Id }, tipoRegistro);
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateTipoRegistro(Guid id, [FromBody] TipoRegistro tipoRegistro)
        {
            if (id != tipoRegistro.Id)
                return BadRequest("El ID no coincide.");

            var existente = await _context.TipoRegistros.FindAsync(id);
            if (existente == null)
                return NotFound("Tipo de registro no encontrado.");

            existente.Nombre = tipoRegistro.Nombre;

            await _context.SaveChangesAsync();
            return Ok("Tipo de registro actualizado correctamente.");
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteTipoRegistro(Guid id)
        {
            var tipo = await _context.TipoRegistros.FindAsync(id);
            if (tipo == null)
                return NotFound("Tipo de registro no encontrado.");

            _context.TipoRegistros.Remove(tipo);
            await _context.SaveChangesAsync();

            return Ok("Tipo de registro eliminado correctamente.");
        }
    }
}
