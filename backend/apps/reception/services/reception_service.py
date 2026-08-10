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
    TRIAGE_PRIORITY_MAP,
    TRIAGE_WAIT_MINUTES,
    CheckInStatus,
    MINOR_AGE_THRESHOLD,
    PRIORITY_ORDER,
    PatientAgeCategory,
    QueuePriority,
    QueueStatus,
    ReferralDepartment,
    TriageColor,
    VisitPurpose,
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
        allowed = {UserRole.RECECIONISTA, UserRole.ENFERMEIRO}
        if user.role not in allowed:
            raise ValueError("Apenas receção ou enfermagem podem efectuar triagem.")

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
        ).select_related("check_in").order_by("position"):
            triage_color = entry.check_in.triage_color
            if triage_color in TRIAGE_WAIT_MINUTES:
                entry.estimated_wait_minutes = TRIAGE_WAIT_MINUTES[triage_color]
            else:
                entry.estimated_wait_minutes = max(
                    0, (entry.position - 1) * DEFAULT_WAIT_MINUTES_PER_POSITION
                )
            entry.save(update_fields=["estimated_wait_minutes", "updated_at"])

    @staticmethod
    @transaction.atomic
    def _insert_queue_position(priority: str) -> int:
        active_entries = list(
            WaitingQueue.objects.select_for_update()
            .filter(status__in=ReceptionService.ACTIVE_QUEUE_STATUSES)
            .select_related("check_in")
            .order_by("position")
        )
        new_rank = PRIORITY_ORDER.get(priority, PRIORITY_ORDER[QueuePriority.NORMAL])
        insert_index = len(active_entries)

        for index, entry in enumerate(active_entries):
            entry_rank = PRIORITY_ORDER.get(entry.check_in.priority, PRIORITY_ORDER[QueuePriority.NORMAL])
            if entry_rank > new_rank:
                insert_index = index
                break

        position = insert_index + 1
        for entry in active_entries[insert_index:]:
            WaitingQueue.objects.filter(pk=entry.pk).update(position=F("position") + 1)
        return position

    @staticmethod
    def _resolve_priority(priority: str | None, triage_color: str | None) -> str:
        if triage_color and triage_color in TRIAGE_PRIORITY_MAP:
            return TRIAGE_PRIORITY_MAP[triage_color]
        return priority or QueuePriority.NORMAL

    @staticmethod
    def _resolve_wait_minutes(triage_color: str | None, position: int) -> int:
        if triage_color in TRIAGE_WAIT_MINUTES:
            return TRIAGE_WAIT_MINUTES[triage_color]
        return max(0, (position - 1) * DEFAULT_WAIT_MINUTES_PER_POSITION)

    @staticmethod
    @transaction.atomic
    def check_in(
        patient_id: int,
        user,
        *,
        priority: str = QueuePriority.NORMAL,
        triage_color: str | None = None,
        age_at_check_in: int | None = None,
        weight=None,
        temperature=None,
        blood_pressure: str = "",
        height_cm: int | None = None,
        spo2: int | None = None,
        heart_rate: int | None = None,
        respiratory_rate: int | None = None,
        race: str = "",
        visit_purpose: str = "",
        symptoms: str = "",
        notes: str = "",
        request=None,
    ) -> ReceptionCheckIn:
        ReceptionService._ensure_receptionist(user)
        patient = PatientService.get_active_queryset().get(pk=patient_id)

        if ReceptionService._patient_has_active_queue(patient):
            raise ValueError("O paciente já se encontra na fila de espera.")

        resolved_priority = ReceptionService._resolve_priority(priority, triage_color)

        age_category = ""
        if age_at_check_in is not None:
            age_category = (
                PatientAgeCategory.MINOR
                if age_at_check_in < MINOR_AGE_THRESHOLD
                else PatientAgeCategory.ADULT
            )

        check_in = ReceptionCheckIn.objects.create(
            patient=patient,
            receptionist=user,
            priority=resolved_priority,
            triage_color=triage_color or "",
            age_at_check_in=age_at_check_in,
            age_category_at_check_in=age_category,
            weight=weight,
            temperature=temperature,
            blood_pressure=blood_pressure,
            height_cm=height_cm,
            spo2=spo2,
            heart_rate=heart_rate,
            respiratory_rate=respiratory_rate,
            race=race,
            visit_purpose=visit_purpose or VisitPurpose.CONSULTA,
            symptoms=symptoms,
            notes=notes,
            status=CheckInStatus.WAITING,
        )

        position = ReceptionService._insert_queue_position(resolved_priority)
        WaitingQueue.objects.create(
            check_in=check_in,
            patient=patient,
            position=position,
            status=QueueStatus.WAITING,
            estimated_wait_minutes=ReceptionService._resolve_wait_minutes(triage_color, position),
        )
        ReceptionService._recalculate_estimated_times()
        ReceptionService._invalidate_queue_cache()

        triage_label = dict(TriageColor.choices).get(triage_color, triage_color) if triage_color else ""
        triage_info = f", triagem {triage_label}" if triage_label else ""
        AuditService.log(
            action=AuditAction.RECEPTION_CHECK_IN,
            user=user,
            request=request,
            description=(
                f"Triagem do paciente {patient.full_name} "
                f"(prioridade {resolved_priority}{triage_info})."
            ),
            resource_type="reception_check_in",
            resource_id=str(check_in.pk),
            metadata={
                "patient_id": patient.pk,
                "priority": resolved_priority,
                "triage_color": triage_color,
            },
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
    def get_patient_preferred_doctor_id(patient_id: int) -> int | None:
        from apps.appointments.constants import AppointmentStatus
        from apps.appointments.models import Appointment

        appointment = (
            Appointment.objects.filter(
                patient_id=patient_id,
                doctor_id__isnull=False,
                status=AppointmentStatus.CONCLUIDA,
            )
            .order_by("-completed_at", "-scheduled_at")
            .first()
        )
        return appointment.doctor_id if appointment else None

    @staticmethod
    def is_doctor_available_for_assignment(doctor_id: int) -> bool:
        from apps.appointments.constants import AppointmentStatus
        from apps.appointments.models import Appointment

        today = timezone.localdate()
        return not Appointment.objects.filter(
            doctor_id=doctor_id,
            consultation_date=today,
            status=AppointmentStatus.EM_CONSULTA,
        ).exists()

    @staticmethod
    def get_doctor_assignment_options(patient_id: int) -> dict:
        from apps.appointments.constants import AppointmentStatus
        from apps.appointments.models import Appointment
        from apps.authentication.models import User, UserRole

        preferred_id = ReceptionService.get_patient_preferred_doctor_id(patient_id)
        doctors_qs = User.objects.filter(role=UserRole.MEDICO, is_active=True).order_by(
            "first_name", "last_name"
        )
        today = timezone.localdate()

        doctors = []
        for doctor in doctors_qs:
            in_consultation = Appointment.objects.filter(
                doctor_id=doctor.pk,
                consultation_date=today,
                status=AppointmentStatus.EM_CONSULTA,
            ).exists()
            waiting_count = Appointment.objects.filter(
                doctor_id=doctor.pk,
                consultation_date=today,
                status=AppointmentStatus.EM_ESPERA,
            ).count()
            doctors.append(
                {
                    "id": doctor.pk,
                    "full_name": doctor.get_full_name(),
                    "available": not in_consultation,
                    "waiting_count": waiting_count,
                    "is_preferred": doctor.pk == preferred_id,
                }
            )

        preferred_doctor = None
        if preferred_id:
            preferred = doctors_qs.filter(pk=preferred_id).first()
            if preferred:
                preferred_doctor = {
                    "id": preferred.pk,
                    "full_name": preferred.get_full_name(),
                    "available": ReceptionService.is_doctor_available_for_assignment(preferred.pk),
                }

        suggested_doctor_id = None
        if preferred_doctor and preferred_doctor["available"]:
            suggested_doctor_id = preferred_doctor["id"]
        else:
            available = [row for row in doctors if row["available"]]
            if available:
                suggested_doctor_id = min(available, key=lambda row: row["waiting_count"])["id"]

        return {
            "preferred_doctor": preferred_doctor,
            "suggested_doctor_id": suggested_doctor_id,
            "doctors": doctors,
        }

    @staticmethod
    @transaction.atomic
    def assign_to_doctor(
        *,
        queue_id: int | None = None,
        check_in_id: int | None = None,
        user,
        reason: str = "",
        doctor_id: int | None = None,
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

        assignment = ReceptionService.get_doctor_assignment_options(entry.patient_id)
        resolved_doctor_id = doctor_id or assignment.get("suggested_doctor_id")
        if not resolved_doctor_id:
            raise ValueError("Seleccione um médico disponível para este utente.")

        from apps.authentication.models import User, UserRole

        doctor = User.objects.filter(pk=resolved_doctor_id, role=UserRole.MEDICO, is_active=True).first()
        if not doctor:
            raise ValueError("Médico inválido ou inactivo.")
        if not ReceptionService.is_doctor_available_for_assignment(resolved_doctor_id):
            raise ValueError(
                "O médico seleccionado está em consulta. Escolha outro médico disponível."
            )

        referral = Referral.objects.create(
            patient=entry.patient,
            check_in=check_in,
            from_department=ReferralDepartment.RECEPTION,
            to_department=ReferralDepartment.DOCTOR,
            reason=reason or "Encaminhamento para consulta médica.",
            referred_by=user,
            assigned_doctor=doctor,
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
            metadata={
                "patient_id": entry.patient_id,
                "queue_id": entry.pk,
                "doctor_id": resolved_doctor_id,
            },
        )

        from apps.appointments.services.appointment_service import AppointmentService

        AppointmentService.create_from_handoff(
            referral,
            user=user,
            request=request,
            doctor_id=resolved_doctor_id,
        )
        return referral

    @staticmethod
    def get_history(*, patient_id: int | None = None, limit: int = 50):
        queryset = ReceptionCheckIn.objects.select_related("patient", "receptionist").order_by("-check_in_time")
        if patient_id:
            queryset = queryset.filter(patient_id=patient_id)
        return queryset[:limit]
