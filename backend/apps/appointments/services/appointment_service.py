"""Serviços do módulo de consultas."""

from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.appointments.constants import (
    ACTIVE_APPOINTMENT_STATUSES,
    DOCTOR_QUEUE_STATUSES,
    AppointmentStatus,
    DEFAULT_DURATION_MINUTES,
)
from apps.appointments.models import Appointment
from apps.appointments.services.number_service import AppointmentNumberService
from apps.appointments.validators import validate_doctor_availability, validate_scheduled_in_future
from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.authentication.models import UserRole
from apps.patients.constants import HistoryEventType
from apps.patients.services.history_service import PatientHistoryService
from apps.patients.services.patient_service import PatientService
from apps.reception.constants import CheckInStatus, QueuePriority, QueueStatus, VisitPurpose
from apps.reception.models import Referral, WaitingQueue


class AppointmentService:
    @staticmethod
    def _log_consulta(action, user, request, appointment, description, metadata=None):
        AuditService.log(
            action=action,
            user=user,
            request=request,
            description=description,
            resource_type="appointment",
            resource_id=str(appointment.pk),
            metadata=metadata or {"patient_id": appointment.patient_id},
        )

    @staticmethod
    def _ensure_doctor(user) -> None:
        if user.is_superuser or user.role == UserRole.ADMINISTRADOR:
            return
        if user.role != UserRole.MEDICO:
            raise ValueError("Apenas médicos podem efectuar esta acção.")

    @staticmethod
    def has_active_appointments(patient_id: int) -> bool:
        return Appointment.objects.filter(
            patient_id=patient_id,
            status__in=ACTIVE_APPOINTMENT_STATUSES,
        ).exists()

    @staticmethod
    def get_doctor_queue(doctor=None):
        queryset = (
            Appointment.objects.filter(status__in=DOCTOR_QUEUE_STATUSES)
            .select_related("patient", "doctor", "check_in", "referral", "queue_entry", "receptionist")
            .order_by("scheduled_at")
        )
        if doctor and doctor.role == UserRole.MEDICO and not doctor.is_superuser:
            # Fila exclusiva: só utentes explicitamente atribuídos a este médico.
            queryset = queryset.filter(doctor=doctor)
        return queryset

    @staticmethod
    def listar_consultas_do_dia(*, day=None, doctor_id: int | None = None):
        target = day or timezone.localdate()
        qs = Appointment.objects.filter(consultation_date=target).select_related("patient", "doctor")
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        return qs.order_by("scheduled_at")

    @staticmethod
    def listar_consultas_do_medico(doctor_id: int, *, day=None):
        return AppointmentService.listar_consultas_do_dia(day=day, doctor_id=doctor_id)

    @staticmethod
    @transaction.atomic
    def criar_consulta(
        *,
        patient_id: int,
        user,
        scheduled_at=None,
        doctor_id: int | None = None,
        duration_minutes: int = DEFAULT_DURATION_MINUTES,
        priority: str = QueuePriority.NORMAL,
        notes: str = "",
        chief_complaint: str = "",
        receptionist_id: int | None = None,
        request=None,
    ) -> Appointment:
        return AppointmentService.create(
            patient_id=patient_id,
            user=user,
            scheduled_at=scheduled_at,
            doctor_id=doctor_id,
            duration_minutes=duration_minutes,
            priority=priority,
            notes=notes,
            chief_complaint=chief_complaint,
            receptionist_id=receptionist_id,
            request=request,
        )

    @staticmethod
    @transaction.atomic
    def create(
        *,
        patient_id: int,
        user,
        scheduled_at=None,
        doctor_id: int | None = None,
        duration_minutes: int = DEFAULT_DURATION_MINUTES,
        priority: str = QueuePriority.NORMAL,
        notes: str = "",
        chief_complaint: str = "",
        receptionist_id: int | None = None,
        request=None,
    ) -> Appointment:
        patient = PatientService.get_active_queryset().get(pk=patient_id)
        when = scheduled_at or timezone.now()
        validate_scheduled_in_future(when)
        if doctor_id:
            validate_doctor_availability(
                doctor_id=doctor_id,
                scheduled_at=when,
                duration_minutes=duration_minutes,
            )

        appointment = Appointment.objects.create(
            patient=patient,
            doctor_id=doctor_id,
            receptionist_id=receptionist_id or (
                user.pk if getattr(user, "role", None) == UserRole.RECECIONISTA else None
            ),
            appointment_number=AppointmentNumberService.generate(),
            scheduled_at=when,
            consultation_date=when.date(),
            duration_minutes=duration_minutes,
            status=AppointmentStatus.AGENDADA,
            priority=priority,
            notes=notes,
            chief_complaint=chief_complaint,
            created_by=user,
        )
        AppointmentService._log_consulta(
            AuditAction.CONSULTA_CRIADA,
            user,
            request,
            appointment,
            f"Consulta {appointment.appointment_number} agendada para {patient.full_name}.",
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def create_from_handoff(referral: Referral, user, request=None, doctor_id: int | None = None) -> Appointment:
        """Cria consulta a partir do handoff da receção, ou reutiliza marcação já ligada ao check-in."""
        queue_entry = WaitingQueue.objects.filter(check_in=referral.check_in).first()
        resolved_doctor_id = doctor_id or getattr(referral, "assigned_doctor_id", None)

        existing_by_referral = (
            Appointment.objects.select_for_update()
            .filter(referral=referral, status__in=ACTIVE_APPOINTMENT_STATUSES)
            .first()
        )
        if existing_by_referral:
            return existing_by_referral

        existing_by_check_in = None
        if referral.check_in_id:
            existing_by_check_in = (
                Appointment.objects.select_for_update()
                .filter(
                    check_in_id=referral.check_in_id,
                    status__in=ACTIVE_APPOINTMENT_STATUSES,
                )
                .first()
            )

        if existing_by_check_in:
            update_fields = ["referral", "updated_at"]
            existing_by_check_in.referral = referral
            if resolved_doctor_id and existing_by_check_in.doctor_id != resolved_doctor_id:
                existing_by_check_in.doctor_id = resolved_doctor_id
                update_fields.append("doctor_id")
            if queue_entry and existing_by_check_in.queue_entry_id != queue_entry.pk:
                existing_by_check_in.queue_entry = queue_entry
                update_fields.append("queue_entry")
            if existing_by_check_in.status in {
                AppointmentStatus.AGENDADA,
                AppointmentStatus.CONFIRMADA,
            }:
                existing_by_check_in.status = AppointmentStatus.EM_ESPERA
                update_fields.append("status")
            existing_by_check_in.save(update_fields=update_fields)
            AppointmentService._log_consulta(
                AuditAction.CONSULTA_CRIADA,
                user,
                request,
                existing_by_check_in,
                (
                    f"Marcação {existing_by_check_in.appointment_number} ligada ao "
                    f"encaminhamento — {referral.patient.full_name}."
                ),
                metadata={
                    "patient_id": referral.patient_id,
                    "referral_id": referral.pk,
                    "check_in_id": referral.check_in_id,
                    "source": "reception_handoff_reuse",
                },
            )
            return existing_by_check_in

        now = timezone.now()
        priority = QueuePriority.NORMAL
        if referral.check_in_id:
            priority = referral.check_in.priority

        check_in = referral.check_in
        triage_complaint = ""
        if check_in is not None:
            triage_complaint = (check_in.symptoms or "").strip()
        referral_reason = (referral.reason or "").strip()
        chief_complaint = triage_complaint or referral_reason or "Encaminhamento para consulta médica."
        notes = referral_reason or triage_complaint

        appointment = Appointment.objects.create(
            patient=referral.patient,
            doctor_id=resolved_doctor_id,
            check_in=referral.check_in,
            referral=referral,
            queue_entry=queue_entry,
            receptionist=user if user.role == UserRole.RECECIONISTA else None,
            appointment_number=AppointmentNumberService.generate(),
            scheduled_at=now,
            consultation_date=now.date(),
            status=AppointmentStatus.EM_ESPERA,
            priority=priority,
            notes=notes,
            chief_complaint=chief_complaint,
            created_by=user,
        )
        AppointmentService._log_consulta(
            AuditAction.CONSULTA_CRIADA,
            user,
            request,
            appointment,
            f"Consulta criada a partir da receção — {referral.patient.full_name}.",
            metadata={
                "patient_id": referral.patient_id,
                "referral_id": referral.pk,
                "check_in_id": referral.check_in_id,
                "source": "reception_handoff",
            },
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def confirmar_chegada(appointment_id: int, user, request=None) -> Appointment:
        """Regista chegada do paciente marcado via check-in/fila da Receção (sem nova consulta).

        Reutiliza ``ReceptionService.check_in`` (mesmo fluxo de Atendimento rápido / Fila).
        Idempotente: repetir a acção não cria segundo check-in nem segunda consulta.
        """
        from apps.reception.services.reception_service import ReceptionService

        appointment = (
            Appointment.objects.select_for_update()
            .select_related("patient")
            .get(pk=appointment_id)
        )

        if appointment.status in {
            AppointmentStatus.CANCELADA,
            AppointmentStatus.CONCLUIDA,
            AppointmentStatus.FALTA,
            AppointmentStatus.EM_CONSULTA,
        }:
            raise ValueError("Não é possível confirmar chegada para esta marcação.")

        # Já ligado à fila da receção — só garantir estado EM_ESPERA.
        if appointment.check_in_id:
            update_fields: list[str] = []
            if not appointment.queue_entry_id:
                queue_entry = WaitingQueue.objects.filter(check_in_id=appointment.check_in_id).first()
                if queue_entry:
                    appointment.queue_entry = queue_entry
                    update_fields.append("queue_entry")
            if appointment.status in {AppointmentStatus.AGENDADA, AppointmentStatus.CONFIRMADA}:
                appointment.status = AppointmentStatus.EM_ESPERA
                update_fields.append("status")
            if update_fields:
                update_fields.append("updated_at")
                appointment.save(update_fields=update_fields)
            return appointment

        today = timezone.localdate()
        appt_date = appointment.consultation_date
        if appt_date is None and appointment.scheduled_at:
            appt_date = timezone.localtime(appointment.scheduled_at).date()
        if appt_date != today:
            raise ValueError("Só é possível confirmar chegada para marcações do dia.")

        if appointment.status not in {
            AppointmentStatus.AGENDADA,
            AppointmentStatus.CONFIRMADA,
            AppointmentStatus.EM_ESPERA,
        }:
            raise ValueError("Estado da marcação não permite confirmar chegada.")

        existing_entry = (
            WaitingQueue.objects.select_for_update()
            .filter(
                patient_id=appointment.patient_id,
                status__in=ReceptionService.ACTIVE_QUEUE_STATUSES,
            )
            .select_related("check_in")
            .first()
        )

        if existing_entry:
            other = (
                Appointment.objects.filter(
                    check_in=existing_entry.check_in,
                    status__in=ACTIVE_APPOINTMENT_STATUSES,
                )
                .exclude(pk=appointment.pk)
                .first()
            )
            if other:
                raise ValueError(
                    "O paciente já está em atendimento noutro registo. "
                    "Não é possível ligar esta marcação."
                )
            check_in = existing_entry.check_in
            queue_entry = existing_entry
        else:
            check_in = ReceptionService.check_in(
                appointment.patient_id,
                user,
                priority=appointment.priority or QueuePriority.NORMAL,
                visit_purpose=VisitPurpose.CONSULTA,
                symptoms=(appointment.chief_complaint or "").strip(),
                notes=(appointment.notes or "").strip(),
                request=request,
            )
            queue_entry = WaitingQueue.objects.get(check_in=check_in)

        appointment.check_in = check_in
        appointment.queue_entry = queue_entry
        appointment.status = AppointmentStatus.EM_ESPERA
        update_fields = ["check_in", "queue_entry", "status", "updated_at"]
        if user.role == UserRole.RECECIONISTA and appointment.receptionist_id is None:
            appointment.receptionist = user
            update_fields.append("receptionist")
        appointment.save(update_fields=update_fields)

        AppointmentService._log_consulta(
            AuditAction.CONSULTA_CONFIRMADA,
            user,
            request,
            appointment,
            f"Chegada confirmada — {appointment.patient.full_name} na fila da receção.",
            metadata={
                "patient_id": appointment.patient_id,
                "check_in_id": check_in.pk,
                "queue_entry_id": queue_entry.pk,
                "source": "confirm_arrival",
            },
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def confirmar_consulta(appointment_id: int, user, request=None) -> Appointment:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(pk=appointment_id)
        if appointment.status != AppointmentStatus.AGENDADA:
            raise ValueError("Apenas consultas agendadas podem ser confirmadas.")
        appointment.status = AppointmentStatus.CONFIRMADA
        appointment.save(update_fields=["status", "updated_at"])
        AppointmentService._log_consulta(
            AuditAction.CONSULTA_CONFIRMADA,
            user,
            request,
            appointment,
            f"Consulta confirmada — {appointment.patient.full_name}.",
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def reagendar_consulta(
        appointment_id: int,
        user,
        *,
        scheduled_at,
        doctor_id: int | None = None,
        duration_minutes: int | None = None,
        request=None,
    ) -> Appointment:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(pk=appointment_id)
        if appointment.status in {AppointmentStatus.CONCLUIDA, AppointmentStatus.CANCELADA, AppointmentStatus.FALTA}:
            raise ValueError("Não é possível reagendar uma consulta finalizada.")

        validate_scheduled_in_future(scheduled_at)
        target_doctor = doctor_id or appointment.doctor_id
        target_duration = duration_minutes or appointment.duration_minutes
        if target_doctor:
            validate_doctor_availability(
                doctor_id=target_doctor,
                scheduled_at=scheduled_at,
                duration_minutes=target_duration,
                exclude_appointment_id=appointment.pk,
            )

        old_when = appointment.scheduled_at
        appointment.scheduled_at = scheduled_at
        appointment.consultation_date = scheduled_at.date()
        if doctor_id is not None:
            appointment.doctor_id = doctor_id
        if duration_minutes is not None:
            appointment.duration_minutes = duration_minutes
        if appointment.status == AppointmentStatus.AGENDADA:
            appointment.status = AppointmentStatus.CONFIRMADA
        appointment.save(
            update_fields=[
                "scheduled_at",
                "consultation_date",
                "doctor_id",
                "duration_minutes",
                "status",
                "updated_at",
            ]
        )
        AppointmentService._log_consulta(
            AuditAction.CONSULTA_REAGENDADA,
            user,
            request,
            appointment,
            f"Consulta reagendada de {old_when:%d/%m/%Y %H:%M} para {scheduled_at:%d/%m/%Y %H:%M}.",
            metadata={"old_scheduled_at": old_when.isoformat()},
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def iniciar_consulta(appointment_id: int, doctor, request=None) -> Appointment:
        return AppointmentService.start(appointment_id, doctor, request=request)

    @staticmethod
    @transaction.atomic
    def start(appointment_id: int, doctor, request=None) -> Appointment:
        AppointmentService._ensure_doctor(doctor)
        appointment = Appointment.objects.select_for_update().select_related("patient").get(pk=appointment_id)

        if appointment.status not in {
            AppointmentStatus.AGENDADA,
            AppointmentStatus.CONFIRMADA,
            AppointmentStatus.EM_ESPERA,
        }:
            raise ValueError("Esta consulta não pode ser iniciada.")

        if appointment.doctor_id and appointment.doctor_id != doctor.pk:
            raise ValueError("Esta consulta está atribuída a outro médico.")

        appointment.doctor = doctor
        appointment.status = AppointmentStatus.EM_CONSULTA
        appointment.started_at = timezone.now()
        appointment.save(update_fields=["doctor", "status", "started_at", "updated_at"])

        AppointmentService._log_consulta(
            AuditAction.CONSULTA_INICIADA,
            doctor,
            request,
            appointment,
            f"Consulta iniciada — {appointment.patient.full_name}.",
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def update_clinical(
        appointment_id: int,
        user,
        *,
        chief_complaint: str | None = None,
        notes: str | None = None,
        diagnosis: str | None = None,
        clinical_notes: str | None = None,
        request=None,
    ) -> Appointment:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(pk=appointment_id)

        if appointment.status != AppointmentStatus.EM_CONSULTA:
            raise ValueError("A consulta deve estar em curso para actualizar dados clínicos.")

        update_fields = ["updated_at"]
        if chief_complaint is not None:
            appointment.chief_complaint = chief_complaint
            update_fields.append("chief_complaint")
        if notes is not None:
            appointment.notes = notes
            update_fields.append("notes")
        if diagnosis is not None:
            appointment.diagnosis = diagnosis
            update_fields.append("diagnosis")
        if clinical_notes is not None:
            appointment.clinical_notes = clinical_notes
            update_fields.append("clinical_notes")

        appointment.save(update_fields=update_fields)
        return appointment

    @staticmethod
    @transaction.atomic
    def concluir_consulta(
        appointment_id: int,
        user,
        *,
        diagnosis: str = "",
        clinical_notes: str = "",
        request=None,
    ) -> Appointment:
        return AppointmentService.complete(
            appointment_id,
            user,
            diagnosis=diagnosis,
            clinical_notes=clinical_notes,
            request=request,
        )

    @staticmethod
    @transaction.atomic
    def complete(
        appointment_id: int,
        user,
        *,
        diagnosis: str = "",
        clinical_notes: str = "",
        request=None,
    ) -> Appointment:
        AppointmentService._ensure_doctor(user)
        appointment = (
            Appointment.objects.select_for_update()
            .select_related("patient")
            .get(pk=appointment_id)
        )

        # Idempotente: segunda conclusão na mesma consulta devolve o estado actual.
        if appointment.status == AppointmentStatus.CONCLUIDA:
            return appointment

        if appointment.status != AppointmentStatus.EM_CONSULTA:
            raise ValueError("Apenas consultas em curso podem ser concluídas.")

        if appointment.doctor_id and appointment.doctor_id != user.pk and user.role == UserRole.MEDICO:
            raise ValueError("Apenas o médico responsável pode concluir a consulta.")

        now = timezone.now()
        if diagnosis:
            appointment.diagnosis = diagnosis
        if clinical_notes:
            appointment.clinical_notes = clinical_notes
        appointment.status = AppointmentStatus.CONCLUIDA
        appointment.completed_at = now
        if appointment.started_at:
            delta = now - appointment.started_at
            appointment.duration_minutes = max(1, int(delta.total_seconds() // 60))
        appointment.save(
            update_fields=[
                "diagnosis",
                "clinical_notes",
                "status",
                "completed_at",
                "duration_minutes",
                "updated_at",
            ]
        )

        if appointment.check_in_id:
            from apps.reception.models import ReceptionCheckIn

            check_in = ReceptionCheckIn.objects.select_for_update().get(pk=appointment.check_in_id)
            check_in.status = CheckInStatus.COMPLETED
            check_in.save(update_fields=["status", "updated_at"])
            WaitingQueue.objects.filter(check_in=check_in).update(
                status=QueueStatus.COMPLETED,
                updated_at=now,
            )

        PatientHistoryService.record(
            patient=appointment.patient,
            event_type=HistoryEventType.CONSULTA,
            title="Consulta médica concluída",
            description=appointment.diagnosis or "Consulta concluída sem diagnóstico registado.",
            user=user,
            source_module="appointments",
            source_id=appointment.pk,
            metadata={"appointment_id": appointment.pk},
        )

        AppointmentService._log_consulta(
            AuditAction.CONSULTA_CONCLUIDA,
            user,
            request,
            appointment,
            f"Consulta concluída — {appointment.patient.full_name}.",
            metadata={"duration_minutes": appointment.duration_minutes},
        )
        return appointment

    @staticmethod
    @transaction.atomic
    def cancelar_consulta(appointment_id: int, user, reason: str = "", request=None) -> Appointment:
        return AppointmentService.cancel(appointment_id, user, reason=reason, request=request)

    @staticmethod
    @transaction.atomic
    def cancel(appointment_id: int, user, reason: str = "", request=None) -> Appointment:
        appointment = Appointment.objects.select_for_update().select_related("patient").get(pk=appointment_id)

        if appointment.status in {AppointmentStatus.CONCLUIDA, AppointmentStatus.CANCELADA}:
            raise ValueError("Esta consulta já está finalizada.")

        appointment.status = AppointmentStatus.CANCELADA
        appointment.cancellation_reason = reason
        if reason:
            appointment.notes = f"{appointment.notes}\n\nCancelamento: {reason}".strip()
        appointment.save(update_fields=["status", "cancellation_reason", "notes", "updated_at"])

        AppointmentService._log_consulta(
            AuditAction.CONSULTA_CANCELADA,
            user,
            request,
            appointment,
            f"Consulta cancelada — {appointment.patient.full_name}.",
            metadata={"reason": reason},
        )
        return appointment

    @staticmethod
    def list_for_patient(patient_id: int):
        return (
            Appointment.objects.filter(patient_id=patient_id)
            .select_related("doctor", "patient", "receptionist")
            .order_by("-scheduled_at")
        )

    @staticmethod
    def get_calendar(*, start_date, end_date, doctor_id: int | None = None):
        qs = Appointment.objects.filter(
            consultation_date__gte=start_date,
            consultation_date__lte=end_date,
        ).select_related("patient", "doctor")
        if doctor_id:
            qs = qs.filter(doctor_id=doctor_id)
        return qs.order_by("scheduled_at")
