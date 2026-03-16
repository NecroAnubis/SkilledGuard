// Ruta: /api/TipoReporte
// Propósito: CRUD de tipos de reporte con soft delete (IsDeleted). Requiere token JWT.
using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;
using System;
using System.Collections.Generic;
using System.Data;
using System.Linq;
using System.Threading.Tasks;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar tipos de reporte (listar, obtener por id, crear, actualizar, eliminar).
    /// La eliminación es lógica (soft delete): se marca IsDeleted = true en lugar de borrar el registro.
    /// </summary>
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

        /// <summary>
        /// GET /api/TipoReporte - Lista solo tipos de reporte no eliminados (Where !IsDeleted).
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<TipoReporte>>> GetTiposReporte()
        {
            try
            {
                // Filtra registros con soft delete: solo se muestran los que no están marcados como eliminados
                var tiposReporte = await _context.TiposReporte
                    .Where(t => !t.IsDeleted)
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

        /// <summary>
        /// GET /api/TipoReporte/{id} - Obtiene un tipo de reporte por ID (solo si no está eliminado).
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<TipoReporte>> GetTipoReporteById(Guid id)
        {
            try
            {
                var tipoReporte = await _context.TiposReporte
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

        /// <summary>
        /// POST /api/TipoReporte - Crea un nuevo tipo de reporte (Id, FechaCreado, IsDeleted = false se asignan aquí).
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<TipoReporte>> CreateTipoReporte([FromBody] TipoReporte objetoTipoReporte)
        {
            try
            {
                if (objetoTipoReporte == null)
                    return BadRequest("Datos inválidos.");

                if (string.IsNullOrWhiteSpace(objetoTipoReporte.Nombre))
                    return BadRequest("El nombre del tipo de reporte es obligatorio.");

                objetoTipoReporte.Id = Guid.NewGuid();
                objetoTipoReporte.FechaCreado = DateTime.Now;
                objetoTipoReporte.IsDeleted = false; // Registro activo por defecto

                _context.TiposReporte.Add(objetoTipoReporte);
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

        /// <summary>
        /// PUT /api/TipoReporte/{id} - Actualiza el nombre y FechaActualizado de un tipo de reporte (solo no eliminados).
        /// </summary>
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> UpdateTipoReporte(Guid id, [FromBody] TipoReporte objetoModificadoTipoReporte)
        {
            try
            {
                if (objetoModificadoTipoReporte == null || id != objetoModificadoTipoReporte.Id)
                    return BadRequest("El objeto enviado es nulo o el id no coincide.");

                if (string.IsNullOrWhiteSpace(objetoModificadoTipoReporte.Nombre))
                    return BadRequest("El nombre del tipo de reporte es obligatorio.");

                var tipoReporteExistente = await _context.TiposReporte.FindAsync(id);
                if (tipoReporteExistente == null || tipoReporteExistente.IsDeleted)
                    return NotFound("Tipo de reporte no encontrado.");

                tipoReporteExistente.Nombre = objetoModificadoTipoReporte.Nombre;
                tipoReporteExistente.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();
                return Ok(tipoReporteExistente);
            }
            catch (DBConcurrencyException dbEx)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Error de concurrencia al actualizar: {dbEx.Message}");
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al actualizar el tipo de reporte: {ex.Message}");
            }
        }

        /// <summary>
        /// DELETE /api/TipoReporte/{id} - Soft delete: marca IsDeleted = true y actualiza FechaActualizado (no borra el registro).
        /// </summary>
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> DeleteTipoReporte(Guid id)
        {
            try
            {
                var tipoReporte = await _context.TiposReporte.FindAsync(id);
                if (tipoReporte == null || tipoReporte.IsDeleted)
                    return NotFound("Tipo de reporte no encontrado.");

                // Soft delete: no se elimina de la BD, solo se marca como eliminado
                tipoReporte.IsDeleted = true;
                tipoReporte.FechaActualizado = DateTime.Now;

                await _context.SaveChangesAsync();
                return Ok("Tipo de reporte eliminado correctamente (Soft Delete).");
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Ocurrió un error al eliminar el tipo de reporte: {ex.Message}");
            }
        }
    }
}
