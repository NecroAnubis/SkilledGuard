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
    public class TipoRegistroController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoRegistroController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET: api/tiporegistro
        [HttpGet]
        public async Task<ActionResult<IEnumerable<object>>> GetTiposRegistro()
        {
            try
            {
                var tipos = await _context.TipoRegistros
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .ToListAsync();

                if (!tipos.Any())
                    return NotFound("No se encontraron tipos de registro.");

                return Ok(tipos);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al obtener los tipos de registro.");
            }
        }

        // GET: api/tiporegistro/{id}
        [HttpGet("{id}")]
        public async Task<ActionResult<object>> GetTipoRegistroById(Guid id)
        {
            try
            {
                var tipo = await _context.TipoRegistros
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
                    return NotFound("Tipo de registro no encontrado.");

                return Ok(tipo);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al obtener el tipo de registro.");
            }
        }

        // POST: api/tiporegistro
        [HttpPost]
        public async Task<ActionResult<object>> CreateTipoRegistro([FromBody] TipoRegistro tipo)
        {
            try
            {
                if (tipo == null)
                    return BadRequest("Datos inválidos.");

                tipo.Id = Guid.NewGuid();
                tipo.FechaCreado = DateTime.Now;

                _context.TipoRegistros.Add(tipo);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoRegistroById), new { id = tipo.Id }, tipo);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al crear el tipo de registro.");
            }
        }

        // PUT: api/tiporegistro/{id}
        [HttpPut("{id}")]
        public async Task<IActionResult> UpdateTipoRegistro(Guid id, [FromBody] TipoRegistro tipo)
        {
            try
            {
                if (id != tipo.Id)
                    return BadRequest("Los IDs no coinciden.");

                var existente = await _context.TipoRegistros.FindAsync(id);
                if (existente == null)
                    return NotFound("Tipo de registro no encontrado.");

                existente.Nombre = tipo.Nombre;
                existente.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();

                return Ok("Tipo de registro actualizado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al actualizar el tipo de registro.");
            }
        }

        // DELETE: api/tiporegistro/{id}
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteTipoRegistro(Guid id)
        {
            try
            {
                var tipo = await _context.TipoRegistros.FindAsync(id);
                if (tipo == null)
                    return NotFound("Tipo de registro no encontrado.");

            
                var auditorias = _context.AuditoriasNegocio.Where(a => a.IdTipoRegistro == id);
                _context.AuditoriasNegocio.RemoveRange(auditorias);

                _context.TipoRegistros.Remove(tipo);
                await _context.SaveChangesAsync();

                return Ok("Tipo de registro eliminado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al eliminar el tipo de registro.");
            }
        }
    }
}




