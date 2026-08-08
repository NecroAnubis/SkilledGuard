"""Datos iniciales del sistema.

Resuelve el problema del huevo y la gallina: `/usuarios` exige rol Administrador,
así que el primer administrador no puede crearse por la API.

Uso:  python -m app.seed
Es idempotente: correrlo dos veces no duplica nada.
"""

import os
import sys

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Rol, TipoDispositivo, TipoDocumento, Usuario, UsuarioRol
from app.security import ROL_ADMINISTRADOR, ROL_SEGURIDAD, ROL_USUARIO, hashear_contrasena

TIPOS_DOCUMENTO = [
    ("Cédula de ciudadanía", "CC", "Documento nacional"),
    ("Tarjeta de identidad", "TI", "Documento para menores de edad"),
    ("Cédula de extranjería", "CE", "Documento para extranjeros"),
]

ROLES = [
    (ROL_ADMINISTRADOR, "Gestión total del sistema"),
    (ROL_SEGURIDAD, "Validación de ingreso y salida en portería"),
    (ROL_USUARIO, "Registro y consulta de sus propios equipos"),
]

TIPOS_DISPOSITIVO = [
    ("Computador", "Equipo portátil o de escritorio"),
    ("Celular", "Teléfono móvil"),
    ("Tablet", "Dispositivo tipo tableta"),
]


def _obtener_o_crear(db: Session, modelo, **campos):
    existente = db.scalar(select(modelo).filter_by(nombre=campos["nombre"]))
    if existente is not None:
        return existente
    registro = modelo(**campos)
    db.add(registro)
    db.flush()
    return registro


def sembrar(db: Session, documento_admin: str, contrasena_admin: str) -> None:
    for nombre, acronimo, descripcion in TIPOS_DOCUMENTO:
        _obtener_o_crear(
            db, TipoDocumento, nombre=nombre, acronimo=acronimo, descripcion=descripcion
        )
    for nombre, descripcion in TIPOS_DISPOSITIVO:
        _obtener_o_crear(db, TipoDispositivo, nombre=nombre, descripcion=descripcion)

    roles = {
        nombre: _obtener_o_crear(db, Rol, nombre=nombre, descripcion=descripcion)
        for nombre, descripcion in ROLES
    }

    admin = db.scalar(select(Usuario).where(Usuario.documento == documento_admin))
    if admin is None:
        cedula = db.scalar(select(TipoDocumento).filter_by(acronimo="CC"))
        admin = Usuario(
            nombres="Administrador",
            apellidos="del Sistema",
            id_tipo_documento=cedula.id,
            documento=documento_admin,
            contrasena_hash=hashear_contrasena(contrasena_admin),
        )
        db.add(admin)
        db.flush()
        db.add(UsuarioRol(id_usuario=admin.id, id_rol=roles[ROL_ADMINISTRADOR].id))

    db.commit()


def main() -> None:
    documento = os.environ.get("ADMIN_DOCUMENTO", "1000000000")
    contrasena = os.environ.get("ADMIN_CONTRASENA")
    if not contrasena:
        sys.exit(
            "Falta ADMIN_CONTRASENA. Ejemplo:\n"
            "  ADMIN_CONTRASENA='una-clave-larga' python -m app.seed"
        )

    with SessionLocal() as db:
        sembrar(db, documento, contrasena)
    print(f"Datos iniciales cargados. Administrador: documento {documento}")


if __name__ == "__main__":
    main()
