# 01 – Visión y alcance

**Proyecto:** SkilledGuard  
**Documento:** Visión y alcance  
**Referencia:** Complementa la descripción del [README principal](../README.md) del proyecto.

---

## 1. Visión

**SkilledGuard** es un sistema de auditoría que permite gestionar usuarios, dispositivos, registros de negocio y reportes, con autenticación JWT, roles y trazabilidad mediante logs del sistema.

El sistema está pensado para organizaciones que necesitan:

- Control de usuarios y acceso según roles.
- Registro de dispositivos (por ejemplo equipos corporativos) asociados a usuarios.
- Auditoría de eventos de negocio (ingresos, salidas u otros tipos de registro).
- Generación y consulta de reportes por sede y tipo.
- Trazabilidad de acciones mediante logs asociados a usuarios.

---

## 2. Usuarios objetivo

| Tipo de usuario   | Descripción                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| **Administrador** | Gestión de usuarios, dispositivos, auditorías, reportes y consulta de logs.|
| **Usuario**       | Uso de las funciones permitidas según permisos asignados (rol Usuario).     |

Los roles están definidos en la base de datos (catálogo `Rol`); los tipos documentados en el proyecto son Administrador y Usuario.

---

## 3. Alcance funcional (qué hace el sistema)

Lo siguiente está **implementado** o **previsto** en el proyecto:

| Área                  | Descripción                                                                 | Estado en el proyecto        |
|-----------------------|-----------------------------------------------------------------------------|------------------------------|
| **Usuarios y roles**  | Gestión de usuarios con roles (Administrador / Usuario), tipos de documento y autenticación segura. | Implementado (API).          |
| **Dispositivos**      | Registro de dispositivos (ej. laptops, smartphones) asociados a usuarios, con serial, marca, modelo, sistema y códigos QR. | Implementado (API).          |
| **Auditoría de negocio** | Registro de eventos de ingreso/salida u otros tipos, con fecha y usuario que registra. | Implementado (API).          |
| **Reportes**          | Generación de reportes por sede y tipo (diario, mensual), con URL de archivo. | Implementado (API).          |
| **Logs del sistema**  | Trazabilidad de acciones mediante logs asociados a usuarios.                | Implementado (API).          |
| **Autenticación**     | Login con email y contraseña; emisión de token JWT; endpoints protegidos con Bearer token. | Implementado (API).          |
| **Interfaz de usuario** | Aplicación web para uso por usuarios y administradores.                    | Prevista (carpeta CodigoForntend). |

La solución está organizada en **base de datos** (SQL Server con scripts DDL/DML), **backend (API REST)** en .NET 9 y **frontend** (carpeta preparada para implementación).

---

## 4. Fuera de alcance (qué no incluye este proyecto)

Para evitar malentendidos, se considera **fuera del alcance** actual:

- Aplicación móvil nativa (iOS/Android).
- Integraciones con sistemas externos (ERP, nómina, etc.) no documentadas en el proyecto.
- Generación automática de archivos de reporte (PDF/Excel) en el backend (la API gestiona metadatos y URL de archivo).
- Single Sign-On (SSO) o federación de identidad más allá de JWT propio.
- Módulos o funcionalidades no descritas en el [README](../README.md) ni en la documentación del proyecto.

Si en el futuro se incorpora alguno de estos puntos, este documento y el [Índice de documentación](INDICE_DOCUMENTACION.md) deberían actualizarse.

---

## 5. Criterios de éxito

Se considera que el proyecto cumple sus objetivos cuando:

1. **Base de datos:** La base de datos `auditoria_sistema` se puede crear y poblar ejecutando los scripts DDL y DML en el orden indicado en el [README](../README.md) (sección "Paso a paso: configuración y ejecución").
2. **Backend:** La API se ejecuta correctamente (por ejemplo con `dotnet run` sobre el proyecto Auditorias), responde al login y expone los recursos documentados en Swagger.
3. **Autenticación:** El endpoint `POST /api/Auth/login` devuelve un token JWT y los endpoints protegidos aceptan el header `Authorization: Bearer <token>`.
4. **Documentación:** Existe documentación suficiente para configurar, ejecutar e integrar la API (README, Swagger y documentos en la carpeta Documentacion).
5. **Frontend (cuando se implemente):** La interfaz de usuario consume la API con autenticación JWT y permite a usuarios y administradores realizar las operaciones previstas.

Los criterios 1 a 4 se pueden verificar con el estado actual del proyecto; el criterio 5 aplica cuando la carpeta CodigoForntend contenga la aplicación frontend.

---

## 6. Referencias

- [README principal del proyecto](../README.md)
- [Índice de documentación](INDICE_DOCUMENTACION.md)
- Base de datos: [Base_de_Datos/README.txt](../Base_de_Datos/README.txt)
