"""Serviços do módulo de receção."""

from django.core.cache import cache
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import UserRole
from apps.patients.models import Patient
from apps.patients.services.patient_service import PatientService
from apps.reception.constants import (
    DEFAULT_WAIT_MINUTES_PER_POSITION,
    QUEUE_CACHE_KEY,
    QUEUE_CACHE_TTL,
    CheckInStatus,
    QueuePriority,
    QueueStatus,
    ReferralDepartment,
)
from apps.reception.models import ReceptionCheckIn, Referral, WaitingQueue


class ReceptionService:
    ACTIVE_CHECK_IN_STATUSES = {CheckInStatus.WAITING, CheckInStatus.IN_CONSULTATION}
    ACTIVE_QUEUE_STATUSES = {QueueStatus.WAITING, QueueStatus.CALLED, QueueStatus.IN_SERVICE}

    @staticmethod
    def _invalidate_queue_cache() -> None:
        cache.delete(QUEUE_CACHE_KEY)

    @staticmethod
    def _ensure_receptionist(user) -> None:
        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return
        if user.role != UserRole.RECECIONISTA:
            raise ValueError("Apenas rececionistas podem efectuar check-in.")

    @staticmethod
    def _patient_has_active_queue(patient: Patient) -> bool:
        return WaitingQueue.objects.filter(
            patient=patient,
            status__in=ReceptionService.ACTIVE_QUEUE_STATUSES,
        ).exists()

    @staticmethod
    def _recalculate_estimated_times() -> None:
        for entry in WaitingQueue.objects.filter(
            status__in=ReceptionService.ACTIVE_QUEUE_STATUSES
        ).order_by("position"):
            entry.estimated_wait_minutes = max(0, (entry.position - 1) * DEFAULT_WAIT_MINUTES_PER_POSITION)
            entry.save(update_fields=["estimated_wait_minutes", "updated_at"])

    @staticmethod
    @transaction.atomic
    def _reorder_queue_for_priority(priority: str) -> int:
        active_entries = list(
            WaitingQueue.objects.select_for_update()
            .filter(status__in=ReceptionService.ACTIVE_QUEUE_STATUSES)
            .order_by("position")
        )
        next_position = len(active_entries) + 1
        if priority != QueuePriority.EMERGENCY:
            return next_position

        for entry in active_entries:
            WaitingQueue.objects.filter(pk=entry.pk).update(position=F("position") + 1)
        return 1

    @staticmethod
    @transaction.atomic
    def check_in(
        patient_id: int,
        user,
        *,
        priority: str = QueuePriority.NORMAL,
        notes: str = "",
        request=None,
    ) -> ReceptionCheckIn:
        ReceptionService._ensure_receptionist(user)
        patient = PatientService.get_active_queryset().get(pk=patient_id)

        if ReceptionService._patient_has_active_queue(patient):
            raise ValueError("O paciente já se encontra na fila de espera.")

        check_in = ReceptionCheckIn.objects.create(
            patient=patient,
            receptionist=user,
            priority=priority,
            notes=notes,
            status=CheckInStatus.WAITING,
        )

        position = ReceptionService._reorder_queue_for_priority(priority)
        WaitingQueue.objects.create(
            check_in=check_in,
            patient=patient,
            position=position,
            status=QueueStatus.WAITING,
            estimated_wait_minutes=max(0, (position - 1) * DEFAULT_WAIT_MINUTES_PER_POSITION),
        )
        ReceptionService._recalculate_estimated_times()
        ReceptionService._invalidate_queue_cache()

        AuditService.log(
            action=AuditAction.RECEPTION_CHECK_IN,
            user=user,
            request=request,
            description=f"Check-in do paciente {patient.full_name} (prioridade {priority}).",
            resource_type="reception_check_in",
            resource_id=str(check_in.pk),
            metadata={"patient_id": patient.pk, "priority": priority},
        )
        return check_in

    @staticmethod
    def get_active_queue(use_cache: bool = True):
        if use_cache:
            cached = cache.get(QUEUE_CACHE_KEY)
            if cached is not None:
                return cached

        queryset = (
            WaitingQueue.objects.filter(status__in=ReceptionService.ACTIVE_QUEUE_STATUSES)
            .select_related("patient", "check_in", "check_in__receptionist")
            .order_by("position")
        )
        if use_cache:
            cache.set(QUEUE_CACHE_KEY, queryset, QUEUE_CACHE_TTL)
        return queryset

    @staticmethod
    @transaction.atomic
    def update_queue_entry(queue_id: int, user, *, status: str | None = None, request=None) -> WaitingQueue:
        entry = WaitingQueue.objects.select_for_update().select_related("check_in", "patient").get(pk=queue_id)
        old_status = entry.status

        if status and status != old_status:
            entry.status = status
            entry.save(update_fields=["status", "updated_at"])

            check_in = entry.check_in
            if status == QueueStatus.IN_SERVICE:
                check_in.status = CheckInStatus.IN_CONSULTATION
            elif status == QueueStatus.COMPLETED:
                check_in.status = CheckInStatus.COMPLETED
            elif status == QueueStatus.CANCELLED:
                check_in.status = CheckInStatus.CANCELLED
            check_in.save(update_fields=["status", "updated_at"])

            AuditService.log(
                action=AuditAction.RECEPTION_STATUS_CHANGE,
                user=user,
                request=request,
                description=(
                    f"Estado da fila alterado para {status} — paciente {entry.patient.full_name}."
                ),
                resource_type="waiting_queue",
                resource_id=str(entry.pk),
                metadata={"old_status": old_status, "new_status": status, "patient_id": entry.patient_id},
            )

            if status in {QueueStatus.COMPLETED, QueueStatus.CANCELLED}:
                ReceptionService._compact_queue_positions()
            ReceptionService._recalculate_estimated_times()
            ReceptionService._invalidate_queue_cache()

        return entry

    @staticmethod
    def _compact_queue_positions() -> None:
        active = WaitingQueue.objects.filter(
            status__in=ReceptionService.ACTIVE_QUEUE_STATUSES
        ).order_by("position")
        for index, entry in enumerate(active, start=1):
            if entry.position != index:
                WaitingQueue.objects.filter(pk=entry.pk).update(position=index)

    @staticmethod
    @transaction.atomic
    def assign_to_doctor(
        *,
        queue_id: int | None = None,
        check_in_id: int | None = None,
        user,
        reason: str = "",
        request=None,
    ) -> Referral:
        if queue_id:
            entry = WaitingQueue.objects.select_for_update().select_related("check_in", "patient").get(pk=queue_id)
        elif check_in_id:
            entry = WaitingQueue.objects.select_for_update().select_related("check_in", "patient").get(
                check_in_id=check_in_id
            )
        else:
            raise ValueError("É necessário indicar queue_id ou check_in_id.")

        if entry.status not in ReceptionService.ACTIVE_QUEUE_STATUSES:
            raise ValueError("Este utente já não está activo na fila.")

        entry.status = QueueStatus.IN_SERVICE
        entry.save(update_fields=["status", "updated_at"])

        check_in = entry.check_in
        check_in.status = CheckInStatus.IN_CONSULTATION
        check_in.save(update_fields=["status", "updated_at"])

        referral = Referral.objects.create(
            patient=entry.patient,
            check_in=check_in,
            from_department=ReferralDepartment.RECEPTION,
            to_department=ReferralDepartment.DOCTOR,
            reason=reason or "Encaminhamento para consulta médica.",
            referred_by=user,
        )

        ReceptionService._recalculate_estimated_times()
        ReceptionService._invalidate_queue_cache()

        AuditService.log(
            action=AuditAction.RECEPTION_ASSIGN_DOCTOR,
            user=user,
            request=request,
            description=f"Paciente {entry.patient.full_name} encaminhado para médico.",
            resource_type="referral",
            resource_id=str(referral.pk),
            metadata={"patient_id": entry.patient_id, "queue_id": entry.pk},
        )

        from apps.appointments.services.appointment_service import AppointmentService

        AppointmentService.create_from_handoff(referral, user=user, request=request)
        return referral

    @staticmethod
    def get_history(*, patient_id: int | None = None, limit: int = 50):
        queryset = ReceptionCheckIn.objects.select_related("patient", "receptionist").order_by("-check_in_time")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset[:limit]
