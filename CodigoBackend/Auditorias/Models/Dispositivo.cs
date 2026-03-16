using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    [Table("Dispositivo")]
    public class Dispositivo
    {
        public Guid Id { get; set; } = Guid.NewGuid();

        [Column("serial")]
        public string Serial { get; set; } = string.Empty;

        [Column("marca")]
        public string Marca { get; set; } = string.Empty;

        [Column("modelo")]
        public string Modelo { get; set; } = string.Empty;

        [Column("sistema")]
        public string Sistema { get; set; } = string.Empty;

        [Column("descripcion")]
        public string Descripcion { get; set; } = string.Empty;

        [Column("foto_url")]
        public string FotoUrl { get; set; } = string.Empty;

        [Column("qr")]
        public string Qr { get; set; } = string.Empty;

        [Column("id_tipo_dispositivo")]
        public Guid IdTipoDispositivo { get; set; }

        [Column("id_usuario")]
        public Guid IdUsuario { get; set; }

        [Column("fecha_creado")]
        public DateTime FechaCreado { get; set; } = DateTime.Now;

        [Column("fecha_actualizado")]
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        [ForeignKey("IdTipoDispositivo")]
        public TipoDispositivo? TipoDispositivo { get; set; }

        [ForeignKey("IdUsuario")]
        public Usuario? Usuario { get; set; }
    }
}