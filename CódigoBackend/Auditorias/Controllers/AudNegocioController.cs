// Ruta: GET /api/AuditoriaNegocio
// Propósito: Consultar logs de negocio.
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Auditorias.Controllers{

[ApiController]
[Route("api/[controller]")]
public class AuditoriaNegocioController : ControllerBase
{
    private readonly AuditoriaContext _context;
    
    // Inyección de Dependencias en el constructor
    public AuditoriaNegocioController(AuditoriaContext context)
    {
        _context = context;
    }

    [HttpGet]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<ActionResult<IEnumerable<AuditoriaNegocio>>> GetAuditoriasAsync()
    {
        try
        {
            var results = await _context.AuditoriasNegocio.ToListAsync();
            return Ok(results);
        }
        catch (Exception)
        {
            return StatusCode(StatusCodes.Status500InternalServerError);
        }
    }
}

    internal interface IAuditoriaNegocioService
    {
    }
}