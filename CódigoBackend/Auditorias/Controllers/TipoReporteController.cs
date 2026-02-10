using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

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
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<Tipo_Reporte>>> GetTiposReporte()
        {
            try
            {
                var tiposReporte = await _context.Tipo_Reporte
                    .Where(t => !t.IsDeleted) // Soft delete
                    .Select(t => new
                    {
                        t.Id,
                        t.Nombre,
                        t.FechaCreado,
                        t.FechaActualizado
                    })
                    .ToListAsync();

                if (!tiposReporte.Any())
                    return NotFound("No se encontraron tipos de reporte activos.");

                return Ok(tiposReporte);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al obtener los tipos de reporte: {ex.Message}");
            }
        }

        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<Tipo_Reporte>> GetTipoReporteById(Guid id)
        {
            try
            {
                var tipoReporte = await _context.Tipo_Reporte
                    .Where(t => t.Id == id && !t.IsDeleted)
                    .FirstOrDefaultAsync();

                if (tipoReporte == null)
                    return NotFound("Tipo de reporte no encontrado.");

                return Ok(tipoReporte);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al obtener el tipo de reporte: {ex.Message}");
            }
        }

        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<Tipo_Reporte>> CreateTipoReporte([FromBody] Tipo_Reporte objetoTipoReporte)
        {
            try
            {
                if (objetoTipoReporte == null)
                    return BadRequest("Datos inválidos.");

                if (string.IsNullOrWhiteSpace(objetoTipoReporte.Nombre))
                    return BadRequest("El nombre del tipo de reporte es obligatorio.");

                objetoTipoReporte.Id = Guid.NewGuid();
                objetoTipoReporte.FechaCreado = DateTime.Now;
                objetoTipoReporte.IsDeleted = false;

                _context.Tipo_Reporte.Add(objetoTipoReporte);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoReporteById), new { id = objetoTipoReporte.Id }, objetoTipoReporte);
            }
            catch (DbUpdateException dbEx)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Error al guardar en la base de datos: {dbEx.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al crear el tipo de reporte: {ex.Message}");
            }
        }

        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> UpdateTipoReporte(Guid id, [FromBody] Tipo_Reporte objetoModificadoTipoReporte)
        {
            try
            {
                if (objetoModificadoTipoReporte == null || id != objetoModificadoTipoReporte.Id)
                    return BadRequest("El objeto enviado es nulo o el id no coincide.");

                if (string.IsNullOrWhiteSpace(objetoModificadoTipoReporte.Nombre))
                    return BadRequest("El nombre del tipo de reporte es obligatorio.");

                var tipoReporteExistente = await _context.Tipo_Reporte.FindAsync(id);
                if (tipoReporteExistente == null || tipoReporteExistente.IsDeleted)
                    return NotFound("Tipo de reporte no encontrado.");

                tipoReporteExistente.Nombre = objetoModificadoTipoReporte.Nombre;
                tipoReporteExistente.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();

                return Ok(tipoReporteExistente);
            }
            catch (DBConcurrencyException)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Error al actualizar en la base de datos: {dbEx.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al actualizar el tipo de reporte: {ex.Message}");
            }
        }

        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> DeleteTipoReporte(Guid id)
        {
            try
            {
                var tipoReporte = await _context.Tipo_Reporte.FindAsync(id);
                if (tipoReporte == null || tipoReporte.IsDeleted)
                    return NotFound("Tipo de reporte no encontrado.");

                tipoReporte.IsDeleted = true;
                tipoReporte.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();

                return Ok("Tipo de reporte eliminado correctamente (Soft Delete).");
            }
            }
            catch (Exception )
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al eliminar el tipo de reporte: {ex.Message}");
            }
        }
    }
}
