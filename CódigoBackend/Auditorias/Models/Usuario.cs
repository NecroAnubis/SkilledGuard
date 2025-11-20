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
        [Column("id")]
        public Guid Id { get; set; } = Guid.NewGuid();

        [Column("nombres")]
        public string Nombres { get; set; } = string.Empty;

        [Column("apellidos")]
        public string Apellidos { get; set; } = string.Empty;

        [Column("id_tipo_documento")]
        public Guid IdTipoDocumento { get; set; }

        [ForeignKey(nameof(IdTipoDocumento))]
        public TipoDocumento? TipoDocumento { get; set; }

        [Column("documento")]
        public string Documento { get; set; } = string.Empty;

        [Column("tipo_usuario")]
        public string TipoUsuario { get; set; } = string.Empty;

        [Column("email")]
        public string Email { get; set; } = string.Empty;

        [Column("direccion")]
        public string Direccion { get; set; } = string.Empty;

        [Column("contraseña")]
        public string Contraseña { get; set; } = string.Empty;

        [Column("fecha_creado")]
        public DateTime FechaCreado { get; set; } = DateTime.Now;

        [Column("fecha_actualizado")]
        public DateTime? FechaActualizado { get; set; }

        [Column("id_rol")]
        public Guid IdRol { get; set; }

        [ForeignKey(nameof(IdRol))]
        public Rol? Rol { get; set; }

        public ICollection<LogSistema> Logs { get; set; } = new List<LogSistema>();
        public ICollection<Dispositivo> Dispositivos { get; set; } = new List<Dispositivo>();
        public ICollection<AuditoriaNegocio> Auditorias { get; set; } = new List<AuditoriaNegocio>();
        public ICollection<Reporte> Reportes { get; set; } = new List<Reporte>();
    }
}