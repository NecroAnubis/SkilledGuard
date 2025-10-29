using Microsoft.EntityFrameworkCore;
using Auditorias.Models;

namespace Auditorias.Data
{
    public class AuditoriaContext : DbContext
    {
        public AuditoriaContext(DbContextOptions<AuditoriaContext> options) : base(options) { }

        public DbSet<Usuario> Usuarios { get; set; }
        public DbSet<Rol> Roles { get; set; }
        public DbSet<UsuarioRol> UsuarioRoles { get; set; }
        public DbSet<TipoAccion> TipoAcciones { get; set; }
        public DbSet<ObjetoAfectado> ObjetosAfectados { get; set; }
        public DbSet<LogSistema> LogsSistema { get; set; }
        public DbSet<LogDetalle> LogsDetalles { get; set; }
        public DbSet<TipoDispositivo> TiposDispositivo { get; set; }
        public DbSet<Dispositivo> Dispositivos { get; set; }
        public DbSet<TipoReporte> TiposReporte { get; set; }
        public DbSet<Reporte> Reportes { get; set; }
        public DbSet<ConsultaReporte> ConsultasReporte { get; set; }
        public DbSet<AuditoriaNegocio> AuditoriasNegocio { get; set; }
        public DbSet<TipoRegistro> TiposRegistro { get; set; }
    }
}
