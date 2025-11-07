using Microsoft.AspNetCore.Mvc;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using Auditorias.Data;
using Microsoft.AspNetCore.Authorization;
using Microsoft.EntityFrameworkCore;
using Auditorias.utils;

namespace Auditorias.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly AuditoriaContext _context;
        private readonly IConfiguration _configuration;

        public AuthController(AuditoriaContext context, IConfiguration configuration)
        {
            _context = context;
            _configuration = configuration;
        }

        [HttpPost("login")]
        [AllowAnonymous]
        public IActionResult Login([FromBody] LoginRequest request)
        {
            var usuario = _context.Usuarios
                .Include(u => u.Rol)
                .FirstOrDefault(u => u.Email == request.Email);

            // Verifica el hash de la contraseña
            if (usuario == null || !PasswordHelper.VerifyPassword(request.Contraseña, usuario.Contraseña))
                return Unauthorized("Credenciales inválidas");

            var claims = new[]
            {
        new Claim(JwtRegisteredClaimNames.Sub, usuario.Id.ToString()),
        new Claim(JwtRegisteredClaimNames.Email, usuario.Email),
        new Claim("rol", usuario.Rol?.Nombre ?? string.Empty)
    };

            var keyString = _configuration["Jwt:Key"] ?? "skilledGuardSuperKey1234567890!@#$%^";
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(keyString));
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var token = new JwtSecurityToken(
                issuer: _configuration["Jwt:Issuer"],
                audience: null,
                claims: claims,
                expires: DateTime.Now.AddHours(2),
                signingCredentials: creds
            );

            return Ok(new
            {
                token = new JwtSecurityTokenHandler().WriteToken(token),
                usuario = new
                {
                    id = usuario.Id,
                    nombres = usuario.Nombres,
                    apellidos = usuario.Apellidos,
                    email = usuario.Email,
                    rol = usuario.Rol?.Nombre ?? string.Empty
                }
            });
        }
    }

    public class LoginRequest
    {
        public string Email { get; set; } = string.Empty;
        public string Contraseña { get; set; } = string.Empty;
    }
}