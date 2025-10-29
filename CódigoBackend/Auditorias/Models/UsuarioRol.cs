using System;

namespace Auditorias.Models
{
    public class UsuarioRol
    {
        public int Id { get; set; }
        public int IdUsuario { get; set; }
        public int IdRol { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public Usuario? Usuario { get; set; }
        public Rol? Rol { get; set; }
    }
}
