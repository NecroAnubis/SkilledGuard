// Ruta: /api/Reportes
// Propósito: CRUD de reportes (listar, obtener por id, crear). Requiere token JWT.
using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Auditorias.Models;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers
{
    /// <summary>
    /// Controlador para gestionar reportes (listado, detalle y creación).
    /// Todas las acciones requieren token de autorización en el header.
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    [Authorize] // Indica que todos los endpoints del controlador requieren token JWT en el header
    public class ReportesController : ControllerBase
    {
        // Contexto de BD para acceder a Reportes, SedeEntidad, TipoReporte y Usuario
        private readonly AuditoriaContext _context;

        public ReportesController(AuditoriaContext context)
        {
            _context = context;
        }

        /// <summary>
        /// GET /api/Reportes - Lista todos los reportes con SedeEntidad, TipoReporte y nombre del Usuario.
        /// </summary>
        [HttpGet]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<IEnumerable<object>>> GetReportes()
        {
            try
            {
                // Incluye SedeEntidad y TipoReporte para devolver nombres en el objeto anónimo
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
                    return NotFound("No se han encontrado registros en la tabla Reportes");

                return Ok(reportes);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener la lista");
            }
        }

        /// <summary>
        /// GET /api/Reportes/{id} - Obtiene un reporte por su ID con SedeEntidad, TipoReporte y Usuario.
        /// </summary>
        [HttpGet("{id}")]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<object>> GetReporteById (Guid id)
        {
            try
            {
                // Filtra por id y proyecta a objeto anónimo con nombres de relaciones
                var reporte = await _context.Reportes
                .Include(r => r.SedeEntidad)
                .Include(r => r.TipoReporte)
                .Where(r => r.Id == id)
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

                if (reporte == null)
                    return NotFound("No se ha encontrado el registro en la tabla Reportes");

                return Ok(reporte);
            }
            catch (Exception)
            {
                return StatusCode(StatusCodes.Status500InternalServerError, "Ocurrio un error al intentar obtener el reporte");
            }
        }

        /// <summary>
        /// POST /api/Reportes - Crea un nuevo reporte (Id y FechaGenerado se asignan aquí).
        /// </summary>
        [HttpPost]
        [ProducesResponseType(StatusCodes.Status200OK)]
        [ProducesResponseType(StatusCodes.Status404NotFound)]
        [ProducesResponseType(StatusCodes.Status500InternalServerError)]

        public async Task<ActionResult<object>> CreateReporte([FromBody] Reporte objetoReporte)
        {

            if (objetoReporte == null)
                return BadRequest("El objeto enviado es nulo");

            try
            {
                objetoReporte.Id = Guid.NewGuid();
                objetoReporte.FechaGenerado = DateTime.Now;

                _context.Reportes.Add(objetoReporte);
                await _context.SaveChangesAsync();

                // Se consulta el reporte recién creado con relaciones para devolverlo en 201 Created
                var reporteCreado = await _context.Reportes
                .Where(r => r.Id == objetoReporte.Id)
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