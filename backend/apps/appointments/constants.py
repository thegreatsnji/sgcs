"""Constantes do módulo de consultas."""

from django.db import models

from apps.reception.constants import QueuePriority


class AppointmentStatus(models.TextChoices):
    AGENDADA = "AGENDADA", "Agendada"
    CONFIRMADA = "CONFIRMADA", "Confirmada"
    EM_ESPERA = "EM_ESPERA", "Em espera"
    EM_CONSULTA = "EM_CONSULTA", "Em consulta"
    CONCLUIDA = "CONCLUIDA", "Concluída"
    CANCELADA = "CANCELADA", "Cancelada"
    FALTA = "FALTA", "Falta"


# Compatibilidade com estados legados (migração de dados)
LEGACY_STATUS_MAP = {
    "SCHEDULED": AppointmentStatus.AGENDADA,
    "CONFIRMED": AppointmentStatus.CONFIRMADA,
    "IN_PROGRESS": AppointmentStatus.EM_CONSULTA,
    "COMPLETED": AppointmentStatus.CONCLUIDA,
    "CANCELLED": AppointmentStatus.CANCELADA,
    "NO_SHOW": AppointmentStatus.FALTA,
}

ACTIVE_APPOINTMENT_STATUSES = {
    AppointmentStatus.AGENDADA,
    AppointmentStatus.CONFIRMADA,
    AppointmentStatus.EM_ESPERA,
    AppointmentStatus.EM_CONSULTA,
}

DOCTOR_QUEUE_STATUSES = {
    AppointmentStatus.CONFIRMADA,
    AppointmentStatus.EM_ESPERA,
    AppointmentStatus.EM_CONSULTA,
}

DEFAULT_DURATION_MINUTES = 30
APPOINTMENT_NUMBER_PREFIX = "CON"


class DiagnosticoTipo(models.TextChoices):
    PRINCIPAL = "PRINCIPAL", "Principal"
    SECUNDARIO = "SECUNDARIO", "Secundário"


class PedidoEstado(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    EM_PROCESSAMENTO = "EM_PROCESSAMENTO", "Em processamento"
    CONCLUIDO = "CONCLUIDO", "Concluído"
    CANCELADO = "CANCELADO", "Cancelado"


class PedidoLaboratorioEstadoFaturacao(models.TextChoices):
    AGUARDA_REGULARIZACAO = "AGUARDA_REGULARIZACAO", "Aguarda regularização"
    REGULARIZADO = "REGULARIZADO", "Regularizado"
    NAO_APLICAVEL = "NAO_APLICAVEL", "Não aplicável"
