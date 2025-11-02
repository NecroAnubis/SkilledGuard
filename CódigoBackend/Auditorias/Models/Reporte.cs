using System;

namespace Auditorias.Models
{
    public class Reporte
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid GeneradoPor { get; set; }
        public Guid Sede { get; set; }
        public string Descripcion { get; set; }
        public DateTime FechaGenerado { get; set; } = DateTime.Now;
        public string UrlArchivo { get; set; }
        public Guid IdTipoReporte { get; set; }
        public DateTime? FechaCreado { get; set; }
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        public Usuario Usuario { get; set; }
        public Sede SedeEntidad { get; set; }
        public TipoReporte TipoReporte { get; set; }
    }
}
