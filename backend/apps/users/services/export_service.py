"""Estrutura de exportação — implementação na Sprint 4."""

from typing import Any


class ExportService:
    SUPPORTED_FORMATS = ("pdf", "excel", "csv")

    @staticmethod
    def export_users(format: str, queryset: Any) -> bytes:
        if format not in ExportService.SUPPORTED_FORMATS:
            raise ValueError(f"Formato não suportado: {format}")
        raise NotImplementedError(
            "A exportação de utilizadores será implementada na Sprint 4."
        )
