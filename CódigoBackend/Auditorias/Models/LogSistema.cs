using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class LogSistema
    {
        public int Id { get; set; }
        public int IdAccion { get; set; }
        public int IdUsuario { get; set; }
        public int IdObjetoAfectado { get; set; }
        public string IvFirma { get; set; } = string.Empty;
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public TipoAccion? TipoAccion { get; set; }
        public Usuario? Usuario { get; set; }
        public ObjetoAfectado? ObjetoAfectado { get; set; }
        public ICollection<LogDetalle>? Detalles { get; set; }
    }
}
