"""Constantes do módulo de faturação."""

from decimal import Decimal

from django.db import models


class OrcamentoEstado(models.TextChoices):
    RASCUNHO = "RASCUNHO", "Rascunho"
    PENDENTE = "PENDENTE", "Pendente"
    APROVADO = "APROVADO", "Aprovado"
    EXPIRADO = "EXPIRADO", "Expirado"


class FaturaEstado(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PARCIAL = "PARCIAL", "Parcial"
    PAGA = "PAGA", "Paga"
    CANCELADA = "CANCELADA", "Cancelada"


class PagamentoEstado(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PROCESSADO = "PROCESSADO", "Processado"
    CONFIRMADO = "CONFIRMADO", "Confirmado"
    REEMBOLSADO = "REEMBOLSADO", "Reembolsado"


class MetodoPagamento(models.TextChoices):
    DINHEIRO = "DINHEIRO", "Dinheiro"
    TRANSFERENCIA = "TRANSFERENCIA", "Transferência"
    CARTAO = "CARTAO", "Cartão"
    MOBILE_MONEY = "MOBILE_MONEY", "Mobile Money"
    OUTRO = "OUTRO", "Outro"


ORCAMENTO_EDITABLE_STATUSES = {
    OrcamentoEstado.RASCUNHO,
    OrcamentoEstado.PENDENTE,
}

FATURA_EDITABLE_STATUSES = {
    FaturaEstado.PENDENTE,
    FaturaEstado.PARCIAL,
}

QUOTE_NUMBER_PREFIX = "ORC"
INVOICE_NUMBER_PREFIX = "FAT"
RECEIPT_NUMBER_PREFIX = "REC"

DEFAULT_TAX_RATE = Decimal("0.00")

CACHE_KEY_SERVICES = "sgcs:billing:services"
CACHE_KEY_DASHBOARD = "sgcs:dashboard:billing"
CACHE_KEY_PATIENT_HISTORY = "sgcs:billing:patient_history:{patient_id}"

SERVICE_CATEGORIES = [
    ("CONSULTA", "Consulta"),
    ("EXAME", "Exame"),
    ("PROCEDIMENTO", "Procedimento"),
    ("INTERNAMENTO", "Internamento"),
    ("OUTRO", "Outro"),
]

DEFAULT_SERVICE_CATEGORY = "OUTRO"
