using System;
using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    [Table ("Log_Sistema")]
    public class LogSistema
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        [Column("id_usuario")]
        public Guid IdUsuario { get; set; }
        [Column("descripcion")]
        public string Descripcion { get; set; } = string.Empty;
        [Column("fecha_creado")]
        public DateTime FechaCreado { get; set; } = DateTime.Now;

        // Relaciones
        [ForeignKey("IdUsuario")]
        public Usuario? Usuario { get; set; }
    }
}