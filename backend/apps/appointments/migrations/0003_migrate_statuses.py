"""Migração de estados legados e números de consulta."""

from django.db import migrations
from django.utils import timezone


def migrate_statuses_and_numbers(apps, schema_editor):
    Appointment = apps.get_model("appointments", "Appointment")
    mapping = {
        "SCHEDULED": "AGENDADA",
        "CONFIRMED": "CONFIRMADA",
        "IN_PROGRESS": "EM_CONSULTA",
        "COMPLETED": "CONCLUIDA",
        "CANCELLED": "CANCELADA",
        "NO_SHOW": "FALTA",
    }
    year = timezone.now().year
    sequence = 0
    for appointment in Appointment.objects.order_by("id"):
        if appointment.status in mapping:
            appointment.status = mapping[appointment.status]
        if not appointment.appointment_number:
            sequence += 1
            appointment.appointment_number = f"CON-{year}-{sequence:05d}"
        if appointment.scheduled_at and not appointment.consultation_date:
            appointment.consultation_date = appointment.scheduled_at.date()
        appointment.save(
            update_fields=["status", "appointment_number", "consultation_date"]
        )


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0002_appointment_appointment_number_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_statuses_and_numbers, migrations.RunPython.noop),
    ]
