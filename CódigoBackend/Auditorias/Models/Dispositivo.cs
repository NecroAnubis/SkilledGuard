using System;

namespace Auditorias.Models
{
    public class Dispositivo
    {
        public int Id { get; set; }
        public string Serial { get; set; } = string.Empty;
        public string Marca { get; set; } = string.Empty;
        public string Modelo { get; set; } = string.Empty;
        public string Sistema { get; set; } = string.Empty;
        public int IdTipoDispositivo { get; set; }
        public int IdUsuario { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        public TipoDispositivo? TipoDispositivo { get; set; }
        public Usuario? Usuario { get; set; }
    }
}
