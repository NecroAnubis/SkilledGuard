// Ruta: /api/LogSistema
// Propósito: Consulta de logs de nivel de sistema (e.g., errores, advertencias, info).
using Auditorias.Data;
using Auditorias.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

[ApiController]
[Route("api/[controller]")]
public class LogSistemaController : ControllerBase
{
    private readonly AuditoriaContext _context;
    public LogSistemaController(AuditoriaContext context)
    {
        _context = context;
    }

    
    /// Obtiene un log específico por su identificador.
    [HttpGet("{id}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    [ProducesResponseType(StatusCodes.Status500InternalServerError)]
    public async Task<ActionResult<IEnumerable<LogSistema>>>GetLogsSistema(Guid id)
    {
        var log = await _context.LogsSistema.FindAsync(id);

        if (log == null)
        {
            return NotFound();
        }

        return Ok(log);
    }

    }