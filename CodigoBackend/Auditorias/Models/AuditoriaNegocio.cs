using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    [Table("Auditoria_Negocio")]
    public class AuditoriaNegocio
    {
        public Guid Id { get; set; } = Guid.NewGuid();

        [Column("fecha_registro")]
        public DateTime FechaRegistro { get; set; } = DateTime.Now;

        [Column("id_tipo_registro")]
        public Guid IdTipoRegistro { get; set; }

        [Column("registrado_por")]
        public Guid RegistradoPor { get; set; }

        [Column("descripcion")]
        public string Descripcion { get; set; } = string.Empty;

        // Relaciones
        [ForeignKey("IdTipoRegistro")]
        public TipoRegistro? TipoRegistro { get; set; }

        [ForeignKey("RegistradoPor")]
        public Usuario? Usuario { get; set; }
    }
}