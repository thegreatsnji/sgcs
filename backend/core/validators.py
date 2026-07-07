"""Validadores reutilizáveis."""

import re

from django.core.exceptions import ValidationError


PHONE_PATTERN = re.compile(r"^\+?[0-9]{7,15}$")


def validate_phone_number(value: str) -> str:
    if not PHONE_PATTERN.match(value):
        raise ValidationError("Introduza um número de telefone válido.")
    return value


def validate_positive_amount(value) -> None:
    if value is not None and value < 0:
        raise ValidationError("O valor deve ser positivo.")
