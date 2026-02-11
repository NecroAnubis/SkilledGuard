using Microsoft.AspNetCore.Mvc;
using Auditorias.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
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

        // GET: api/TipoRegistro
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<Tipo_registro>>> GetTiposRegistro()
        {
            try
            {
                var tipos = await _context.Tipo_registro.ToListAsync();

                if (tipos == null || !tipos.Any())
                    return NotFound("No se han encontrado registros en la tabla Tipo_registro.");

                return Ok(tipos);
            }
            catch (Exception)
            {

                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar obtener la lista de tipos de registro.");
            }
        }

        // GET: api/TipoRegistro/{id}
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<Tipo_registro>>> GetTipoRegistroById(Guid id)
        {
            try
            {
                var tipoRegistroid = await _context.Tipo_registro.FindAsync(id);

                if (tipoRegistroid == null || tipoRegistroid.Id == Guid.Empty)
                {
                    return NotFound($"No existe un tipo de registro con ID {id}");
                }
                return Ok(tipoRegistroid);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al obtener el registro solicitado.");
            }
        }

        // POST: api/TipoRegistro
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<Tipo_registro>> CreateTipoRegistro([FromBody] Tipo_registro objetoTipoRegistro)
{
    try
    {
        if (objetoTipoRegistro == null)
            return BadRequest("Datos inválidos.");

        objetoTipoRegistro.Id = Guid.NewGuid();
        objetoTipoRegistro.FechaCreado = DateTime.Now;

        _context.Tipo_registro.Add(objetoTipoRegistro);
        await _context.SaveChangesAsync();

        return CreatedAtAction(nameof(GetTipoRegistroById), new { id = objetoTipoRegistro.Id }, objetoTipoRegistro);
    }
    catch (Exception)
    {
        return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar crear el registro.");
    }
}


        // PUT: api/TipoRegistro/{id}
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> UpdateTipoRegistro(Guid id, [FromBody] Tipo_registro objetoModificadoTipoRegistro)
        {
            try
            {
                if (objetoModificadoTipoRegistro == null || id != objetoModificadoTipoRegistro.Id)
                {
                    return BadRequest("El objeto enviado es nulo o el id no coincide.");
                }

                var tipoRegistroExistente = await _context.Tipo_registro.FindAsync(id);
                if (tipoRegistroExistente == null)
                {
                    return NotFound($"No se ha encontrado el registro en la tabla Tipo_registro con el id {id}");
                }

                _context.Entry(tipoRegistroExistente).CurrentValues.SetValues(objetoModificadoTipoRegistro);
                await _context.SaveChangesAsync();
                return Ok(tipoRegistroExistente);
            }
            catch (DbUpdateConcurrencyException)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error de concurrencia al intentar actualizar el registro.");
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar actualizar el registro.");
            }
        }

        // DELETE: api/TipoRegistro/{id}
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> DeleteTipoRegistro(Guid id)
        {
            try
            {
                var tipoRegistro = await _context.Tipo_registro.FindAsync(id);
                if (tipoRegistro == null)
                {
                    return NotFound($"No se ha encontrado el registro con id {id}");
                }

                _context.Tipo_registro.Remove(tipoRegistro);
                await _context.SaveChangesAsync();
                return Ok("Registro eliminado correctamente.");
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar eliminar el registro.");
            }
        }
    }
}
