// Ruta: /api/TipoRegistro
// Propósito: CRUD de tipos de registro. Requiere token JWT.
using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using System;
using System.Data;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.Authorization;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar tipos de registro (listar, obtener por id, crear, actualizar).
    /// Requiere autorización por token.
    /// </summary>
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

        /// <summary>
        /// GET /api/TipoRegistro - Lista todos los tipos de registro.
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<IEnumerable<TipoRegistro>>> GetTiposRegistro()
        {
            try
            {
                var tipos = await _context.TiposRegistro.ToListAsync();
                if (tipos == null || !tipos.Any())
                    return NotFound("No se han encontrado registros en la tabla Tipo_registro.");

                return Ok(tipos);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar obtener la lista de tipos de registro.");
            }
        }

        /// <summary>
        /// GET /api/TipoRegistro/{id} - Obtiene un tipo de registro por su ID.
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<TipoRegistro>> GetTipoRegistroById(Guid id)
        {
            try
            {
                var tipoRegistroid = await _context.TiposRegistro.FindAsync(id);

                if (tipoRegistroid == null || tipoRegistroid.Id == Guid.Empty)
                    return NotFound($"No existe un tipo de registro con ID {id}");

                return Ok(tipoRegistroid);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al obtener el registro solicitado.");
            }
        }

        /// <summary>
        /// POST /api/TipoRegistro - Crea un nuevo tipo de registro (Id se genera con Guid.NewGuid()).
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status201Created)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult<TipoRegistro>> CreateTipoRegistro([FromBody] TipoRegistro objetoTipoRegistro)
        {
            try
            {
                if (objetoTipoRegistro == null)
                    return BadRequest("Datos inválidos.");

                objetoTipoRegistro.Id = Guid.NewGuid();
                _context.TiposRegistro.Add(objetoTipoRegistro);
                await _context.SaveChangesAsync();

                return CreatedAtAction(nameof(GetTipoRegistroById), new { id = objetoTipoRegistro.Id }, objetoTipoRegistro);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar crear el registro.");
            }
        }

        /// <summary>
        /// PUT /api/TipoRegistro/{id} - Actualiza un tipo de registro (SetValues con el objeto recibido).
        /// </summary>
        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status400BadRequest)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<IActionResult> UpdateTipoRegistro(Guid id, [FromBody] TipoRegistro objetoModificadoTipoRegistro)
        {
            if (objetoModificadoTipoRegistro == null || id != objetoModificadoTipoRegistro.Id)
            {
                return BadRequest("El objeto enviado es nulo o el id no coincide.");
            }

            var tipoRegistroExistente = await _context.TiposRegistro.FindAsync(id);
            if (tipoRegistroExistente == null)
                return NotFound($"No se ha encontrado el registro en la tabla TiposRegistro con el id {id}");

            // Reemplaza los valores de la entidad existente con los del cuerpo del request
            _context.Entry(tipoRegistroExistente).CurrentValues.SetValues(objetoModificadoTipoRegistro);

            try
            {
                await _context.SaveChangesAsync();
                return Ok(tipoRegistroExistente);
            }
            catch (DBConcurrencyException)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error de concurrencia al intentar actualizar el registro.");
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrió un error al intentar actualizar el registro.");
            }
        }
    }
}
