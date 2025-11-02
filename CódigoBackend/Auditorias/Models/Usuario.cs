using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    [Table("Usuario")]
    public class Usuario
    {
        [Key]
        public Guid Id { get; set; } = Guid.NewGuid();

        [Column("nombres")]
        public string Nombres { get; set; }
        [Column("apellidos")]
        public string Apellidos { get; set; }
        [Column("id_tipo_documento")]
        public Guid IdTipoDocumento { get; set; }
        [Column("documento")]
        public string Documento { get; set; }
        [Column("tipo_usuario")]
        public string TipoUsuario { get; set; }
        [Column("email")]
        public string Email { get; set; }
        [Column("direccion")]
        public string Direccion { get; set; }
        [Column("contraseña")]
        public string Contraseña { get; set; }
        [Column("fecha_creado")]
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        [Column("fecha_actualizado")]
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        public TipoDocumento TipoDocumento { get; set; }
        public ICollection<UsuarioRol> UsuarioRoles { get; set; }
        public ICollection<LogSistema> Logs { get; set; }
        public ICollection<Dispositivo> Dispositivos { get; set; }
        public ICollection<AuditoriaNegocio> Auditorias { get; set; }
        public ICollection<Reporte> Reportes { get; set; }
    }
}
