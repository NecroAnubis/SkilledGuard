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
    public class TipoDocumentoController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoDocumentoController(AuditoriaContext context)
        {
            _context = context;
        }

        //  api/TipoDocumento
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<object>>> GetTiposDocumento()
        {
            try
            {
                var tipos = await _context.TipoDocumentos
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .ToListAsync();

                if (!tipos.Any())
                    return NotFound("No se encontraron tipos de documento.");

                return Ok(tipos);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al obtener los tipos de documento.");
            }
        }

        //  api/TipoDocumento/{id}
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> GetTipoDocumentoById(Guid id)
        {
            try
            {
                var tipo = await _context.TipoDocumentos
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
                    return NotFound("Tipo de documento no encontrado.");

                return Ok(tipo);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al obtener el registro solicitado.");
            }
        }

        //  api/TipoDocumento
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> CreateTipoDocumento([FromBody] TipoDocumento tipo)
        {
            try
            {
                if (tipo == null)
                    return BadRequest("Datos inválidos.");

                tipo.Id = Guid.NewGuid();
                tipo.FechaCreado = DateTime.Now;

                _context.TipoDocumentos.Add(tipo);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoDocumentoById), new { id = tipo.Id }, tipo);
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al intentar crear el tipo de documento.");
            }
        }

        // PUT: api/TipoDocumento/{id}
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> UpdateTipoDocumento(Guid id, [FromBody] TipoDocumento tipo)
        {
            try
            {
                if (id != tipo.Id)
                    return BadRequest("IDs no coinciden.");

                var existente = await _context.TipoDocumentos.FindAsync(id);
                if (existente == null)
                    return NotFound("Tipo de documento no encontrado.");

                existente.Nombre = tipo.Nombre;
                existente.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();
                return Ok("Tipo de documento actualizado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al intentar actualizar el registro.");
            }
        }

        // DELETE: api/TipoDocumento/{id}
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> DeleteTipoDocumento(Guid id)
        {
            try
            {
                var tipo = await _context.TipoDocumentos.FindAsync(id);
                if (tipo == null)
                    return NotFound("Tipo de documento no encontrado.");

               
                var usuarios = _context.Usuarios.Where(u => u.IdTipoDocumento == id);
                _context.Usuarios.RemoveRange(usuarios);

                _context.TipoDocumentos.Remove(tipo);
                await _context.SaveChangesAsync();

                return Ok("Tipo de documento eliminado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(500, "Ocurrió un error al intentar eliminar el tipo de documento.");
            }
        }
    }
}

