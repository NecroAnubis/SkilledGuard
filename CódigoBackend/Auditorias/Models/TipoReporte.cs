using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoReporte
    {
        public int Id { get; set; }
        public string Nombre { get; set; } = string.Empty;
        public string? Descripcion { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public ICollection<Reporte>? Reportes { get; set; }
    }
}
