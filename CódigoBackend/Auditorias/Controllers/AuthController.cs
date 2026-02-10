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
        [AllowAnonymous] // indica que no es necesario un token de autorizacion 
        public IActionResult Login([FromBody] LoginRequest request)
        {
            var usuario = _context.Usuarios
                .Include(u => u.Rol)
                .FirstOrDefault(u => u.Email == request.Email);

            // Verifica el hash de la contraseña
            if (usuario == null || !PasswordHelper.VerifyPassword(request.Contraseña, usuario.Contraseña))
                return Unauthorized("Credenciales inválidas");

            var claims = new[] // dato clave valor 
            {
        new Claim(JwtRegisteredClaimNames.Sub, usuario.Id.ToString()),
        new Claim(JwtRegisteredClaimNames.Email, usuario.Email),
        new Claim("rol", usuario.Rol?.Nombre ?? string.Empty)
    };

            var keyString = _configuration["Jwt:Key"] ?? "skilledGuardSuperKey1234567890!@#$%^"; // proceso de obtencion de clave secreta desde appsettings
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(keyString)); // convierte la clave en un objeto para firmar token
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256); // crea las credenciales de firma 

            var token = new JwtSecurityToken(
                issuer: _configuration["Jwt:Issuer"], // indica quien emite el token
                audience: null, // para quien es el token, en este caso no se usa
                claims: claims, // datos sobre el usuario que estan dentro del token
                expires: DateTime.Now.AddHours(2), // tiempo que dura valido el token 
                signingCredentials: creds // credenciales de firma para poder asegurar la autenticidad del token
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