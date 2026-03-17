// Controlador de autenticación: login y generación de JWT.
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
    /// <summary>
    /// Gestiona la autenticación de usuarios (login) y emisión de tokens JWT.
    /// Ruta base: /api/Auth
    /// </summary>
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        // Contexto para consultar usuarios en la BD
        private readonly AuditoriaContext _context;
        // Configuración para leer Jwt:Key, Jwt:Issuer desde appsettings
        private readonly IConfiguration _configuration;

        // Inyección del contexto y la configuración para poder validar credenciales y generar el token
        public AuthController(AuditoriaContext context, IConfiguration configuration)
        {
            _context = context;
            _configuration = configuration;
        }

        /// <summary>
        /// POST /api/Auth/login - Valida credenciales y devuelve un token JWT y datos del usuario.
        /// </summary>
        [HttpPost("login")]
        [AllowAnonymous] // Indica que no es necesario un token de autorización para llamar a este endpoint
        public IActionResult Login([FromBody] LoginRequest? request)
        {
            if (request == null || string.IsNullOrWhiteSpace(request.Email) || string.IsNullOrWhiteSpace(request.Contraseña))
                return BadRequest("Se requieren email y contraseña.");

            // Busca el usuario por email e incluye su Rol para añadirlo al token
            var usuario = _context.Usuarios
                .Include(u => u.Rol)
                .FirstOrDefault(u => u.Email == request.Email);

            // Verifica que exista el usuario y que la contraseña coincida con el hash almacenado
            if (usuario == null || !PasswordHelper.VerifyPassword(request.Contraseña, usuario.Contraseña))
                return Unauthorized("Credenciales inválidas");

            // Claims: datos clave-valor que se incluirán dentro del token (id, email, rol)
            var claims = new[]
            {
                new Claim(JwtRegisteredClaimNames.Sub, usuario.Id.ToString()),
                new Claim(JwtRegisteredClaimNames.Email, usuario.Email),
                new Claim("rol", usuario.Rol?.Nombre ?? string.Empty)
            };

            // Obtención de la clave secreta desde appsettings para firmar el token
            var keyString = _configuration["Jwt:Key"] ?? "skilledGuardSuperKey1234567890!@#$%^";
            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(keyString)); // Convierte la clave en objeto para firmar
            var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256); // Credenciales de firma HMAC-SHA256

            // Construcción del token JWT con emisor, claims, expiración y firma
            var token = new JwtSecurityToken(
                issuer: _configuration["Jwt:Issuer"],
                audience: null,
                claims: claims,
                expires: DateTime.Now.AddHours(2), // El token es válido durante 2 horas
                signingCredentials: creds
            );

            // Respuesta 200 OK con el token en texto y los datos del usuario (sin contraseña)
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

    /// <summary>
    /// DTO para el cuerpo del request de login (email y contraseña).
    /// </summary>
    public class LoginRequest
    {
        public string Email { get; set; } = string.Empty;
        public string Contraseña { get; set; } = string.Empty;
    }
}