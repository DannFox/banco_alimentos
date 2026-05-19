"""
Generación de Excel y PDF con el registro del inventario y movimientos.
"""
from __future__ import annotations

from io import BytesIO

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from inventario.models import Movimiento, Producto


def generar_excel_registro() -> bytes:
    wb = Workbook()
    bold = Font(bold=True)

    ws1 = wb.active
    ws1.title = "Inventario"
    ws1.append(["ID", "Nombre", "Código barras", "Cantidad", "Vencimiento"])
    for c in ws1[1]:
        c.font = bold
    for p in Producto.objects.all().order_by("fecha_vencimiento"):
        ws1.append(
            [
                p.id,
                p.nombre,
                p.codigo_barras or "",
                p.cantidad,
                p.fecha_vencimiento.isoformat(),
            ]
        )

    ws2 = wb.create_sheet("Movimientos")
    ws2.append(["ID", "Producto", "Tipo", "Cantidad", "Usuario", "Fecha", "Nota"])
    for c in ws2[1]:
        c.font = bold
    for m in Movimiento.objects.select_related("producto", "usuario").all()[:5000]:
        ws2.append(
            [
                m.id,
                m.producto.nombre,
                m.get_tipo_display(),
                m.cantidad,
                m.usuario.username if m.usuario else "",
                timezone.localtime(m.registrado_en).strftime("%Y-%m-%d %H:%M"),
                m.nota or "",
            ]
        )

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()


def generar_pdf_registro() -> bytes:
    buf = BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter, title="Registro Banco de Alimentos")
    styles = getSampleStyleSheet()
    story = []
    now = timezone.localtime(timezone.now()).strftime("%Y-%m-%d %H:%M")
    story.append(Paragraph("Registro de inventario — Banco de Alimentos", styles["Title"]))
    story.append(Paragraph(f"Generado: {now}", styles["Normal"]))
    story.append(Spacer(1, 12))

    productos = list(Producto.objects.all().order_by("fecha_vencimiento")[:200])
    data = [["ID", "Nombre", "Cant.", "Vence"]]
    for p in productos:
        data.append([str(p.id), p.nombre[:40], str(p.cantidad), p.fecha_vencimiento.isoformat()])

    t = Table(data, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2d6a4f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f0f0")]),
            ]
        )
    )
    story.append(t)
    story.append(Spacer(1, 16))
    story.append(Paragraph("Últimos movimientos", styles["Heading2"]))
    movs = Movimiento.objects.select_related("producto", "usuario").all()[:30]
    md = [["Tipo", "Producto", "Cant.", "Usuario", "Fecha"]]
    for m in movs:
        md.append(
            [
                m.get_tipo_display(),
                m.producto.nombre[:30],
                str(m.cantidad),
                m.usuario.username if m.usuario else "",
                timezone.localtime(m.registrado_en).strftime("%Y-%m-%d %H:%M"),
            ]
        )
    t2 = Table(md, repeatRows=1)
    t2.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1b4332")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ]
        )
    )
    story.append(t2)

    doc.build(story)
    return buf.getvalue()
