using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    [Table("Rol")]
    public class Rol
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; } = string.Empty;
        public string? Descripcion { get; set; }
    }
}