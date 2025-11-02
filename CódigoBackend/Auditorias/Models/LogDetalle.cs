using System;

namespace Auditorias.Models
{
    public class LogDetalle
    {
        public int Id { get; set; }
        public int IdLog { get; set; }
        public string CampoAfectado { get; set; } = string.Empty;
        public string? ValorAnterior { get; set; }
        public string? ValorNuevo { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public LogSistema? Log { get; set; }
    }
}
