using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class Usuario
    {
        public int Id { get; set; }
        public string Nombres { get; set; } = string.Empty;
        public string Apellidos { get; set; } = string.Empty;
        public int IdTipoDocumento { get; set; }
        public string Documento { get; set; } = string.Empty;
        public string? Direccion { get; set; }
        public string Contrasena { get; set; } = string.Empty;
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public TipoDocumento? TipoDocumento { get; set; }
        public ICollection<UsuarioRol>? Roles { get; set; }
        public ICollection<Dispositivo>? Dispositivos { get; set; }
        public ICollection<LogSistema>? Logs { get; set; }
        public ICollection<AuditoriaNegocio>? Auditorias { get; set; }
        public ICollection<Reporte>? ReportesGenerados { get; set; }
    }
}
