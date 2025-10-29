using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    
    [Table("Tipo_Accion")]
    public class TipoAccion
    {
        [Key]
        public int Id { get; set; }
        public string Nombre { get; set; } = string.Empty;
        public string? Descripcion { get; set; }

        [Column("fecha_creado")]
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        [Column("fecha_actualizado")] 
        public DateTime? FechaActualizado { get; set; }

        public ICollection<LogSistema>? Logs { get; set; }
    }
}
