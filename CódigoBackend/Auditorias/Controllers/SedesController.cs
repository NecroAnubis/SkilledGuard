using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize] // notacion que indica que todos los controladores necesitan un token de autorizacion en los header
    public class SedeController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public SedeController(AuditoriaContext context)
        {
            _context = context;
        }

        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<object>>> GetSedes()
        {
            try
            {
                var sedes = await _context.Sedes
                .Select(u => new 
                {
                    u.Id,
                    u.NombreSede
                }).ToListAsync();
                
                
                if (sedes == null || !sedes.Any())
                {
                    return NotFound("No se han encontrado registros en la tabla Sedes");
                }

                return Ok(sedes);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener la lista");

            }
        }

           
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
                {
                    return NotFound($"No se ha encontrado el registro con id {id}");
                }

                return Ok(sede);
                
            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener la sede");
            }
        }
         

        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult>SedeCrear([FromBody] Sede objetoSede)
        {

            if (objetoSede == null)
            {
                return BadRequest("El objeto enviado es nulo");
            }

            var sedeExistente = await _context.Sedes
                .FirstOrDefaultAsync(s => s.NombreSede.ToLower() == objetoSede.NombreSede.ToLower());

                if (sedeExistente != null)
                {
                    return Conflict($"Ya existe una sede con el nombre '{objetoSede.NombreSede}'.");
                }

            try
            {
                _context.Sedes.Add(objetoSede);
                await _context.SaveChangesAsync();

            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar crear la sede");    
            }

            return CreatedAtAction(nameof(GetSedeById),
                new { id = objetoSede.Id }, objetoSede);
        }

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

            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar actualizar la sede");    
            }

            return Ok(sedeExistente);
        }

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
                var relatedReportes = _context.Reportes.Where(r => r.Sede == id);
                _context.Reportes.RemoveRange(relatedReportes);
                    
                _context.Sedes.Remove(sedeExistente);
                await _context.SaveChangesAsync();

            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar eliminar la sede");    
            }

            return Ok($"La sede con id {id} ha sido eliminada exitosamente.");
        }

    }

}