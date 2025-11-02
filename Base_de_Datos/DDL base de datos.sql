
CREATE DATABASE auditoria_sistema;
GO

USE auditoria_sistema;
GO

-- Tabla: Tipo_Accion
CREATE TABLE Tipo_Accion (
    id INT uniqueidentifier PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Objeto_Afectado
CREATE TABLE Objeto_Afectado (
    id INT uniqueidentifier PRIMARY KEY,
    nombre_tabla NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Tipo_documento
CREATE TABLE Tipo_documento (
    id INT uniqueidentifier PRIMARY KEY,
    nombre NVARCHAR(100) NOT NULL,
    acronimo NVARCHAR(10),
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Usuario
CREATE TABLE Usuario (
    id INT uniqueidentifier PRIMARY KEY,
    nombres NVARCHAR(100),
    apellidos NVARCHAR(100),
    id_tipo_documento uniqueidentifier,
    documento NVARCHAR(50),
    direccion NVARCHAR(255),
    contrasena NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (id_tipo_documento) REFERENCES Tipo_documento(id)
);

-- Tabla: Rol
CREATE TABLE Rol (
    id INT uniqueidentifier PRIMARY KEY,
    nombre NVARCHAR(100),
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Usuario_rol
CREATE TABLE Usuario_rol (
    id INT uniqueidentifier PRIMARY KEY,
    id_usuario uniqueidentifier NOT NULL,
    id_rol uniqueidentifier NOT NULL,
    fecha_creado DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_rol) REFERENCES Rol(id)
);

-- Tabla: Tipo_dispositivo
CREATE TABLE Tipo_dispositivo (
    id INT uniqueidentifier PRIMARY KEY,
    nombre NVARCHAR(100),
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Dispositivo
CREATE TABLE Dispositivo (
    id INT uniqueidentifier PRIMARY KEY,
    serial NVARCHAR(50),
    marca NVARCHAR(100),
    modelo NVARCHAR(100),
    sistema NVARCHAR(50),
    id_tipo_dispositivo uniqueidentifier,
    id_usuario uniqueidentifier,
    fecha_url NVARCHAR(255),
    qr NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (id_tipo_dispositivo) REFERENCES Tipo_dispositivo(id),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id)
);

-- Tabla: Tipo_registro
CREATE TABLE Tipo_registro (
    id INT uniqueidentifier PRIMARY KEY,
    nombre NVARCHAR(100),
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Auditoria_Negocio
CREATE TABLE Auditoria_Negocio (
    id INT uniqueidentifier PRIMARY KEY,
    id_tipo_registro uniqueidentifier,
    registrado_por uniqueidentifier,
    ejemplo_data NVARCHAR(500),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (id_tipo_registro) REFERENCES Tipo_registro(id),
    FOREIGN KEY (registrado_por) REFERENCES Usuario(id)
);

-- Tabla: Tipo_Reporte
CREATE TABLE Tipo_Reporte (
    id INT uniqueidentifier PRIMARY KEY,
    nombre NVARCHAR(100),
    descripcion NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL
);

-- Tabla: Reporte
CREATE TABLE Reporte (
    id INT uniqueidentifier PRIMARY KEY,
    generado_por uniqueidentifier,
    filtros_aplicados NVARCHAR(255),
    url_archivo NVARCHAR(255),
    id_tipo_reporte uniqueidentifier,
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (generado_por) REFERENCES Usuario(id),
    FOREIGN KEY (id_tipo_reporte) REFERENCES Tipo_Reporte(id)
);

-- Tabla: consulta_reporte
CREATE TABLE consulta_reporte (
    id INT uniqueidentifier PRIMARY KEY,
    entidad_consultada NVARCHAR(100),
    filtro_aplicado NVARCHAR(255),
    id_reporte uniqueidentifier,
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (id_reporte) REFERENCES Reporte(id)
);

-- Tabla: Log_Sistema
CREATE TABLE Log_Sistema (
    id INT uniqueidentifier PRIMARY KEY,
    id_accion uniqueidentifier,
    id_usuario uniqueidentifier,
    id_objeto_afectado uniqueidentifier,
    iv_firma NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (id_accion) REFERENCES Tipo_Accion(id),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id),
    FOREIGN KEY (id_objeto_afectado) REFERENCES Objeto_Afectado(id)
);

-- Tabla: Log_Detalle
CREATE TABLE Log_Detalle (
    id INT uniqueidentifier PRIMARY KEY,
    id_log uniqueidentifier,
    campo_afectado NVARCHAR(100),
    valor_anterior NVARCHAR(255),
    valor_nuevo NVARCHAR(255),
    fecha_creado DATETIME DEFAULT GETDATE(),
    fecha_actualizado DATETIME NULL,
    FOREIGN KEY (id_log) REFERENCES Log_Sistema(id)
);
GO