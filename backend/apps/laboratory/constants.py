"""Constantes do módulo de laboratório."""

from django.db import models


class PedidoLaboratorialEstado(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    RECEBIDO = "RECEBIDO", "Recebido"
    AGUARDANDO_COLHEITA = "AGUARDANDO_COLHEITA", "Aguardando colheita"
    EM_PROCESSAMENTO = "EM_PROCESSAMENTO", "Em processamento"
    CONCLUIDO = "CONCLUIDO", "Concluído"
    CANCELADO = "CANCELADO", "Cancelado"


# Alias com acento para documentação/UI (valor persistido sem acento)
PEDIDO_ESTADO_LABELS = {
    "PENDENTE": "Pendente",
    "RECEBIDO": "Recebido",
    "AGUARDANDO_COLHEITA": "Aguardando colheita",
    "EM_PROCESSAMENTO": "Em processamento",
    "CONCLUIDO": "Concluído",
    "CANCELADO": "Cancelado",
}

PENDING_STATUSES = {
    PedidoLaboratorialEstado.PENDENTE,
    PedidoLaboratorialEstado.RECEBIDO,
    PedidoLaboratorialEstado.AGUARDANDO_COLHEITA,
}

COLLECTION_QUEUE_STATUSES = {
    PedidoLaboratorialEstado.RECEBIDO,
    PedidoLaboratorialEstado.AGUARDANDO_COLHEITA,
}

FINAL_STATUSES = {
    PedidoLaboratorialEstado.CONCLUIDO,
    PedidoLaboratorialEstado.CANCELADO,
}

ORDER_NUMBER_PREFIX = "LAB"

DEFAULT_EXAM_CATEGORY = "GERAL"

EXAM_CATEGORIES = [
    ("HEMATOLOGIA", "Hematologia"),
    ("BIOQUIMICA", "Bioquímica"),
    ("MICROBIOLOGIA", "Microbiologia"),
    ("IMUNOLOGIA", "Imunologia"),
    ("GERAL", "Geral"),
]


class ResultadoLaboratorialEstado(models.TextChoices):
    EM_PROCESSAMENTO = "EM_PROCESSAMENTO", "Em processamento"
    RESULTADO_PENDENTE = "RESULTADO_PENDENTE", "Resultado pendente"
    VALIDADO = "VALIDADO", "Validado"
    ENTREGUE = "ENTREGUE", "Entregue"


RESULTADO_ESTADO_LABELS = {
    "EM_PROCESSAMENTO": "Em processamento",
    "RESULTADO_PENDENTE": "Resultado pendente",
    "VALIDADO": "Validado",
    "ENTREGUE": "Entregue",
}

RESULTADO_EDITABLE_STATUSES = {
    ResultadoLaboratorialEstado.EM_PROCESSAMENTO,
    ResultadoLaboratorialEstado.RESULTADO_PENDENTE,
}

class InterpretacaoParametro(models.TextChoices):
    NORMAL = "NORMAL", "Normal"
    ALTO = "ALTO", "Alto"
    BAIXO = "BAIXO", "Baixo"
    CRITICO = "CRITICO", "Crítico"


class TipoAnexoResultado(models.TextChoices):
    PDF = "PDF", "PDF"
    PNG = "PNG", "PNG"
    JPEG = "JPEG", "JPEG"
    DOCX = "DOCX", "DOCX"


ALLOWED_ATTACHMENT_MIMES = {
    "application/pdf": TipoAnexoResultado.PDF,
    "image/png": TipoAnexoResultado.PNG,
    "image/jpeg": TipoAnexoResultado.JPEG,
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": TipoAnexoResultado.DOCX,
}

CACHE_KEY_LAB_SUMMARY = "sgcs:laboratory:summary"
CACHE_KEY_LAB_RESULTS = "sgcs:laboratory:results"
