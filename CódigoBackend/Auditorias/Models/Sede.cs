using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class Sede
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string NombreSede { get; set; }

        // Relaciones
        public ICollection<Reporte> Reportes { get; set; }
    }
}
