"""Serviço de prescrições médicas."""

from django.db import transaction

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.appointments.models import Appointment
from apps.doctors.constants import PrescricaoEstado
from apps.doctors.models import MedicamentoPrescrito, PlanoTerapeutico, Prescricao
from apps.doctors.services.cache_service import DoctorsCacheService
from core.events.event_bus import event_bus
from core.events.events import EventNames


class PrescriptionService:
    @staticmethod
    def _log(action, user, request, obj, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type="prescricao",
            resource_id=str(obj.pk),
            metadata=metadata or {},
        )

    @staticmethod
    @transaction.atomic
    def criar_prescricao(*, consulta_id: int, medico, data: dict, request=None) -> Prescricao:
        consulta = Appointment.objects.select_related("patient").get(pk=consulta_id)
        prescricao = Prescricao.objects.create(
            consulta=consulta,
            paciente=consulta.patient,
            medico=medico,
            observacoes=data.get("observacoes", ""),
        )
        for med in data.get("medicamentos", []):
            MedicamentoPrescrito.objects.create(prescricao=prescricao, **med)
        if data.get("plano"):
            PlanoTerapeutico.objects.create(
                consulta=consulta,
                prescricao=prescricao,
                **data["plano"],
            )
        PrescriptionService._log(
            AuditAction.PRESCRICAO_CRIADA,
            medico,
            request,
            prescricao,
            f"Prescrição #{prescricao.pk} criada.",
        )
        event_bus.publish(
            EventNames.DOCTOR_PRESCRIPTION_CREATED,
            {"prescricao_id": prescricao.pk, "paciente_id": consulta.patient_id},
        )
        DoctorsCacheService.invalidate_historico(consulta.patient_id)
        from apps.doctors.tasks import enviar_prescricao_email

        enviar_prescricao_email.delay(prescricao.pk)
        return prescricao

    @staticmethod
    @transaction.atomic
    def aprovar_prescricao(prescricao_id: int, user, request=None) -> Prescricao:
        prescricao = Prescricao.objects.get(pk=prescricao_id)
        prescricao.estado = PrescricaoEstado.APROVADA
        prescricao.save(update_fields=["estado", "updated_at"])
        PrescriptionService._log(
            AuditAction.PRESCRICAO_EDITADA,
            user,
            request,
            prescricao,
            "Prescrição aprovada.",
            {"estado": PrescricaoEstado.APROVADA},
        )
        DoctorsCacheService.invalidate_historico(prescricao.paciente_id)
        return prescricao

    @staticmethod
    @transaction.atomic
    def concluir_prescricao(prescricao_id: int, user, request=None) -> Prescricao:
        prescricao = Prescricao.objects.get(pk=prescricao_id)
        prescricao.estado = PrescricaoEstado.CONCLUIDA
        prescricao.save(update_fields=["estado", "updated_at"])
        PrescriptionService._log(
            AuditAction.PRESCRICAO_EDITADA,
            user,
            request,
            prescricao,
            "Prescrição concluída.",
        )
        DoctorsCacheService.invalidate_historico(prescricao.paciente_id)
        return prescricao

    @staticmethod
    def historico_paciente(paciente_id: int) -> dict:
        cached = DoctorsCacheService.get_historico(paciente_id)
        if cached:
            return cached
        data = {
            "prescricoes": list(
                Prescricao.objects.filter(paciente_id=paciente_id).values(
                    "id", "estado", "created_at", "consulta_id"
                )
            ),
            "tratamentos": list(
                __import__("apps.doctors.models", fromlist=["Tratamento"])
                .Tratamento.objects.filter(paciente_id=paciente_id)
                .values("id", "tipo", "estado", "data_inicio")
            ),
        }
        DoctorsCacheService.set_historico(paciente_id, data)
        return data
