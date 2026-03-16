// Ruta: /api/TipoDocumento
// Propósito: CRUD de tipos de documento (ej. CC, NIT, Pasaporte). Requiere token JWT.
using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar tipos de documento (listar, obtener por id, crear, actualizar).
    /// Requiere autorización por token.
    /// </summary>
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

        /// <summary>
        /// GET /api/TipoDocumento - Lista todos los tipos de documento (Id, Nombre, Acronimo).
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<IEnumerable<TipoDocumento>>> GetTiposDocumento()
        {
            try
            {
                var tipos = await _context.TipoDocumentos
                    .Select(t => new { t.Id, t.Nombre, t.Acronimo })
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

        /// <summary>
        /// GET /api/TipoDocumento/{id} - Obtiene un tipo de documento por su ID.
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<TipoDocumento>> GetTipoDocumentoById(Guid id)
        {
            try
            {
                var tipo = await _context.TipoDocumentos.FindAsync(id);
                if (tipo == null)
                    return NotFound("Tipo de documento no encontrado.");

                return Ok(tipo);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al obtener el registro solicitado.");
            }
        }

        /// <summary>
        /// POST /api/TipoDocumento - Crea un nuevo tipo de documento (Id se genera con Guid.NewGuid()).
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<TipoDocumento>> CreateTipoDocumento([FromBody] TipoDocumento objeto_tipo_documento)
        {
            try
            {
                if (objeto_tipo_documento == null)
                    return BadRequest("Datos inválidos.");

                objeto_tipo_documento.Id = Guid.NewGuid();
                _context.TipoDocumentos.Add(objeto_tipo_documento);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoDocumentoById), new { id = objeto_tipo_documento.Id }, objeto_tipo_documento);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar crear el tipo de documento.");
            }
        }

        /// <summary>
        /// PUT /api/TipoDocumento/{id} - Actualiza Nombre y Acronimo de un tipo de documento existente.
        /// </summary>
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

                var TipoDocumentoExistente = await _context.TipoDocumentos.FindAsync(id);
                if (TipoDocumentoExistente == null)
                    return NotFound("Tipo de documento no encontrado.");

                // Actualiza solo Nombre y Acronimo
                TipoDocumentoExistente.Nombre = objetoModificadoTipoDocumento.Nombre;
                TipoDocumentoExistente.Acronimo = objetoModificadoTipoDocumento.Acronimo;

                await _context.SaveChangesAsync();
                return Ok(TipoDocumentoExistente);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar actualizar el registro.");
            }
        }
    }
}

