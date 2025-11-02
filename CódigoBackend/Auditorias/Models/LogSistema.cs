using System;

namespace Auditorias.Models
{
    public class LogSistema
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public Guid IdUsuario { get; set; }
        public string Descripcion { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;

        // Relaciones
        public Usuario Usuario { get; set; }
    }
}
