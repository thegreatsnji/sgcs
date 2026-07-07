"""Serviço de seguimento clínico."""

from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.doctors.models import SeguimentoClinico
from apps.doctors.services.cache_service import DoctorsCacheService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class FollowupService:
    @staticmethod
    @transaction.atomic
    def agendar_seguimento(*, consulta_id: int, medico, data: dict, request=None) -> SeguimentoClinico:
        consulta = Appointment.objects.select_related("patient").get(pk=consulta_id)
        data_prevista = data["data_prevista"]
        if isinstance(data_prevista, str):
            from datetime import date

            data_prevista = date.fromisoformat(data_prevista)

        scheduled_at = timezone.make_aware(
            datetime.combine(data_prevista, datetime.min.time().replace(hour=9))
        )
        nova_consulta = AppointmentService.criar_consulta(
            patient_id=consulta.patient_id,
            user=medico,
            scheduled_at=scheduled_at,
            doctor_id=medico.pk,
            chief_complaint=data.get("motivo", "Seguimento clínico"),
            notes=data.get("observacoes", ""),
            request=request,
        )
        seguimento = SeguimentoClinico.objects.create(
            consulta_origem=consulta,
            paciente=consulta.patient,
            medico=medico,
            data_prevista=data_prevista,
            motivo=data.get("motivo", ""),
            observacoes=data.get("observacoes", ""),
            consulta_agendada=nova_consulta,
        )
        AuditService.log(
            action=AuditAction.SEGUIMENTO_AGENDADO,
            user=medico,
            request=request,
            description=f"Seguimento agendado para {data_prevista}.",
            resource_type="seguimento",
            resource_id=str(seguimento.pk),
            metadata={"consulta_agendada_id": nova_consulta.pk},
        )
        event_bus.publish(
            EventNames.DOCTOR_FOLLOWUP_CREATED,
            {"seguimento_id": seguimento.pk, "consulta_id": nova_consulta.pk},
        )
        DoctorsCacheService.invalidate_historico(consulta.patient_id)
        from apps.doctors.tasks import lembrar_seguimento

        lembrar_seguimento.delay(seguimento.pk)
        return seguimento
