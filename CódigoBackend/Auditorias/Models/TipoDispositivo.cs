using System;
using System.Collections.Generic;

namespace Auditorias.Models
{
    public class TipoDispositivo
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; }

        // Relaciones
        public ICollection<Dispositivo> Dispositivos { get; set; }
    }
}
