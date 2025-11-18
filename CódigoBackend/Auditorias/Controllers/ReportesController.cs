

using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    [Authorize] // notacion que indica que todos los controladores necesitan un token de autorizacion en los header
    public class ReportesController : ControllerBase
    {

        private readonly AuditoriaContext _context;
        public ReportesController(AuditoriaContext context)
        {
            _context = context;
        }


        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<IEnumerable<object>>> GetReportes()
        {
            try
            {
                var reportes = await _context.Reportes
                .Include(r => r.SedeEntidad)
                .Include(r => r.TipoReporte)
                .Select(r => new
                {
                    r.Id,
                    r.GeneradoPor,
                    r.Sede,
                    r.Descripcion,
                    r.FechaGenerado,
                    r.UrlArchivo,
                    r.IdTipoReporte,
                    r.FechaActualizado,
                    Usuario = r.Usuario != null ? r.Usuario.Nombres : null,
                    SedeEntidad = r.SedeEntidad != null ? r.SedeEntidad.NombreSede : null,
                    TipoReporte = r.TipoReporte != null ? r.TipoReporte.Nombre : null    
                })
                .ToListAsync();
                if (reportes == null || !reportes.Any())
                {
                    return NotFound("No se han encontrado registros en la tabla Reportes");
                }

                return Ok(reportes);
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

        public async Task<ActionResult<object>> GetReporteById (Guid id)
        {
            try
            {
                var reporte = await _context.Reportes
                .Include(r => r.SedeEntidad)
                .Include(r => r.TipoReporte)
                .Select(r => new
                {
                    r.Id,
                    r.GeneradoPor,
                    r.Sede,
                    r.Descripcion,
                    r.FechaGenerado,
                    r.UrlArchivo,
                    r.IdTipoReporte,
                    r.FechaActualizado,
                    Usuario = r.Usuario != null ? r.Usuario.Nombres : null,
                    SedeEntidad = r.SedeEntidad != null ? r.SedeEntidad.NombreSede : null,
                    TipoReporte = r.TipoReporte != null ? r.TipoReporte.Nombre : null    
                })
                .FirstOrDefaultAsync(r => r.Id == id);



                if (reporte == null || reporte.Id == Guid.Empty)
                {
                    return NotFound("No se ha encontrado el registro en la tabla Reportes");
                }

                return Ok(reporte);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener el reporte");

            }
        }


        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<object>> CreateReporte([FromBody] Reporte objetoReporte)
        {

            if (objetoReporte == null)
            {
                return BadRequest("El objeto enviado es nulo");
            }

            try
            {
               objetoReporte.Id = Guid.NewGuid();
               objetoReporte.FechaGenerado = DateTime.Now;

               _context.Reportes.Add(objetoReporte);
               await _context.SaveChangesAsync();

               var reporteCreado = await _context.Reportes
                .Include(r => r.SedeEntidad)
                .Include(r => r.TipoReporte)
                .Select(r => new
                {
                    r.Id,
                    r.GeneradoPor,
                    r.Sede,
                    r.Descripcion,
                    r.FechaGenerado,
                    r.UrlArchivo,
                    r.IdTipoReporte,
                    r.FechaActualizado,
                    Usuario = r.Usuario != null ? r.Usuario.Nombres : null,
                    SedeEntidad = r.SedeEntidad != null ? r.SedeEntidad.NombreSede : null,
                    TipoReporte = r.TipoReporte != null ? r.TipoReporte.Nombre : null    
                })
                .FirstOrDefaultAsync();

                return CreatedAtAction(nameof(GetReporteById),
                new { id = objetoReporte.Id }, reporteCreado);


            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar crear el reporte");    
            }
        }
    }
}