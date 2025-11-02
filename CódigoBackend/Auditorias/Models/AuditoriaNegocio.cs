using System;

namespace Auditorias.Models
{
    public class AuditoriaNegocio
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public DateTime FechaRegistro { get; set; } = DateTime.Now;
        public Guid IdTipoRegistro { get; set; }
        public Guid RegistradoPor { get; set; }
        public string Descripcion { get; set; }

        // Relaciones
        public TipoRegistro TipoRegistro { get; set; }
        public Usuario Usuario { get; set; }
    }
}
