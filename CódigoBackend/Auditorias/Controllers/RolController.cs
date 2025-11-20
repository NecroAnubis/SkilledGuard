using Microsoft.AspNetCore.Mvc;
using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;
using System.Data;


namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize] // notacion que indica que todos los controladores necesitan un token de autorizacion en los header
    public class RolController : ControllerBase
    {
        private readonly AuditoriaContext _context;

        public RolController(AuditoriaContext context)
        {
            _context = context;
        }

        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<IEnumerable<Rol>>> GetRoles()
        {
            try
            {
                var roles = await _context.Roles.ToListAsync();
                if (roles == null || !roles.Any())
                {
                    return NotFound("No se han encontrado registros en la tabla Roles");
                }

                return Ok(roles);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener la lista");

            }
        }

        
        // buscar un registro por id
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<Rol>> GetRolById (Guid id)
        {
            try
            {
                var rol = await _context.Roles.FindAsync(id);

                if (rol == null || rol.Id == Guid.Empty)
                {
                    return NotFound("No se ha encontrado el registro en la tabla Roles");
                }

                return Ok(rol);
                
            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener el registro");
            }
        }


        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<Rol>> CreateRol([FromBody] Rol objetoRol)
        {

            if (objetoRol == null)
            {
                return BadRequest("El objeto enviado es nulo");
            }

            try
            {
                _context.Roles.Add(objetoRol);
                await _context.SaveChangesAsync();

            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar crear el registro");    
            }
                return CreatedAtAction(nameof(GetRolById), new { id = objetoRol.Id }, objetoRol);
        }


        [HttpPut("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<IActionResult> updateRol(Guid id, [FromBody] Rol objetoModificadoRol)
        {
            if (objetoModificadoRol == null || id != objetoModificadoRol.Id)
            {
                return BadRequest("El objeto enviado es nulo o el id no coincide");
            }

            var rolExistente = await _context.Roles.FindAsync(id);

            if (rolExistente == null)
            {
                return NotFound($"No se ha encontrado el registro en la tabla Roles con el id {id}");
            }

            _context.Entry(rolExistente).CurrentValues.SetValues(objetoModificadoRol); // toma el dbset existente y reemplaza los valores con los del objeto modificado

            try
            {
                await _context.SaveChangesAsync();
                return Ok(rolExistente);
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


        [HttpDelete("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]
        public async Task<ActionResult> DeleteRol(Guid id)
        {
            var rolcito = await _context.Roles.FindAsync(id);
            if (rolcito == null)
            {
                return NotFound($"No se ha encontrado el registro en la tabla Roles con el id {id}");
            }

            try
            {
                EliminarUsuariosDelRol(id);

                _context.Roles.Remove(rolcito);
                await _context.SaveChangesAsync();

                return Ok($"El rol con id {id} ha sido eliminado exitosamente.");
            
            }catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar eliminar el registro");
            }
        }

        private void EliminarUsuariosDelRol(Guid rolId)
        {
            var usuarios = _context.Usuarios.Where(u => u.IdRol == rolId).ToList();

            foreach (var user in usuarios)
            {
                EliminarDependenciasUsuario(user.Id);
            }

            _context.Usuarios.RemoveRange(usuarios);
        }


        private void EliminarDependenciasUsuario(Guid userId)
        {
            var logs = _context.LogsSistema.Where(l => l.IdUsuario == userId);
            _context.LogsSistema.RemoveRange(logs);

            var dispositivos = _context.Dispositivos.Where(d => d.IdUsuario == userId);
            _context.Dispositivos.RemoveRange(dispositivos);

            var auditorias = _context.AuditoriasNegocio.Where(a => a.RegistradoPor == userId);
            _context.AuditoriasNegocio.RemoveRange(auditorias);

            var reportes = _context.Reportes.Where(r => r.GeneradoPor == userId);
            _context.Reportes.RemoveRange(reportes);
        }


       





    }
}