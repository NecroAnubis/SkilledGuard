using System;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;

namespace Auditorias.Models
{
    [Table("Reporte")]
    public class Reporte
    {
        public Guid Id { get; set; } = Guid.NewGuid();

        [Column("generado_por")]
        public Guid GeneradoPor { get; set; }

        [Column("sede")]
        public Guid Sede { get; set; }

        [Column("descripcion")]
        public string Descripcion { get; set; } = string.Empty;

        [Column("fecha_generado")]
        public DateTime FechaGenerado { get; set; } = DateTime.Now;

        [Column("url_archivo")]
        public string UrlArchivo { get; set; } = string.Empty;

        [Column("id_tipo_reporte")]
        public Guid IdTipoReporte { get; set; }

        [JsonIgnore]
        [Column("fecha_creado")]
        public DateTime? FechaCreado { get; set; } = DateTime.Now;

        [Column("fecha_actualizado")]
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        [ForeignKey("GeneradoPor")]
        public Usuario? Usuario { get; set; }

        [ForeignKey("Sede")]
        public Sede? SedeEntidad { get; set; }

        [ForeignKey("IdTipoReporte")]
        public TipoReporte? TipoReporte { get; set; }
    }
}