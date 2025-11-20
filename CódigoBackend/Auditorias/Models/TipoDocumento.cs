using System.ComponentModel.DataAnnotations.Schema;

namespace Auditorias.Models
{
    [Table("Tipo_documento")]
    public class TipoDocumento
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string Nombre { get; set; } = string.Empty;
        public string Acronimo { get; set; } = string.Empty;

        // Relaciones
        public ICollection<Usuario> Usuarios { get; set; } = new List<Usuario>();
    }
}