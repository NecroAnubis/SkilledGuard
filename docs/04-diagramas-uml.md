# Diagramas UML

**Proyecto:** Skilled Guard

Ocho diagramas de siete tipos distintos: el de secuencia aparece dos veces, una por cada flujo crítico (inicio de sesión y validación en portería).

UML 2.5 define catorce tipos. Se incluyen los siete que aportan información que los demás no dan; los omitidos se listan al final con el motivo. Preferir siete diagramas que digan algo antes que catorce por completar el conteo.

---

## 1. Casos de uso

Qué puede hacer cada actor.

```mermaid
graph LR
    ADM(("👤<br>Administrador"))
    SEG(("👤<br>Seguridad"))
    USU(("👤<br>Usuario"))

    subgraph SG[Sistema Skilled Guard]
        CU01([Iniciar sesión])
        CU02([Registrar usuario])
        CU03([Asignar rol])
        CU04([Registrar equipo])
        CU05([Generar código QR])
        CU06([Consultar equipos])
        CU07([Registrar ingreso])
        CU08([Registrar salida])
        CU09([Consultar estado del equipo])
        CU10([Consultar trazabilidad])
        CU11([Exportar reporte])
        CU12([Consultar auditoría])
    end

    ADM --> CU01
    ADM --> CU02
    ADM --> CU03
    ADM --> CU04
    ADM --> CU12

    SEG --> CU01
    SEG --> CU07
    SEG --> CU08
    SEG --> CU09
    SEG --> CU10
    SEG --> CU11

    USU --> CU01
    USU --> CU06

    CU04 -.->|include| CU05
    CU07 -.->|include| CU09
    CU08 -.->|include| CU09
```

**Nota sobre las relaciones `include`:** registrar un equipo genera siempre su código QR, y registrar un movimiento consulta siempre el estado actual para validar la transición. No son pasos opcionales.

---

## 2. Clases

Las 15 entidades del modelo y sus relaciones.

```mermaid
classDiagram
    class Usuario {
        +int id
        +str nombres
        +str apellidos
        +str documento UK
        +str direccion
        +str contrasena_hash
        +nombre_completo() str
    }

    class Rol {
        +int id
        +str nombre UK
        +str descripcion
    }

    class UsuarioRol {
        +int id
        +int id_usuario
        +int id_rol
    }

    class TipoDocumento {
        +int id
        +str nombre UK
        +str acronimo
    }

    class Dispositivo {
        +int id
        +str serial UK
        +str marca
        +str modelo
        +str sistema
        +str qr UK
    }

    class TipoDispositivo {
        +int id
        +str nombre UK
    }

    class AuditoriaNegocio {
        +int id
        +int id_dispositivo
        +int id_tipo_registro
        +int registrado_por
        +str observacion
        +datetime fecha_creado
    }

    class TipoRegistro {
        +int id
        +str nombre UK
    }

    class LogSistema {
        +int id
        +int id_accion
        +int id_usuario
        +int id_objeto_afectado
    }

    class LogDetalle {
        +int id
        +str campo_afectado
        +str valor_anterior
        +str valor_nuevo
    }

    class TipoAccion {
        +int id
        +str nombre UK
    }

    class ObjetoAfectado {
        +int id
        +str nombre_tabla UK
    }

    class Reporte {
        +int id
        +int generado_por
        +str filtros_aplicados
        +str url_archivo
    }

    class TipoReporte {
        +int id
        +str nombre UK
    }

    class ConsultaReporte {
        +int id
        +str entidad_consultada
        +str filtro_aplicado
    }

    Usuario "1" -- "*" UsuarioRol
    Rol "1" -- "*" UsuarioRol
    TipoDocumento "1" -- "*" Usuario
    Usuario "1" -- "*" Dispositivo : es responsable de
    TipoDispositivo "1" -- "*" Dispositivo
    Dispositivo "1" -- "*" AuditoriaNegocio : registra movimientos
    TipoRegistro "1" -- "*" AuditoriaNegocio
    Usuario "1" -- "*" AuditoriaNegocio : registrado por
    LogSistema "1" -- "*" LogDetalle
    TipoAccion "1" -- "*" LogSistema
    ObjetoAfectado "1" -- "*" LogSistema
    Usuario "1" -- "*" LogSistema
    Usuario "1" -- "*" Reporte
    TipoReporte "1" -- "*" Reporte
    Reporte "1" -- "*" ConsultaReporte
```

**`UK`** indica restricción de unicidad. `Dispositivo.qr` es única porque es el identificador que la portería escanea: dos equipos con el mismo código harían imposible saber cuál se movió.

---

## 3. Secuencia — Inicio de sesión

```mermaid
sequenceDiagram
    actor U as Usuario
    participant API as AuthController
    participant SEG as security.py
    participant BD as PostgreSQL

    U->>API: POST /auth/login (documento, contraseña)
    API->>BD: SELECT usuario WHERE documento = ?
    BD-->>API: usuario o nada

    alt Usuario no existe o contraseña incorrecta
        API-->>U: 401 "Documento o contraseña incorrectos"
        Note over API,U: El mismo mensaje en ambos casos:<br/>distinguirlos revelaría qué documentos existen
    else Credenciales válidas
        API->>SEG: verificar_contrasena(entrada, hash)
        SEG-->>API: verdadero
        API->>BD: SELECT roles del usuario
        BD-->>API: ["Administrador"]
        API->>SEG: crear_token(usuario, roles)
        SEG-->>API: JWT firmado
        API-->>U: 200 { access_token }
    end
```

---

## 4. Secuencia — Validación en portería

El flujo central del sistema.

```mermaid
sequenceDiagram
    actor V as Vigilante
    participant API as MovimientosController
    participant SEG as security.py
    participant POR as porteria.py
    participant BD as PostgreSQL

    V->>API: POST /movimientos (qr, tipo)
    API->>SEG: usuario_actual(token)
    SEG->>BD: SELECT usuario
    SEG-->>API: vigilante

    API->>SEG: exige_rol(Administrador, Seguridad)
    alt Rol no autorizado
        SEG-->>V: 403
    end

    API->>BD: SELECT dispositivo WHERE qr = ?
    alt Código QR desconocido
        BD-->>API: nada
        API-->>V: 404 "El código QR no corresponde a un equipo"
    else Equipo encontrado
        API->>POR: registrar(dispositivo, tipo, vigilante)
        POR->>BD: SELECT ... FOR UPDATE (bloquea la fila)
        Note over POR,BD: El bloqueo evita que dos escaneos<br/>simultáneos dupliquen el movimiento
        POR->>BD: SELECT último movimiento
        BD-->>POR: último o nada
        POR->>POR: validar_transicion(estado, tipo)

        alt Transición inválida
            POR-->>API: MovimientoInvalido
            API-->>V: 409 "El equipo ya se encuentra dentro"
        else Transición válida
            POR->>BD: INSERT movimiento
            POR-->>API: movimiento
            API->>BD: INSERT rastro de auditoría
            API->>BD: COMMIT
            API-->>V: 201 { movimiento }
        end
    end
```

---

## 5. Actividad — Ingreso y salida de un equipo

```mermaid
flowchart TD
    INICIO([El equipo llega a portería]) --> ESCANEAR[El vigilante escanea el código QR]
    ESCANEAR --> BUSCAR{¿El código<br/>está registrado?}

    BUSCAR -->|No| ERROR1[Mostrar: equipo no registrado]
    ERROR1 --> REGISTRAR[Enviar al administrador<br/>para registrar el equipo]
    REGISTRAR --> FIN1([Fin])

    BUSCAR -->|Sí| ESTADO{¿Cuál es el<br/>estado del equipo?}

    ESTADO -->|Fuera| SENTIDO1{¿Qué registra<br/>el vigilante?}
    ESTADO -->|Dentro| SENTIDO2{¿Qué registra<br/>el vigilante?}

    SENTIDO1 -->|Ingreso| OK1[Registrar ingreso]
    SENTIDO1 -->|Salida| RECHAZO1[Rechazar:<br/>el equipo no ha ingresado]

    SENTIDO2 -->|Salida| OK2[Registrar salida]
    SENTIDO2 -->|Ingreso| RECHAZO2[Rechazar:<br/>el equipo ya está dentro]

    OK1 --> AUDITAR[Dejar rastro de auditoría]
    OK2 --> AUDITAR
    AUDITAR --> CONFIRMAR[Confirmar al vigilante]
    CONFIRMAR --> FIN2([Fin])

    RECHAZO1 --> REVISAR[El vigilante verifica<br/>la situación del equipo]
    RECHAZO2 --> REVISAR
    REVISAR --> FIN3([Fin])
```

---

## 6. Estados — Ciclo de vida de un equipo

```mermaid
stateDiagram-v2
    [*] --> Registrado : el administrador da de alta el equipo

    Registrado --> Fuera : se genera y se pega el código QR

    Fuera --> Dentro : registrar ingreso
    Dentro --> Fuera : registrar salida

    Fuera --> Fuera : intento de salida rechazado (409)
    Dentro --> Dentro : intento de ingreso rechazado (409)

    note right of Fuera
        Estado inicial de todo equipo.
        Un equipo sin movimientos
        se considera fuera.
    end note

    note right of Dentro
        El equipo está dentro de
        las instalaciones.
    end note
```

Las transiciones reflexivas (`Fuera → Fuera`, `Dentro → Dentro`) representan los intentos rechazados: el sistema responde, pero **el estado no cambia y no se registra ningún movimiento**. Son la representación de los requerimientos RF-14 y RF-15.

---

## 7. Componentes

```mermaid
graph TB
    subgraph CLIENTE[Cliente]
        NAV[Navegador web<br/>lector de QR]
    end

    subgraph API[Contenedor: API]
        ROUT[Routers<br/>capa HTTP]
        SEG[security<br/>JWT y roles]
        POR[porteria<br/>reglas de negocio]
        AUD[auditoria<br/>rastro de acciones]
        QR[qr<br/>generación de códigos]
        REP[reportes<br/>Excel y PDF]
        CONS[consultas<br/>filtros compartidos]
        ORM[SQLAlchemy<br/>ORM]
    end

    subgraph DATOS[Contenedor: Base de datos]
        PG[(PostgreSQL 16)]
    end

    NAV -->|HTTP/JSON| ROUT
    ROUT --> SEG
    ROUT --> POR
    ROUT --> AUD
    ROUT --> QR
    ROUT --> REP
    REP --> CONS
    ROUT --> CONS
    POR --> ORM
    AUD --> ORM
    SEG --> ORM
    CONS --> ORM
    ORM -->|SQL| PG
```

`consultas` lo usan tanto los endpoints como los reportes: es lo que garantiza que el Excel y la pantalla muestren exactamente lo mismo ante los mismos filtros.

---

## 8. Despliegue

```mermaid
graph TB
    subgraph DISPOSITIVO[Dispositivo del vigilante]
        BROWSER[Navegador<br/>con cámara]
    end

    subgraph SERVIDOR[Servidor · Docker Engine]
        subgraph C1[Contenedor: api]
            UVICORN[Uvicorn + FastAPI<br/>puerto 8000]
        end
        subgraph C2[Contenedor: db]
            POSTGRES[(PostgreSQL 16<br/>puerto 5432)]
        end
        VOL[(Volumen<br/>datos_postgres)]
    end

    subgraph NUBE[Supabase · opcional]
        SUPA[(PostgreSQL gestionado)]
    end

    BROWSER -->|HTTP :8000| UVICORN
    UVICORN -->|red interna| POSTGRES
    POSTGRES --- VOL
    UVICORN -.->|DATABASE_URL alterna| SUPA

    style NUBE stroke-dasharray: 5 5
```

**Dos modos de despliegue.** En local, la base de datos corre en su propio contenedor con un volumen persistente — el sistema funciona sin internet, lo que importa porque la portería puede quedarse sin conexión. Cambiando `DATABASE_URL` la misma API apunta a PostgreSQL gestionado en Supabase, sin tocar el código.

---

## Diagramas omitidos y por qué

| Diagrama | Motivo |
|---|---|
| Comunicación | Muestra la misma información que los de secuencia, con otra disposición |
| Objetos | Una instantánea de instancias no agrega nada sobre el diagrama de clases en un modelo de este tamaño |
| Paquetes | La estructura de módulos ya se ve en el diagrama de componentes |
| Tiempos | No hay restricciones temporales que modelar |
| Estructura compuesta | Ningún componente tiene partes internas colaborando entre sí |
| Perfil | Sirve para extender el propio UML; no aplica |
| Vista general de interacción | Solo se justifica al coordinar muchos diagramas de secuencia |
