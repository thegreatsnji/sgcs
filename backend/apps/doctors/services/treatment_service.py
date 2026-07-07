"""Serviço de tratamentos."""

from django.db import transaction

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.appointments.models import Appointment
from apps.doctors.constants import TratamentoEstado
from apps.doctors.models import Tratamento
from apps.doctors.services.cache_service import DoctorsCacheService


class TreatmentService:
    @staticmethod
    @transaction.atomic
    def criar_tratamento(*, consulta_id: int, user, data: dict, request=None) -> Tratamento:
        consulta = Appointment.objects.select_related("patient").get(pk=consulta_id)
        tratamento = Tratamento.objects.create(
            consulta=consulta,
            paciente=consulta.patient,
            responsavel=user,
            **data,
        )
        AuditService.log(
            action=AuditAction.TRATAMENTO_CRIADO,
            user=user,
            request=request,
            description=f"Tratamento #{tratamento.pk} criado.",
            resource_type="tratamento",
            resource_id=str(tratamento.pk),
        )
        DoctorsCacheService.invalidate_historico(consulta.patient_id)
        return tratamento

    @staticmethod
    @transaction.atomic
    def concluir_tratamento(tratamento_id: int, user, request=None) -> Tratamento:
        tratamento = Tratamento.objects.get(pk=tratamento_id)
        tratamento.estado = TratamentoEstado.CONCLUIDO
        tratamento.save(update_fields=["estado", "updated_at"])
        AuditService.log(
            action=AuditAction.TRATAMENTO_CONCLUIDO,
            user=user,
            request=request,
            description=f"Tratamento #{tratamento.pk} concluído.",
            resource_type="tratamento",
            resource_id=str(tratamento.pk),
        )
        DoctorsCacheService.invalidate_historico(tratamento.paciente_id)
        return tratamento
