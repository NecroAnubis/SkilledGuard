using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoDispositivo
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; } = string.Empty;

        // Relaciones
        public ICollection<Dispositivo> Dispositivos { get; set; } = new List<Dispositivo>();
    }
}