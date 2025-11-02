using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoDocumento
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; }
        public string Acronimo { get; set; }

        // Relaciones
        public ICollection<Usuario> Usuarios { get; set; }
    }
}
