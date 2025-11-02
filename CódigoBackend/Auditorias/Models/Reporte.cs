using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class Reporte
    {
        public int Id { get; set; }
        public int GeneradoPor { get; set; }
        public string? FiltrosAplicados { get; set; }
        public string UrlArchivo { get; set; } = string.Empty;
        public int IdTipoReporte { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public Usuario? Usuario { get; set; }
        public TipoReporte? TipoReporte { get; set; }
        public ICollection<ConsultaReporte>? Consultas { get; set; }
    }
}
