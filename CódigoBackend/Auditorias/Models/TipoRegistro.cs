using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoRegistro
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; }

        // Relaciones
        public ICollection<AuditoriaNegocio> Auditorias { get; set; }
    }
}
