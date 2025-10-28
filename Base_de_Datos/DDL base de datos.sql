

IF DB_ID('auditoria_sistema') IS NOT NULL
BEGIN
    DROP DATABASE auditoria_sistema;
END
GO

CREATE DATABASE auditoria_sistema;
GO

USE auditoria_sistema;
GO

-- Tabla: Tipo_Acciona
CREATE TABLE dbo.Tipo_Accion (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(255) NOT NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Objeto_Afectado
CREATE TABLE dbo.Objeto_Afectado (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre_tabla NVARCHAR(255) NOT NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Tipo_documento
CREATE TABLE dbo.Tipo_documento (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(255) NOT NULL,
    acronimo NVARCHAR(50) NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Usuario
CREATE TABLE dbo.Usuario (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombres NVARCHAR(255) NOT NULL,
    apellidos NVARCHAR(255) NOT NULL,
    id_tipo_documento INT NULL,
    documento NVARCHAR(100) NULL,
    direccion NVARCHAR(255) NULL,
    contrasena NVARCHAR(255) NOT NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_Usuario_TipoDocumento FOREIGN KEY (id_tipo_documento)
        REFERENCES dbo.Tipo_documento(id)
);
CREATE UNIQUE INDEX UX_Usuario_documento ON dbo.Usuario(documento) WHERE documento IS NOT NULL;
GO

-- Tabla: Rol
CREATE TABLE dbo.Rol (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(255) NOT NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Usuario_rol
CREATE TABLE dbo.Usuario_rol (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_rol INT NOT NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_UsuarioRol_Usuario FOREIGN KEY (id_usuario) REFERENCES dbo.Usuario(id),
    CONSTRAINT FK_UsuarioRol_Rol FOREIGN KEY (id_rol) REFERENCES dbo.Rol(id)
);
GO

-- Tabla: Tipo_dispositivo
CREATE TABLE dbo.Tipo_dispositivo (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(255) NOT NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Dispositivo
CREATE TABLE dbo.Dispositivo (
    id INT IDENTITY(1,1) PRIMARY KEY,
    serial NVARCHAR(100) NULL,
    marca NVARCHAR(100) NULL,
    modelo NVARCHAR(100) NULL,
    sistema NVARCHAR(100) NULL,
    foto_url NVARCHAR(255) NULL,
    qr NVARCHAR(255) NULL,
    id_tipo_dispositivo INT NULL,
    id_usuario INT NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_Dispositivo_TipoDispositivo FOREIGN KEY (id_tipo_dispositivo) REFERENCES dbo.Tipo_dispositivo(id),
    CONSTRAINT FK_Dispositivo_Usuario FOREIGN KEY (id_usuario) REFERENCES dbo.Usuario(id)
);
GO

-- Tabla: Log_Sistema
CREATE TABLE dbo.Log_Sistema (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_accion INT NULL,
    id_usuario INT NULL,
    id_objeto_afectado INT NULL,
    iv_firma NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_LogSistema_TipoAccion FOREIGN KEY (id_accion) REFERENCES dbo.Tipo_Accion(id),
    CONSTRAINT FK_LogSistema_Usuario FOREIGN KEY (id_usuario) REFERENCES dbo.Usuario(id),
    CONSTRAINT FK_LogSistema_ObjetoAfectado FOREIGN KEY (id_objeto_afectado) REFERENCES dbo.Objeto_Afectado(id)
);
GO

-- Tabla: Log_Detalle
CREATE TABLE dbo.Log_Detalle (
    id INT IDENTITY(1,1) PRIMARY KEY,
    id_log INT NOT NULL,
    campo_afectado NVARCHAR(255) NULL,
    valor_anterior NVARCHAR(255) NULL,
    valor_nuevo NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_LogDetalle_LogSistema FOREIGN KEY (id_log) REFERENCES dbo.Log_Sistema(id)
);
GO

-- Tabla: Tipo_registro
CREATE TABLE dbo.Tipo_registro (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(255) NOT NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Auditoria_Negocio
CREATE TABLE dbo.Auditoria_Negocio (
    id INT IDENTITY(1,1) PRIMARY KEY,
    fecha_registro DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    id_tipo_registro INT NULL,
    registrado_por INT NULL,
    ejemplo_data NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_AuditoriaNegocio_TipoRegistro FOREIGN KEY (id_tipo_registro) REFERENCES dbo.Tipo_registro(id),
    CONSTRAINT FK_AuditoriaNegocio_Usuario FOREIGN KEY (registrado_por) REFERENCES dbo.Usuario(id)
);
GO

-- Tabla: Tipo_Reporte
CREATE TABLE dbo.Tipo_Reporte (
    id INT IDENTITY(1,1) PRIMARY KEY,
    nombre NVARCHAR(255) NOT NULL,
    descripcion NVARCHAR(255) NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL
);
GO

-- Tabla: Reporte
CREATE TABLE dbo.Reporte (
    id INT IDENTITY(1,1) PRIMARY KEY,
    generado_por INT NULL,
    fecha_generado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    filtros_aplicados NVARCHAR(255) NULL,
    url_archivo NVARCHAR(255) NULL,
    id_tipo_reporte INT NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_Reporte_Usuario FOREIGN KEY (generado_por) REFERENCES dbo.Usuario(id),
    CONSTRAINT FK_Reporte_TipoReporte FOREIGN KEY (id_tipo_reporte) REFERENCES dbo.Tipo_Reporte(id)
);
GO

-- Tabla: consulta_reporte
CREATE TABLE dbo.consulta_reporte (
    id INT IDENTITY(1,1) PRIMARY KEY,
    entidad_consultada NVARCHAR(255) NULL,
    filtro_aplicado NVARCHAR(255) NULL,
    id_reporte INT NULL,
    fecha_creado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    fecha_actualizado DATETIME2 DEFAULT SYSUTCDATETIME() NOT NULL,
    CONSTRAINT FK_consulta_reporte_Reporte FOREIGN KEY (id_reporte) REFERENCES dbo.Reporte(id)
);
GO




