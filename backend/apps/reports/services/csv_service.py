"""Exportação de relatórios em CSV."""

import csv
import io
from datetime import datetime
from typing import Any


class CsvExportService:
    @staticmethod
    def export_report(titulo: str, data: dict[str, Any], clinica_nome: str = "SauVida Clínica") -> bytes:
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        gerado_em = datetime.now().strftime("%d/%m/%Y %H:%M")
        writer.writerow([clinica_nome])
        writer.writerow([titulo])
        writer.writerow([f"Gerado em: {gerado_em}"])
        writer.writerow([])
        CsvExportService._write_dict(writer, data)
        return buffer.getvalue().encode("utf-8-sig")

    @staticmethod
    def _write_dict(writer, data: dict, prefix: str = "") -> None:
        for key, value in data.items():
            label = f"{prefix}{key}" if not prefix else f"{prefix}.{key}"
            if isinstance(value, dict):
                CsvExportService._write_dict(writer, value, label)
            elif isinstance(value, list):
                writer.writerow([label, f"{len(value)} itens"])
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        CsvExportService._write_dict(writer, item, f"{label}[{idx}]")
                    else:
                        writer.writerow([f"{label}[{idx}]", item])
            else:
                writer.writerow([label, value])
