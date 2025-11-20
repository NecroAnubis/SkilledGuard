using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoRegistro
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; } = string.Empty;

        // Relaciones
        public ICollection<AuditoriaNegocio> Auditorias { get; set; } = new List<AuditoriaNegocio>();
    }
}