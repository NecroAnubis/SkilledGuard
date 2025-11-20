namespace Auditorias.utils
{
    public class CambiarContraseñaRequest
    {
        public Guid IdUsuario { get; set; }
        public string ContraseñaActual { get; set; } = string.Empty;
        public string NuevaContraseña { get; set; } = string.Empty;
    }
}