"""Serviço de evolução clínica."""

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.appointments.models import Appointment
from apps.doctors.models import EvolucaoClinica
from apps.doctors.services.cache_service import DoctorsCacheService


class ClinicalEvolutionService:
    @staticmethod
    def registar_evolucao(*, consulta_id: int, user, data: dict, request=None) -> EvolucaoClinica:
        consulta = Appointment.objects.select_related("patient").get(pk=consulta_id)
        evolucao = EvolucaoClinica.objects.create(
            consulta=consulta,
            paciente=consulta.patient,
            registado_por=user,
            **data,
        )
        AuditService.log(
            action=AuditAction.EVOLUCAO_ADICIONADA,
            user=user,
            request=request,
            description=f"Evolução clínica #{evolucao.pk} registada.",
            resource_type="evolucao",
            resource_id=str(evolucao.pk),
        )
        DoctorsCacheService.invalidate_historico(consulta.patient_id)
        return evolucao
