// Ruta: /api/Dispositivo
// Propósito: Gestión completa de dispositivos (e.g., IoT, endpoints, sensores).
using System.Data;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class DispositivoController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public DispositivoController(AuditoriaContext context)
        {
            _context = context;
        }

        //Agregar listar Dispositivos
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<object>>> GetAuditoriasAsync()
        {
            try
            {
                var results = await _context.Dispositivos
                .Include(r => r.TipoDispositivo)
                .Include(r => r.Usuario)
                .Select(r => new
                {
                    r.Id,
                    r.Serial,
                    r.Marca,
                    r.Modelo,
                    r.Sistema,
                    r.Descripcion,
                    r.FotoUrl,
                    r.Qr,
                    r.IdTipoDispositivo,
                    r.IdUsuario,
                    r.FechaCreado,
                    r.FechaActualizado,
                    TipoDispositivo = r.TipoDispositivo != null ? r.TipoDispositivo.Nombre : null,
                    usuario = r.Usuario != null ? r.Usuario.Nombres : null
                }).ToListAsync();

                if (results == null || !results.Any())
                    return NotFound("No se encontraron dispositivos");

                return Ok(results);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError);
            }
        }

        // GET /api/Dispositivo/{id}
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> GetDispositivoById(Guid id)
        {
            var dispositivo = await _context.Dispositivos
            .Include(d => d.TipoDispositivo)
            .Include(d => d.Usuario)
            .Where(d => d.Id == id)
            .Select(d => new
            {
                d.Id,
                d.Serial,
                d.Marca,
                d.Modelo,
                d.Sistema,
                d.Descripcion,
                d.FotoUrl,
                d.Qr,
                d.IdTipoDispositivo,
                d.IdUsuario,
                d.FechaCreado,
                d.FechaActualizado,
                TipoDispositivo = d.TipoDispositivo != null ? d.TipoDispositivo.Nombre : null,
                usuario = d.Usuario != null ? d.Usuario.Nombres : null
            }).FirstOrDefaultAsync();


            if (dispositivo == null)
            {
                return NotFound($"Dispositivo con ID {id} no encontrado.");
            }

            return Ok(dispositivo);
        }

        // POST /api/Crear Dispositivo
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> CreateDispositivo([FromBody] Dispositivo dispositivo)
        {
            if (dispositivo == null)
            {
                return BadRequest("Datos Invalidos");
            }

            try
            {

                dispositivo.Id = Guid.NewGuid();
                dispositivo.FechaCreado = DateTime.Now;

                _context.Dispositivos.Add(dispositivo);
                await _context.SaveChangesAsync();

            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar crear el registro");
            }

            var dipositivoCreado = await _context.Dispositivos
                .Include(d => d.TipoDispositivo)
                .Include(d => d.Usuario)
                .Where(d => d.Id == dispositivo.Id)
                .Select(d => new
                {
                    d.Id,
                    d.Serial,
                    d.Marca,
                    d.Modelo,
                    d.Sistema,
                    d.Descripcion,
                    d.FotoUrl,
                    d.Qr,
                    d.IdTipoDispositivo,
                    d.IdUsuario,
                    d.FechaCreado,
                    d.FechaActualizado,
                    TipoDispositivo = d.TipoDispositivo != null ? d.TipoDispositivo.Nombre : null,
                    usuario = d.Usuario != null ? d.Usuario.Nombres : null
                }).FirstOrDefaultAsync();

            return CreatedAtAction(nameof(GetDispositivoById), new { id = dispositivo.Id }, dipositivoCreado);
        }

        // PUT /api/Dispositivo/{id}
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> updateDispositivo(Guid id, [FromBody] Dispositivo dispositivoModificado)
        {

            if (dispositivoModificado == null || id != dispositivoModificado.Id)
            {
                return BadRequest("El objeto enviado es nulo o el id no coincide");
            }

            var dispoExiste = await _context.Dispositivos.FindAsync(id);

            if (dispoExiste == null)
            {
                return NotFound($"No se ha encontrado el registro en la tabla Dispositivos con el id {id}");
            }

            dispositivoModificado.FechaActualizado = DateTime.Now;

            _context.Entry(dispoExiste).CurrentValues.SetValues(dispositivoModificado); // toma el dbset existente y reemplaza los valores con los del objeto modificado

            try
            {
                await _context.SaveChangesAsync();
                return Ok("Dispositivo actualizado exitosamente");
            }
            catch (DBConcurrencyException)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error de concurrencia al intentar actualizar el registro");
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar actualizar el registro");
            }

        }

        // DELETE /api/Dispositivo/{id}
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult> DeleteDispositivo(Guid id)
        {
            var dispo = await _context.Dispositivos.FindAsync(id);
            if (dispo == null)
            {
                return NotFound($"No se ha encontrado el registro en la tabla Dispositivos con el id {id}");
            }

            try
            {
                _context.Dispositivos.Remove(dispo);
                await _context.SaveChangesAsync();

                return Ok($"El dispositivo con id {id} ha sido eliminado exitosamente.");

            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar eliminar el registro");
            }
        }
    }
}