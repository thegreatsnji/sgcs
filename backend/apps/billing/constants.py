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
    ("LABORATORIO", "Laboratório"),
    ("ECOGRAFIA", "Ecografia"),
    ("ENFERMAGEM", "Enfermagem"),
    ("PROCEDIMENTO", "Procedimento"),
    ("CIRURGIA", "Cirurgia"),
    ("MATERNIDADE", "Maternidade"),
    ("MED_URGENCIA", "Medicamento de Urgência"),
    ("MATERIAL_CLINICO", "Material Clínico"),
    ("IMUNIZACAO", "Imunização"),
    ("DOCUMENTO", "Documento"),
    ("CARTAO", "Cartão"),
    ("OBSERVACAO_CLINICA", "Observação Clínica"),
    # Legado (compatibilidade)
    ("EXAME", "Exame (legado)"),
    ("OUTRO", "Outro"),
    ("INTERNAMENTO", "Internamento (legado)"),
]

DEFAULT_SERVICE_CATEGORY = "OUTRO"
DEFAULT_SERVICE_CURRENCY = "FCFA"
DEFAULT_BILLING_UNIT = "unidade"

# Importação CSV/JSON — rótulos aceites (sem acentos opcionais)
SERVICE_CATEGORY_IMPORT_ALIASES: dict[str, str] = {
    "CONSULTA": "CONSULTA",
    "LABORATORIO": "LABORATORIO",
    "LABORATÓRIO": "LABORATORIO",
    "EXAME": "LABORATORIO",
    "ECOGRAFIA": "ECOGRAFIA",
    "ENFERMAGEM": "ENFERMAGEM",
    "PROCEDIMENTO": "PROCEDIMENTO",
    "CIRURGIA": "CIRURGIA",
    "MATERNIDADE": "MATERNIDADE",
    "MED_URGENCIA": "MED_URGENCIA",
    "MEDICAMENTO DE URGENCIA": "MED_URGENCIA",
    "MEDICAMENTO DE URGÊNCIA": "MED_URGENCIA",
    "MATERIAL_CLINICO": "MATERIAL_CLINICO",
    "MATERIAL CLÍNICO": "MATERIAL_CLINICO",
    "IMUNIZACAO": "IMUNIZACAO",
    "IMUNIZAÇÃO": "IMUNIZACAO",
    "DOCUMENTO": "DOCUMENTO",
    "CARTAO": "CARTAO",
    "CARTÃO": "CARTAO",
    "OBSERVACAO_CLINICA": "OBSERVACAO_CLINICA",
    "OBSERVAÇÃO CLÍNICA": "OBSERVACAO_CLINICA",
    "OUTRO": "OUTRO",
}

PRICE_REVIEW_MARKER = "REVISAR_COM_CLINICA"

# Catálogo operacional (piloto SauVida)
CATALOGO_VERSAO_ATIVA = "SAUVIDA_V1"
CATALOGO_VERSAO_LEGADO = "LEGACY_PREPARED"


class OrigemPrecoItem(models.TextChoices):
    CATALOGO = "CATALOGO", "Catálogo"
    REDUCAO_RECECAO = "REDUCAO_RECECAO", "Redução na receção"
    REDUCAO_AUTORIZADA = "REDUCAO_AUTORIZADA", "Redução autorizada"
    CAMPANHA = "CAMPANHA", "Campanha"
    GRATUITO_AUTORIZADO = "GRATUITO_AUTORIZADO", "Gratuito autorizado"
    OUTRO = "OUTRO", "Outro"


class MotivoReducao(models.TextChoices):
    DIFICULDADE_FINANCEIRA = "DIFICULDADE_FINANCEIRA", "Dificuldade financeira do paciente"
    APOIO_SOCIAL = "APOIO_SOCIAL", "Apoio social"
    PACIENTE_CARENCIADO = "PACIENTE_CARENCIADO", "Paciente carenciado"
    DESCONTO_DIRECAO = "DESCONTO_DIRECAO", "Desconto autorizado pela Direção"
    CAMPANHA_CLINICA = "CAMPANHA_CLINICA", "Campanha da clínica"
    FUNCIONARIO_FAMILIAR = "FUNCIONARIO_FAMILIAR", "Funcionário ou familiar"
    PAGAMENTO_PARCIAL = "PAGAMENTO_PARCIAL", "Pagamento parcial negociado"
    CORTESIA = "CORTESIA", "Cortesia"
    OUTRO = "OUTRO", "Outro"


class EstadoAutorizacaoReducao(models.TextChoices):
    NAO_APLICAVEL = "NAO_APLICAVEL", "Não aplicável"
    APROVADA_AUTOMATICAMENTE = "APROVADA_AUTOMATICAMENTE", "Aprovada automaticamente"
    PENDENTE = "PENDENTE", "Pendente"
    APROVADA = "APROVADA", "Aprovada"
    REJEITADA = "REJEITADA", "Rejeitada"
    CANCELADA = "CANCELADA", "Cancelada"
