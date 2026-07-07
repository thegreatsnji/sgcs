"""Geração de números de consulta."""

from django.utils import timezone

from apps.appointments.constants import APPOINTMENT_NUMBER_PREFIX
from apps.appointments.models import Appointment


class AppointmentNumberService:
    @staticmethod
    def generate() -> str:
        year = timezone.now().year
        prefix = f"{APPOINTMENT_NUMBER_PREFIX}-{year}-"
        last = (
            Appointment.objects.filter(appointment_number__startswith=prefix)
            .order_by("-appointment_number")
            .values_list("appointment_number", flat=True)
            .first()
        )
        if last:
            try:
                sequence = int(last.split("-")[-1]) + 1
            except ValueError:
                sequence = 1
        else:
            sequence = 1
        return f"{prefix}{sequence:05d}"
