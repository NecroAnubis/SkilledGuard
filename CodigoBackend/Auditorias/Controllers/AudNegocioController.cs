// Ruta: GET /api/AuditoriaNegocio
// Propósito: Consultar logs de negocio (auditorías a nivel de negocio).
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers{

/// <summary>
/// Controlador para consultar auditorías de negocio.
/// Expone un único endpoint GET que devuelve todos los registros de auditoría.
/// </summary>
[ApiController]
[Route("api/[controller]")]
public class AuditoriaNegocioController : ControllerBase
{
    // Contexto de base de datos para acceder a la tabla AuditoriasNegocio
    private readonly AuditoriaContext _context;
    
    // Inyección de Dependencias: el contexto se recibe por constructor para poder consultar la BD
    public AuditoriaNegocioController(AuditoriaContext context)
    {
        _context = context;
    }

    /// <summary>
    /// GET /api/AuditoriaNegocio - Obtiene la lista completa de auditorías de negocio.
    /// </summary>
    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<IEnumerable<AuditoriaNegocio>>> GetAuditoriasAsync()
    {
        try
        {
            // Consulta asíncrona: trae todos los registros de AuditoriasNegocio desde la BD
            var results = await _context.AuditoriasNegocio.ToListAsync();
            // Devuelve 200 OK con la colección de auditorías
            return Ok(results);
        }
        catch (Exception)
        {
            // Cualquier error no controlado se responde con 500
            return StatusCode(StatusCodes.Status500InternalServerError);
        }
    }
}

    internal interface IAuditoriaNegocioService
    {
    }
}