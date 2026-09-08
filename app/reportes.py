"""Generación de reportes de movimientos en Excel y PDF.

Los archivos se producen en memoria y se envían al cliente; no se guardan en
disco. Un reporte es una foto de una consulta en un instante: guardarlo obliga
a decidir cuándo borrarlo, y el archivo queda desactualizado apenas cambian
los datos.
"""

from datetime import datetime
from io import BytesIO

from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

from app.models import AuditoriaNegocio

ENCABEZADOS = ["Fecha", "Tipo", "Serial", "Equipo", "Responsable", "Registrado por", "Observación"]


def _filas(movimientos: list[AuditoriaNegocio]) -> list[list[str]]:
    return [
        [
            m.fecha_creado.strftime("%Y-%m-%d %H:%M"),
            m.tipo_registro.nombre,
            m.dispositivo.serial,
            f"{m.dispositivo.marca} {m.dispositivo.modelo}",
            m.dispositivo.responsable,
            m.vigilante.nombre_completo,
            m.observacion or "",
        ]
        for m in movimientos
    ]


def generar_excel(movimientos: list[AuditoriaNegocio]) -> bytes:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Movimientos"

    relleno = PatternFill("solid", fgColor="1F4E78")
    for columna, encabezado in enumerate(ENCABEZADOS, start=1):
        celda = hoja.cell(row=1, column=columna, value=encabezado)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = relleno
        celda.alignment = Alignment(horizontal="center")

    for fila in _filas(movimientos):
        hoja.append(fila)

    for columna, encabezado in enumerate(ENCABEZADOS, start=1):
        ancho = max([len(encabezado)] + [len(f[columna - 1]) for f in _filas(movimientos)] or [0])
        hoja.column_dimensions[hoja.cell(row=1, column=columna).column_letter].width = min(
            ancho + 2, 40
        )

    # Congela el encabezado: en un reporte largo se pierde de vista al bajar.
    hoja.freeze_panes = "A2"

    buffer = BytesIO()
    libro.save(buffer)
    return buffer.getvalue()


class _ReportePDF(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 14)
        self.cell(
            0, 8, "Skilled Guard - Reporte de movimientos", align="C", new_x="LMARGIN", new_y="NEXT"
        )
        self.set_font("Helvetica", size=8)
        self.cell(
            0,
            5,
            f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", size=8)
        self.cell(0, 8, f"Página {self.page_no()} de {{nb}}", align="C")


# Anchos en mm; suman 277, el ancho útil de una hoja carta apaisada.
_ANCHOS = [30, 20, 30, 50, 50, 50, 47]


def generar_pdf(movimientos: list[AuditoriaNegocio]) -> bytes:
    pdf = _ReportePDF(orientation="L", format="Letter")
    pdf.alias_nb_pages()
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(31, 78, 120)
    pdf.set_text_color(255)
    for ancho, encabezado in zip(_ANCHOS, ENCABEZADOS, strict=True):
        pdf.cell(ancho, 7, encabezado, border=1, fill=True, align="C")
    pdf.ln()

    pdf.set_text_color(0)
    pdf.set_font("Helvetica", size=8)
    for fila in _filas(movimientos):
        for ancho, valor in zip(_ANCHOS, fila, strict=True):
            # El texto se recorta al ancho de la celda: sin esto una observación
            # larga desborda y descuadra toda la tabla.
            maximo = int(ancho / 1.8)
            texto = valor if len(valor) <= maximo else valor[: maximo - 1] + "…"
            pdf.cell(ancho, 6, texto, border=1)
        pdf.ln()

    if not movimientos:
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 8, "No hay movimientos para los filtros seleccionados.", align="C")

    return bytes(pdf.output())
