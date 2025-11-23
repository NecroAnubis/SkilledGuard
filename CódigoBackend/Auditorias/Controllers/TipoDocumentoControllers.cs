using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Auditorias.utils;

namespace Auditoria.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    [Authorize]
    public class TipoDocumentoController : ControllerBase
    {
           private readonly AuditoriaContext _context;

        public TipoDocumentoController(AuditoriaContext context)
        {
            _context = context;
        }

        // GET: api/TipoDocumento
        [HttpGet]
        public async Task<ActionResult<IEnumerable<TipoDocumento>>> GetTipoDocumentos()
        {
            return await _context.TipoDocumentos.ToListAsync();
        }

        [HttpGet("{id}")]
        public async Task<ActionResult<TipoDocumento>> GetTipoDocumento(int id)
        {
            var tipoDocumento = await _context.TipoDocumentos.FindAsync(id);

            if (tipoDocumento == null)
                return NotFound();

            return tipoDocumento;
        }

        // POST: api/TipoDocumento
        [HttpPost]
        public async Task<ActionResult<TipoDocumento>> PostTipoDocumento(TipoDocumento tipoDocumento)
        {
            _context.TipoDocumentos.Add(tipoDocumento);
            await _context.SaveChangesAsync();

            return CreatedAtAction(nameof(GetTipoDocumento), new { id = tipoDocumento.Id }, tipoDocumento);
        }

        // PUT: api/TipoDocumento/5
        [HttpPut("{id}")]
        public async Task<IActionResult> PutTipoDocumento(int id, TipoDocumento tipoDocumento)
        {
            if (id != tipoDocumento.Id)
                return BadRequest();

            _context.Entry(tipoDocumento).State = EntityState.Modified;

            try
            {
                await _context.SaveChangesAsync();
            }
            catch (DbUpdateConcurrencyException)
            {
                if (!_context.TipoDocumentos.Any(e => e.Id == id))
                    return NotFound();
                throw;
            }

            return NoContent();
        }

        // DELETE: api/TipoDocumento/5
        [HttpDelete("{id}")]
        public async Task<IActionResult> DeleteTipoDocumento(int id)
        {
            var tipoDocumento = await _context.TipoDocumentos.FindAsync(id);
            if (tipoDocumento == null)
                return NotFound();

            _context.TipoDocumentos.Remove(tipoDocumento);
            await _context.SaveChangesAsync();

            return NoContent();
        }
    }
}
