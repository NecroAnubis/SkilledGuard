using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace Auditorias.Models
{
    [Table("Tipo_Reporte")]
    public class TipoReporte
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; } = string.Empty;
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }
        public bool IsDeleted { get; set; }

        // Relaciones
        [JsonIgnore]
        public ICollection<Reporte> Reportes { get; set; } = new List<Reporte>();
    }
}