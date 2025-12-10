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

        public async Task<ActionResult<IEnumerable<Tipo_documento>>> GetTiposDocumento()
        {
            try
            {
                var tipos = await _context.TipoDocumento
                    .Select(t => new
                    {
                        t.Id,
                        t.nombre,
                        t.acronimo,
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
        public async Task<ActionResult<Tipo_documento>> GetTipoDocumentoById(Guid id)
        {
            try
            {
                var tipo = await _context.TipoDocumento
                    .Where(t => t.Id == id)
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .FirstOrDefaultAsync();

                if (tipo == null || tipo.Id == Guid.Empty)
                    return NotFound("Tipo de documento no encontrado.");

                return Ok(tipo);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al obtener el registro solicitado.");
            }
        }

        //  api/TipoDocumento
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<Tipo_documento>> CreateTipoDocumento([FromBody] TipoDocumento objeto_tipo_documento)
        {
            try
            {
                if (objeto_tipo_documento == null)
                
                    return BadRequest("Datos inválidos.");
                

                objeto_tipo_documento.Id = Guid.NewGuid();
                objeto_tipo_documento.FechaCreado = DateTime.Now;

                _context.TipoDocumento.Add(objeto_tipo_documento);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoDocumentoById), new { id = objeto_tipo_documento.Id }, objeto_tipo_documento);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar crear el tipo de documento.");
            }
        }

        // PUT: api/TipoDocumento/{id}
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<IActionResult> UpdateTipoDocumento(Guid id, [FromBody] TipoDocumento objetoModificadoTipoDocumento)
        {
            try
            {
                if (id != objetoModificadoTipoDocumento.Id)
                    return BadRequest("IDs no coinciden.");

                var TipoDocumentoExistente = await _context.TipoDocumento.FindAsync(id);
                if (TipoDocumentoExistente == null)
                    return NotFound("Tipo de documento no encontrado.");

                TipoDocumentoExistente.Nombre = objetoModificadoTipoDocumento.Nombre;
                TipoDocumentoExistente.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();
                return Ok("Tipo de documento actualizado correctamente." TipoDocumentoExistente);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar actualizar el registro.");
            }
        }
    }
}

