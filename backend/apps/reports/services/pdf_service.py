"""Exportação de relatórios em PDF."""

import io
from datetime import datetime
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


class PdfExportService:
    @staticmethod
    def export_report(titulo: str, data: dict[str, Any], clinica_nome: str = "SauVida Clínica") -> bytes:
        buffer = io.BytesIO()
        gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")

        def _footer(canvas, doc):
            canvas.saveState()
            canvas.setFont("Helvetica", 8)
            canvas.drawString(2 * cm, 1.2 * cm, f"{clinica_nome} — Gerado em {gerado_em}")
            canvas.drawRightString(
                A4[0] - 2 * cm,
                1.2 * cm,
                f"Página {doc.page}",
            )
            canvas.restoreState()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )
        styles = getSampleStyleSheet()
        story = [
            Paragraph(clinica_nome, styles["Heading2"]),
            Paragraph(titulo, styles["Title"]),
            Paragraph(f"<i>Metadados: exportação SGCS — {gerado_em}</i>", styles["Normal"]),
            Spacer(1, 12),
        ]
        rows = [["Campo", "Valor"]]
        PdfExportService._flatten(data, rows)
        table = Table(rows, colWidths=[200, 300], repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e40af")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ]
            )
        )
        story.append(table)
        doc.build(story, onFirstPage=_footer, onLaterPages=_footer)
        return buffer.getvalue()

    @staticmethod
    def _flatten(data: dict, rows: list, prefix: str = "") -> None:
        for key, value in data.items():
            label = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
            if isinstance(value, dict):
                PdfExportService._flatten(value, rows, label)
            elif isinstance(value, list):
                rows.append([label, f"{len(value)} registos"])
                for idx, item in enumerate(value[:20]):
                    if isinstance(item, dict):
                        PdfExportService._flatten(item, rows, f"{label}[{idx}]")
                    else:
                        rows.append([f"{label}[{idx}]", str(item)])
            else:
                rows.append([label, str(value)])
