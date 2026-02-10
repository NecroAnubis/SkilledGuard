using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations.Schema;
using System.Text.Json.Serialization;


namespace Auditorias.Models
{
    [Table("Sede")]
    public class Sede
    {
        [Column("id")]
        public Guid Id { get; set; } = Guid.NewGuid();
        [Column("nombre_sede")]
        public string NombreSede { get; set; } = string.Empty;

        // Relaciones
        [JsonIgnore]
        public ICollection<Reporte> Reportes { get; set; } = new List<Reporte>();
    }
}