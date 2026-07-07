"""Constantes do módulo de receção."""

from django.db import models


class CheckInStatus(models.TextChoices):
    WAITING = "WAITING", "Em espera"
    IN_CONSULTATION = "IN_CONSULTATION", "Em consulta"
    COMPLETED = "COMPLETED", "Concluído"
    CANCELLED = "CANCELLED", "Cancelado"


class QueuePriority(models.TextChoices):
    LOW = "LOW", "Baixa"
    NORMAL = "NORMAL", "Normal"
    HIGH = "HIGH", "Alta"
    EMERGENCY = "EMERGENCY", "Emergência"


class QueueStatus(models.TextChoices):
    WAITING = "WAITING", "Em espera"
    CALLED = "CALLED", "Chamado"
    IN_SERVICE = "IN_SERVICE", "Em atendimento"
    COMPLETED = "COMPLETED", "Concluído"
    CANCELLED = "CANCELLED", "Cancelado"


class ReferralDepartment(models.TextChoices):
    RECEPTION = "RECEPTION", "Receção"
    DOCTOR = "DOCTOR", "Médico"
    LAB = "LAB", "Laboratório"
    BILLING = "BILLING", "Faturação"


PRIORITY_ORDER = {
    QueuePriority.EMERGENCY: 0,
    QueuePriority.HIGH: 1,
    QueuePriority.NORMAL: 2,
    QueuePriority.LOW: 3,
}

DEFAULT_WAIT_MINUTES_PER_POSITION = 15
QUEUE_CACHE_KEY = "sgcs:reception:queue"
QUEUE_CACHE_TTL = 30
