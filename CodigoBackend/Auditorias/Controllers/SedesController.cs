// Ruta: /api/Sede
// Propósito: CRUD de sedes. Requiere token JWT. No permite nombres duplicados; al eliminar se borran reportes asociados.
using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar sedes (listar, obtener por id, crear, actualizar, eliminar).
    /// Requiere token. Al eliminar una sede se eliminan los reportes asociados.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize] // Todos los endpoints requieren token JWT en el header
    public class SedeController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public SedeController(AuditoriaContext context)
        {
            _context = context;
        }

        /// <summary>
        /// GET /api/Sede - Lista todas las sedes (Id y NombreSede).
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<object>>> GetSedes()
        {
            try
            {
                var sedes = await _context.Sedes
                    .Select(u => new { u.Id, u.NombreSede })
                    .ToListAsync();

                if (sedes == null || !sedes.Any())
                    return NotFound("No se han encontrado registros en la tabla Sedes");

                return Ok(sedes);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener la lista");
            }
        }

        /// <summary>
        /// GET /api/Sede/{id} - Obtiene una sede por su ID.
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<object>> GetSedeById (Guid id)
        {
            try
            {
                var sede = await _context.Sedes
                .Where(s => s.Id == id)
                .Select(s => new 
                {
                    s.Id,
                    s.NombreSede
                }).FirstOrDefaultAsync();

                if (sede == null || sede.Id == Guid.Empty)
                    return NotFound($"No se ha encontrado el registro con id {id}");

                return Ok(sede);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener la sede");
            }
        }

        /// <summary>
        /// POST /api/Sede - Crea una nueva sede. No permite nombre duplicado (insensible a mayúsculas).
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult>SedeCrear([FromBody] Sede objetoSede)
        {

            if (objetoSede == null)
                return BadRequest("El objeto enviado es nulo");

            // Validación: no permitir nombre duplicado (comparación insensible a mayúsculas)
            var sedeExistente = await _context.Sedes
                .FirstOrDefaultAsync(s => s.NombreSede.ToLower() == objetoSede.NombreSede.ToLower());
            if (sedeExistente != null)
                return Conflict($"Ya existe una sede con el nombre '{objetoSede.NombreSede}'.");

            try
            {
                _context.Sedes.Add(objetoSede);
                await _context.SaveChangesAsync();
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar crear la sede");
            }

            return CreatedAtAction(nameof(GetSedeById), new { id = objetoSede.Id }, objetoSede);
        }

        /// <summary>
        /// PUT /api/Sede/{id} - Actualiza el nombre de una sede existente.
        /// </summary>
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult>ActualizarSede(Guid id, [FromBody] Sede objetoSede)
        {

            if (objetoSede == null || id != objetoSede.Id)
            {
                return BadRequest("El objeto enviado es nulo o el id no coincide");
            }

            var sedeExistente = await _context.Sedes.FindAsync(id);

            if (sedeExistente == null)
            {
                return NotFound($"No se ha encontrado la sede con id {id}");
            }

            try
            {
                sedeExistente.NombreSede = objetoSede.NombreSede;
                _context.Sedes.Update(sedeExistente);
                await _context.SaveChangesAsync();
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar actualizar la sede");
            }

            return Ok(sedeExistente);
        }

        /// <summary>
        /// DELETE /api/Sede/{id} - Elimina la sede y todos los reportes que la referencian.
        /// </summary>
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult>EliminarSede(Guid id)
        {

            var sedeExistente =  await _context.Sedes.FindAsync(id);

            if (sedeExistente == null)
            {
                return NotFound($"No se ha encontrado la sede con id {id}");
            }

            try
            {
                // Eliminar primero los reportes que referencian esta sede para evitar violación de FK
                var relatedReportes = _context.Reportes.Where(r => r.Sede == id);
                _context.Reportes.RemoveRange(relatedReportes);
                _context.Sedes.Remove(sedeExistente);
                await _context.SaveChangesAsync();
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar eliminar la sede");
            }

            return Ok($"La sede con id {id} ha sido eliminada exitosamente.");
        }

    }

}