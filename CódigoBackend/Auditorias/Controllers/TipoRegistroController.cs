using Microsoft.AspNetCore.Mvc;
using Auditorias.Models;
using Auditorias.IServices;
using System;
using System.Threading.Tasks;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class TipoRegistroController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public TipoRegistroController(AuditoriaContext context)
        {
            _context = context;
        }

        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<IActionResult> Get()
        {
            try
            {
                var data = await _service.GetAll();
                return Ok(data);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error interno del servidor: {ex.Message}");
            }
        }

        [HttpGet("{id}")]
        public async Task<IActionResult> Get(int id)
        {
            try
            {
                var tipo = await _service.GetById(id);

                if (tipo == null)
                    return NotFound($"No existe un tipo de registro con ID {id}");

                return Ok(tipo);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error interno del servidor: {ex.Message}");
            }
        }

        [HttpPost]
        public async Task<IActionResult> Post([FromBody] TipoRegistro tipo)
        {
            try
            {
                if (!ModelState.IsValid)
                    return BadRequest(ModelState);

                var nuevo = await _service.Add(tipo);
                return CreatedAtAction(nameof(Get), new { id = nuevo.Id }, nuevo);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error al crear el registro: {ex.Message}");
            }
        }

        [HttpPut("{id}")]
        public async Task<IActionResult> Put(int id, [FromBody] TipoRegistro tipo)
        {
            try
            {
                if (!ModelState.IsValid)
                    return BadRequest(ModelState);

                var actualizado = await _service.Update(id, tipo);

                if (actualizado == null)
                    return NotFound($"No existe un tipo de registro con ID {id}");

                return Ok(actualizado);
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error al actualizar el registro: {ex.Message}");
            }
        }

        [HttpDelete("{id}")]
        public async Task<IActionResult> Delete(int id)
        {
            try
            {
                var eliminado = await _service.Delete(id);

                if (!eliminado)
                    return NotFound($"No existe un tipo de registro con ID {id}");

                return NoContent();
            }
            catch (Exception ex)
            {
                return StatusCode(500, $"Error al eliminar el registro: {ex.Message}");
            }
        }
    }
}
