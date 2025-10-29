using System;

namespace Auditorias.Models
{
    public class ConsultaReporte
    {
        public int Id { get; set; }
        public string EntidadConsultada { get; set; } = string.Empty;
        public string? FiltroAplicado { get; set; }
        public int IdReporte { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public Reporte? Reporte { get; set; }
    }
}
