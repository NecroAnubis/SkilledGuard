using System;

namespace Auditorias.Models
{
    public class AuditoriaNegocio
    {
        public int Id { get; set; }
        public int IdTipoRegistro { get; set; }
        public int RegistradoPor { get; set; }
        public string EjemploData { get; set; } = string.Empty;
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public TipoRegistro? TipoRegistro { get; set; }
        public Usuario? Usuario { get; set; }
    }
}
