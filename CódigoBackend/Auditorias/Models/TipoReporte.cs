using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoReporte
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; } = string.Empty;

        // Relaciones
        public ICollection<Reporte> Reportes { get; set; } = new List<Reporte>();
    }
}