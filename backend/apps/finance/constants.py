"""Constantes do módulo financeiro."""

from django.db import models

CACHE_TTL = 60

CACHE_KEY_DASHBOARD = "sgcs:dashboard:finance"
CACHE_KEY_CASHFLOW = "sgcs:finance:cashflow"
CACHE_KEY_REPORT = "sgcs:finance:report:{tipo}:{periodo}"


class CaixaEstado(models.TextChoices):
    ABERTO = "ABERTO", "Aberto"
    FECHADO = "FECHADO", "Fechado"


class MovimentoTipo(models.TextChoices):
    ENTRADA = "ENTRADA", "Entrada"
    SAIDA = "SAIDA", "Saída"
    TRANSFERENCIA = "TRANSFERENCIA", "Transferência"
    AJUSTE = "AJUSTE", "Ajuste"


class MovimentoOrigem(models.TextChoices):
    PAGAMENTO = "PAGAMENTO", "Pagamento"
    DESPESA = "DESPESA", "Despesa"
    CORRECCAO = "CORRECCAO", "Correcção"
    MANUAL = "MANUAL", "Manual"


class DespesaEstado(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    APROVADA = "APROVADA", "Aprovada"
    PAGA = "PAGA", "Paga"
    CANCELADA = "CANCELADA", "Cancelada"


class CategoriaTipo(models.TextChoices):
    RECEITA = "RECEITA", "Receita"
    DESPESA = "DESPESA", "Despesa"


DESPESA_CATEGORIAS = [
    ("MEDICAMENTOS", "Medicamentos"),
    ("EQUIPAMENTOS", "Equipamentos"),
    ("MATERIAL_CLINICO", "Material Clínico"),
    ("ENERGIA", "Energia"),
    ("INTERNET", "Internet"),
    ("AGUA", "Água"),
    ("SALARIOS", "Salários"),
    ("MANUTENCAO", "Manutenção"),
    ("LIMPEZA", "Limpeza"),
    ("OUTROS", "Outros"),
]

DEFAULT_DESPESA_CATEGORIA = "OUTROS"

DEFAULT_CAIXA_CODIGO = "CAIXA-001"
