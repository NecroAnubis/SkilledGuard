CREATE DATABASE auditoria_sistema;
GO

USE auditoria_sistema;
GO

CREATE TABLE Rol (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombre NVARCHAR(100) NOT NULL,
    descripcion NVARCHAR(500)
);

CREATE TABLE Tipo_documento (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombre NVARCHAR(100) NOT NULL,
    acronimo NVARCHAR(20)
);

CREATE TABLE Usuario (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombres NVARCHAR(100) NOT NULL,
    apellidos NVARCHAR(100),
    id_tipo_documento UNIQUEIDENTIFIER NOT NULL,
    documento NVARCHAR(50),
    tipo_usuario NVARCHAR(50),
    email NVARCHAR(150),
    direccion NVARCHAR(255),
    contraseña NVARCHAR(255),
    fecha_creado DATE DEFAULT GETDATE(),
    fecha_actualizado DATE,
    id_rol UNIQUEIDENTIFIER NOT NULL, 
    FOREIGN KEY (id_tipo_documento) REFERENCES Tipo_documento(id),
    FOREIGN KEY (id_rol) REFERENCES Rol(id)
);

CREATE TABLE Log_Sistema (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    id_usuario UNIQUEIDENTIFIER NOT NULL, 
    descripcion NVARCHAR(500),
    fecha_creado DATE DEFAULT GETDATE(),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id)
);

CREATE TABLE Tipo_dispositivo (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombre NVARCHAR(100) NOT NULL
);

CREATE TABLE Dispositivo (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    serial NVARCHAR(100),
    marca NVARCHAR(100),
    modelo NVARCHAR(100),
    sistema NVARCHAR(100),
    descripcion NVARCHAR(500),
    foto_url NVARCHAR(255),
    qr NVARCHAR(255),
    id_tipo_dispositivo UNIQUEIDENTIFIER NOT NULL, 
    id_usuario UNIQUEIDENTIFIER NOT NULL,          
    fecha_creado DATE DEFAULT GETDATE(),
    fecha_actualizado DATE,
    FOREIGN KEY (id_tipo_dispositivo) REFERENCES Tipo_dispositivo(id),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id)
);

CREATE TABLE Tipo_registro (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombre NVARCHAR(100) NOT NULL
);

CREATE TABLE Auditoria_Negocio (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    fecha_registro DATE,
    id_tipo_registro UNIQUEIDENTIFIER NOT NULL,  
    registrado_por UNIQUEIDENTIFIER NOT NULL,    
    descripcion NVARCHAR(500),
    FOREIGN KEY (id_tipo_registro) REFERENCES Tipo_registro(id),
    FOREIGN KEY (registrado_por) REFERENCES Usuario(id)
);

CREATE TABLE Tipo_Reporte (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombre NVARCHAR(100) NOT NULL
);

CREATE TABLE Sede (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    nombre_sede NVARCHAR(150)
);

CREATE TABLE Reporte (
    id UNIQUEIDENTIFIER PRIMARY KEY DEFAULT NEWID(),
    generado_por UNIQUEIDENTIFIER NOT NULL,   
    sede UNIQUEIDENTIFIER NOT NULL,           
    descripcion NVARCHAR(500),
    fecha_generado DATE DEFAULT GETDATE(),
    url_archivo NVARCHAR(255),
    id_tipo_reporte UNIQUEIDENTIFIER NOT NULL, 
    fecha_creado DATE,
    fecha_actualizado DATE,
    FOREIGN KEY (generado_por) REFERENCES Usuario(id),
    FOREIGN KEY (sede) REFERENCES Sede(id),
    FOREIGN KEY (id_tipo_reporte) REFERENCES Tipo_Reporte(id)
);