using System;

namespace Auditorias.Models
{
    public class UsuarioRol
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid IdUsuario { get; set; }
        public Guid IdRol { get; set; }
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        public Usuario Usuario { get; set; }
        public Rol Rol { get; set; }
    }
}
