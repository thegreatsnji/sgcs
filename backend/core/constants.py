"""Constantes globais do SGCS."""

from django.db import models


class UserRole(models.TextChoices):
    ADMINISTRADOR = "ADMINISTRADOR", "Administrador"
    RECECIONISTA = "RECECIONISTA", "Rececionista"
    MEDICO = "MEDICO", "Médico"
    ENFERMEIRO = "ENFERMEIRO", "Enfermeiro"
    LABORATORIO = "LABORATORIO", "Laboratório"
    FINANCEIRO = "FINANCEIRO", "Financeiro"


DEFAULT_PAGE_SIZE = 20
API_VERSION = "v1"
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"
CURRENCY_CODE = "XOF"
CURRENCY_SYMBOL = "FCFA"
