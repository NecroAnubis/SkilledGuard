using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class Rol
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; }
        public string Descripcion { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        public ICollection<UsuarioRol> UsuarioRoles { get; set; }
    }
}
