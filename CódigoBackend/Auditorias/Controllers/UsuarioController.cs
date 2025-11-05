using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class UsuarioController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public UsuarioController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET: api/Usuarios
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<IEnumerable<Usuario>>> GetUsuarios()
        {
            try

            {
                var Usuarios = await _context.Usuarios.ToListAsync();
                if (Usuarios == null || !Usuarios.Any())
                {
                    return NotFound("No se encontraron usuarios.");
                }
                return Ok(Usuarios);
            }
            catch (Exception ex)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, $"Error al obtener los usuarios: {ex.Message}");
            }

        }


    }
}

