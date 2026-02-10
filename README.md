# 🛡️ Skilled Guard  
Sistema de Automatización para el Control de Ingreso de Equipos Tecnológicos – SENA

Skilled Guard es un proyecto desarrollado como parte de la formación en **Análisis y Desarrollo de Software (ADSO)** del SENA. Su objetivo es reemplazar el registro manual en minutas por un sistema digital seguro, rápido y auditable.

---

## ✅ Problema que Soluciona
Actualmente, el ingreso y salida de equipos tecnológicos se registra de forma manual, lo que genera:

Actualmente, el registro manual de equipos consume un promedio de 10 minutos por usuario y genera riesgos de seguridad, con un 35% de empresas en Bogotá reportando pérdidas por fallos en estos sistemas. Skilled Guard ataca este problema automatizando el registro mediante tecnología QR y bases de datos encriptadas.

**Skilled Guard automatiza este proceso** mediante un registro digital de usuarios y equipos, permitiendo validación rápida en portería.

- **Registro de Usuarios:** Gestión de roles (Administrador, Seguridad, Usuario).
- **Registro de Equipos:** Cada usuario puede registrar sus dispositivos (serial, modelo, marca).
- [cite_start]**Verificación QR:** El personal de seguridad puede escanear un QR para validar el ingreso o salida de un equipo en segundos[cite: 71, 200].
- [cite_start]**Trazabilidad:** Historial completo de movimientos de equipos para auditorías[cite: 74, 202].
- [cite_start]**Reportes:** Generación de reportes de ingreso/salida en PDF/Excel[cite: 111, 203].

## ✅ Funcionalidades Planeadas
✔ Registro de usuarios con roles (Administrador – Seguridad – Usuario)  
✔ Registro de equipos (serial, marca, modelo, descripción)  
✔ Validación en portería mediante código QR  
✔ Trazabilidad completa de entradas y salidas  
✔ Generación de reportes (PDF / Excel)

> Nota: Varias funcionalidades están en desarrollo.

---

## 🏗️ Estado Actual del Proyecto
✅ Backend iniciado en .NET  
✅ Arquitectura base del proyecto  
✅ Compilación y ejecución local  
❌ Base de datos aún no configurada  
❌ Frontend sin desarrollo aún  
❌ Módulo de QR pendiente

---

## 🧰 Tecnologías del Proyecto

### ✅ Backend (implementado)
- .NET 9
- ASP.NET Core Web API

### ✅ Planeado
- Base de Datos: MySQL
- Seguridad: JWT + Roles
- Frontend: (por definir)
- Reportes: (por definir)
- Pruebas: Postman + Swagger

---

## 🚀 Ejecutar el Backend
1. Clonar el repositorio:
```bash
git clone https://github.com/NecroAnubis/SkilledGuard.git
