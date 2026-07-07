"""Serviço de alta médica."""

from django.db import transaction

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.appointments.models import Appointment
from apps.doctors.models import AltaMedica
from apps.doctors.services.cache_service import DoctorsCacheService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class DischargeService:
    @staticmethod
    @transaction.atomic
    def emitir_alta(*, consulta_id: int, medico, data: dict, request=None) -> AltaMedica:
        consulta = Appointment.objects.select_related("patient").get(pk=consulta_id)
        alta, _ = AltaMedica.objects.update_or_create(
            consulta=consulta,
            defaults={
                "paciente": consulta.patient,
                "medico": medico,
                **data,
            },
        )
        AuditService.log(
            action=AuditAction.ALTA_MEDICA,
            user=medico,
            request=request,
            description=f"Alta médica emitida para consulta #{consulta_id}.",
            resource_type="alta",
            resource_id=str(alta.pk),
        )
        event_bus.publish(
            EventNames.DOCTOR_DISCHARGE_CREATED,
            {"alta_id": alta.pk, "paciente_id": consulta.patient_id},
        )
        DoctorsCacheService.invalidate_historico(consulta.patient_id)
        from apps.doctors.tasks import gerar_relatorio_alta

        gerar_relatorio_alta.delay(alta.pk)
        return alta
