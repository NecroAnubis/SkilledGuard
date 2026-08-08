"""Generación de códigos QR para los equipos.

La imagen se genera cada vez que se pide, no se guarda. Un PNG de ~1 KB se
produce más rápido de lo que se leería de disco, y así no hay archivos que
queden desincronizados si el código del equipo cambia.
"""

from io import BytesIO

import qrcode


def generar_png(contenido: str) -> bytes:
    imagen = qrcode.make(contenido)
    buffer = BytesIO()
    imagen.save(buffer, format="PNG")
    return buffer.getvalue()
