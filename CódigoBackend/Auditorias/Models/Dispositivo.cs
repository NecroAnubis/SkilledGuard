using System;

namespace Auditorias.Models
{
    public class Dispositivo
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Serial { get; set; }
        public string Marca { get; set; }
        public string Modelo { get; set; }
        public string Sistema { get; set; }
        public string Descripcion { get; set; }
        public string FotoUrl { get; set; }
        public string Qr { get; set; }
        public Guid IdTipoDispositivo { get; set; }
        public Guid IdUsuario { get; set; }
        public DateTime FechaCreado { get; set; } = DateTime.Now;
        public DateTime? FechaActualizado { get; set; }

        // Relaciones
        public TipoDispositivo TipoDispositivo { get; set; }
        public Usuario Usuario { get; set; }
    }
}
