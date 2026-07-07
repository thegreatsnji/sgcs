"""Geração de números de processo clínico."""

from django.utils import timezone

from apps.patients.models import Patient


class PatientNumberService:
    PREFIX = "PAC"

    @classmethod
    def generate_next(cls) -> str:
        year = timezone.localdate().year
        prefix = f"{cls.PREFIX}-{year}-"
        last = (
            Patient.objects.filter(patient_number__startswith=prefix)
            .order_by("-patient_number")
            .values_list("patient_number", flat=True)
            .first()
        )
        if last:
            sequence = int(last.split("-")[-1]) + 1
        else:
            sequence = 1
        return f"{prefix}{sequence:05d}"
