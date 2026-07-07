"""Validadores do módulo de pacientes."""

from datetime import date

from django.core.exceptions import ValidationError
from django.utils import timezone

from core.validators import validate_phone_number


def validate_birth_date(value: date) -> date:
    today = timezone.localdate()
    if value > today:
        raise ValidationError("A data de nascimento não pode ser futura.")
    age = today.year - value.year - (
        (today.month, today.day) < (value.month, value.day)
    )
    if age > 120:
        raise ValidationError("Data de nascimento inválida.")
    return value


def validate_patient_phone(value: str) -> str:
    return validate_phone_number(value)


def validate_insurance_dates(valid_from: date | None, valid_until: date | None) -> None:
    if valid_from and valid_until and valid_until < valid_from:
        raise ValidationError("A data de fim deve ser posterior à data de início.")


def validate_document_expiry(issued_at: date | None, expires_at: date | None) -> None:
    if issued_at and expires_at and expires_at < issued_at:
        raise ValidationError("A validade deve ser posterior à data de emissão.")
