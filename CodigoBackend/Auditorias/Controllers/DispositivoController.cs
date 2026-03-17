// Ruta: /api/Dispositivo
// Propósito: Gestión completa de dispositivos (CRUD: listar, obtener por id, crear, actualizar, eliminar).
using System.Data;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar dispositivos (IoT, endpoints, sensores).
    /// Todas las operaciones usan el contexto de BD inyectado.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize]
    public class DispositivoController : ControllerBase
    {
        // Contexto de Entity Framework para acceder a Dispositivos y relaciones (TipoDispositivo, Usuario)
        private readonly AuditoriaContext _context;

        // Inyección de dependencias: recibe el contexto en el constructor
        public DispositivoController(AuditoriaContext context)
        {
            _context = context;
        }

        /// <summary>
        /// GET /api/Dispositivo - Lista todos los dispositivos con TipoDispositivo y nombre del Usuario.
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<object>>> GetDispositivos()
        {
            try
            {
                // Incluye TipoDispositivo y Usuario para devolver nombres en la respuesta
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

                // Si no hay registros, se responde 404
                if (results == null || !results.Any())
                    return NotFound("No se encontraron dispositivos");

                return Ok(results);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError);
            }
        }

        /// <summary>
        /// GET /api/Dispositivo/{id} - Obtiene un dispositivo por su ID con TipoDispositivo y Usuario.
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> GetDispositivoById(Guid id)
        {
            // Busca por id e incluye relaciones para devolver nombres en el objeto anónimo
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
                return NotFound($"Dispositivo con ID {id} no encontrado.");

            return Ok(dispositivo);
        }

        /// <summary>
        /// POST /api/Dispositivo - Crea un nuevo dispositivo (Id y FechaCreado se asignan aquí).
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<object>> CreateDispositivo([FromBody] Dispositivo dispositivo)
        {
            if (dispositivo == null)
                return BadRequest("Datos Invalidos");

            try
            {
                // Asignación de Id único y fecha de creación antes de guardar
                dispositivo.Id = Guid.NewGuid();
                dispositivo.FechaCreado = DateTime.Now;

                _context.Dispositivos.Add(dispositivo);
                await _context.SaveChangesAsync();
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar crear el registro");
            }

            // Se vuelve a consultar el dispositivo creado con sus relaciones para devolverlo en la respuesta (201 Created)
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

        /// <summary>
        /// PUT /api/Dispositivo/{id} - Actualiza un dispositivo existente; actualiza FechaActualizado.
        /// </summary>
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> updateDispositivo(Guid id, [FromBody] Dispositivo dispositivoModificado)
        {

            if (dispositivoModificado == null || id != dispositivoModificado.Id)
                return BadRequest("El objeto enviado es nulo o el id no coincide");

            var dispoExiste = await _context.Dispositivos.FindAsync(id);
            if (dispoExiste == null)
                return NotFound($"No se ha encontrado el registro en la tabla Dispositivos con el id {id}");

            // Marca la fecha de última actualización
            dispositivoModificado.FechaActualizado = DateTime.Now;
            // Toma la entidad existente en el DbSet y reemplaza sus valores con los del objeto recibido
            _context.Entry(dispoExiste).CurrentValues.SetValues(dispositivoModificado);

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

        /// <summary>
        /// DELETE /api/Dispositivo/{id} - Elimina un dispositivo por ID.
        /// </summary>
        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult> DeleteDispositivo(Guid id)
        {
            var dispo = await _context.Dispositivos.FindAsync(id);
            if (dispo == null)
                return NotFound($"No se ha encontrado el registro en la tabla Dispositivos con el id {id}");

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