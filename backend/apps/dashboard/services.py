"""Serviço do dashboard administrativo."""

from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone

from apps.audit_logs.models import AuditAction, AuditLog
from apps.patients.models import Patient
from apps.reception.constants import CheckInStatus, QueuePriority, QueueStatus
from apps.reception.models import ReceptionCheckIn, WaitingQueue
from apps.users.models import UserSession

User = get_user_model()


class DashboardService:
    @staticmethod
    def get_admin_summary() -> dict:
        from core.cache import CacheHelper, CacheTTL

        return CacheHelper.get_or_set(
            "dashboard",
            "admin",
            DashboardService._compute_admin_summary,
            ttl=CacheTTL.DASHBOARD,
        )

    @staticmethod
    def _compute_admin_summary() -> dict:
        now = timezone.now()
        week_ago = now - timedelta(days=7)

        users_qs = User.objects.all()
        total_users = users_qs.count()
        active_users = users_qs.filter(is_active=True).count()
        inactive_users = total_users - active_users
        new_users_week = users_qs.filter(date_joined__gte=week_ago).count()

        recent_logins = (
            AuditLog.objects.filter(action=AuditAction.LOGIN)
            .select_related("user")
            .order_by("-created_at")[:10]
        )

        recent_activity = AuditLog.objects.select_related("user").order_by("-created_at")[:15]

        users_by_role = list(
            users_qs.values("role").annotate(count=Count("id")).order_by("-count")
        )

        logins_by_day = list(
            AuditLog.objects.filter(
                action=AuditAction.LOGIN,
                created_at__gte=now - timedelta(days=7),
            )
            .annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )

        active_sessions = UserSession.objects.filter(is_active=True).count()

        patients_qs = Patient.objects.filter(is_deleted=False)
        total_patients = patients_qs.count()
        active_patients = patients_qs.filter(is_active=True).count()
        inactive_patients = patients_qs.filter(is_active=False).count()
        new_patients_week = patients_qs.filter(created_at__gte=week_ago).count()

        recent_patient_activity = (
            AuditLog.objects.filter(action__startswith="PATIENT_")
            .select_related("user")
            .order_by("-created_at")[:10]
        )

        return {
            "cards": {
                "total_users": total_users,
                "active_users": active_users,
                "inactive_users": inactive_users,
                "new_users_week": new_users_week,
                "active_sessions": active_sessions,
                "total_patients": total_patients,
                "active_patients": active_patients,
                "inactive_patients": inactive_patients,
                "new_patients_week": new_patients_week,
            },
            "users_by_role": users_by_role,
            "logins_by_day": [
                {"date": item["day"].strftime("%d/%m/%Y") if item["day"] else "", "count": item["count"]}
                for item in logins_by_day
            ],
            "recent_logins": [
                {
                    "user": log.user.get_full_name() if log.user else "—",
                    "email": log.user.email if log.user else "—",
                    "ip_address": log.ip_address,
                    "created_at": log.created_at.strftime("%d/%m/%Y %H:%M"),
                }
                for log in recent_logins
            ],
            "recent_activity": [
                {
                    "action": log.action,
                    "description": log.description,
                    "user": log.user.get_full_name() if log.user else "—",
                    "created_at": log.created_at.strftime("%d/%m/%Y %H:%M"),
                    "resource_type": log.resource_type,
                }
                for log in recent_activity
            ],
            "recent_patient_activity": [
                {
                    "action": log.action,
                    "description": log.description,
                    "user": log.user.get_full_name() if log.user else "—",
                    "created_at": log.created_at.strftime("%d/%m/%Y %H:%M"),
                    "resource_id": log.resource_id,
                }
                for log in recent_patient_activity
            ],
        }

    @staticmethod
    def get_clinical_summary() -> dict:
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        patients_qs = Patient.objects.filter(is_deleted=False)

        recent_patients = list(
            patients_qs.order_by("-created_at")[:5].values(
                "id",
                "full_name",
                "patient_number",
                "created_at",
            )
        )
        for item in recent_patients:
            if item["created_at"]:
                item["created_at"] = item["created_at"].strftime("%d/%m/%Y %H:%M")

        return {
            "cards": {
                "total_patients": patients_qs.count(),
                "active_patients": patients_qs.filter(is_active=True).count(),
                "inactive_patients": patients_qs.filter(is_active=False).count(),
                "new_patients_week": patients_qs.filter(created_at__gte=week_ago).count(),
            },
            "recent_patients": recent_patients,
            "recent_patient_activity": [
                {
                    "action": log.action,
                    "description": log.description,
                    "user": log.user.get_full_name() if log.user else "—",
                    "created_at": log.created_at.strftime("%d/%m/%Y %H:%M"),
                    "resource_id": log.resource_id,
                }
                for log in AuditLog.objects.filter(action__startswith="PATIENT_")
                .select_related("user")
                .order_by("-created_at")[:8]
            ],
        }

    @staticmethod
    def get_reception_summary() -> dict:
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        waiting_qs = WaitingQueue.objects.filter(
            status__in=[QueueStatus.WAITING, QueueStatus.CALLED]
        )
        waiting_count = waiting_qs.count()

        emergencies = WaitingQueue.objects.filter(
            status__in=[QueueStatus.WAITING, QueueStatus.CALLED, QueueStatus.IN_SERVICE],
            check_in__priority=QueuePriority.EMERGENCY,
        ).count()

        # Tempo médio: só utentes em espera activa, ignorar fila abandonada (>24h)
        stale_cutoff = now - timedelta(hours=24)
        waiting_for_avg = waiting_qs.filter(
            status=QueueStatus.WAITING,
            check_in__check_in_time__gte=stale_cutoff,
        )
        wait_minutes = []
        for entry in waiting_for_avg.select_related("check_in"):
            delta = now - entry.check_in.check_in_time
            wait_minutes.append(max(0, int(delta.total_seconds() // 60)))
        avg_wait = round(sum(wait_minutes) / len(wait_minutes), 1) if wait_minutes else 0

        completed_today = max(
            ReceptionCheckIn.objects.filter(
                status=CheckInStatus.COMPLETED,
                check_in_time__gte=today_start,
            ).count(),
            WaitingQueue.objects.filter(
                status=QueueStatus.COMPLETED,
                updated_at__gte=today_start,
            ).count(),
        )

        recent_queue = list(
            WaitingQueue.objects.filter(
                status__in=[QueueStatus.WAITING, QueueStatus.CALLED, QueueStatus.IN_SERVICE]
            )
            .select_related("patient", "check_in")
            .order_by("position")[:10]
            .values(
                "id",
                "position",
                "status",
                "estimated_wait_minutes",
                "patient__id",
                "patient__full_name",
                "patient__patient_number",
                "check_in__priority",
                "check_in__triage_color",
                "check_in__visit_purpose",
            )
        )

        return {
            "cards": {
                "patients_waiting": waiting_count,
                "average_wait_minutes": avg_wait,
                "attended_today": completed_today,
                "active_emergencies": emergencies,
            },
            "queue_preview": recent_queue,
            "recent_reception_activity": [
                {
                    "action": log.action,
                    "description": log.description,
                    "user": log.user.get_full_name() if log.user else "—",
                    "created_at": log.created_at.strftime("%d/%m/%Y %H:%M"),
                }
                for log in AuditLog.objects.filter(action__startswith="RECEPTION_")
                .select_related("user")
                .order_by("-created_at")[:10]
            ],
        }

    @staticmethod
    def get_consultation_summary() -> dict:
        return DashboardService.get_consultas_summary()

    @staticmethod
    def get_consultas_summary() -> dict:
        from apps.appointments.constants import AppointmentStatus
        from apps.appointments.models import Appointment
        from apps.authentication.models import UserRole
        from django.contrib.auth import get_user_model

        User = get_user_model()
        now = timezone.now()
        today = now.date()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        today_qs = Appointment.objects.filter(consultation_date=today)
        consultas_do_dia = today_qs.count()
        consultas_concluidas = today_qs.filter(status=AppointmentStatus.CONCLUIDA).count()
        consultas_em_espera = Appointment.objects.filter(
            status__in=[AppointmentStatus.CONFIRMADA, AppointmentStatus.EM_ESPERA]
        ).count()
        em_consulta = Appointment.objects.filter(status=AppointmentStatus.EM_CONSULTA).count()

        proxima = (
            Appointment.objects.filter(
                consultation_date=today,
                status__in=[
                    AppointmentStatus.AGENDADA,
                    AppointmentStatus.CONFIRMADA,
                    AppointmentStatus.EM_ESPERA,
                ],
                scheduled_at__gte=now,
            )
            .select_related("patient", "doctor")
            .order_by("scheduled_at")
            .first()
        )

        medicos_em_servico = (
            User.objects.filter(role=UserRole.MEDICO, is_active=True)
            .filter(appointments__status=AppointmentStatus.EM_CONSULTA)
            .distinct()
            .count()
        )

        from apps.appointments.models import PedidoImagiologia, PedidoLaboratorio

        pedidos_lab_hoje = PedidoLaboratorio.objects.filter(
            consulta__consultation_date=today,
        ).count()
        pedidos_img_hoje = PedidoImagiologia.objects.filter(
            consulta__consultation_date=today,
        ).count()

        queue_preview = list(
            Appointment.objects.filter(
                status__in=[
                    AppointmentStatus.CONFIRMADA,
                    AppointmentStatus.EM_ESPERA,
                    AppointmentStatus.EM_CONSULTA,
                ]
            )
            .select_related("patient", "doctor")
            .order_by("scheduled_at")[:10]
            .values(
                "id",
                "appointment_number",
                "status",
                "scheduled_at",
                "patient__full_name",
                "patient__patient_number",
                "doctor__first_name",
                "doctor__last_name",
            )
        )

        return {
            "indicadores": {
                "consultas_do_dia": consultas_do_dia,
                "consultas_concluidas": consultas_concluidas,
                "consultas_em_espera": consultas_em_espera,
                "consultas_em_curso": em_consulta,
                "medicos_em_servico": medicos_em_servico,
                "pedidos_laboratorio_emitidos": pedidos_lab_hoje,
                "pedidos_imagiologia_emitidos": pedidos_img_hoje,
            },
            "proxima_consulta": (
                {
                    "id": proxima.pk,
                    "appointment_number": proxima.appointment_number,
                    "patient": proxima.patient.full_name,
                    "doctor": proxima.doctor.get_full_name() if proxima.doctor else None,
                    "scheduled_at": proxima.scheduled_at.strftime("%d/%m/%Y %H:%M"),
                }
                if proxima
                else None
            ),
            "cards": {
                "waiting_for_doctor": consultas_em_espera,
                "in_progress": em_consulta,
                "completed_today": consultas_concluidas,
                "scheduled_today": consultas_do_dia,
                "lab_orders_today": pedidos_lab_hoje,
                "imaging_orders_today": pedidos_img_hoje,
            },
            "queue_preview": queue_preview,
            "recent_consultation_activity": [
                {
                    "action": log.action,
                    "description": log.description,
                    "user": log.user.get_full_name() if log.user else "—",
                    "created_at": log.created_at.strftime("%d/%m/%Y %H:%M"),
                }
                for log in AuditLog.objects.filter(
                    action__startswith="CONSULTA_"
                )
                .select_related("user")
                .order_by("-created_at")[:10]
            ],
        }

    @staticmethod
    def get_laboratory_summary() -> dict:
        from apps.laboratory.services.laboratory_service import LaboratoryService

        return LaboratoryService.get_dashboard_summary()

    @staticmethod
    def get_billing_summary() -> dict:
        from apps.billing.services.billing_service import BillingService

        return BillingService.get_dashboard_summary()

    @staticmethod
    def get_finance_summary() -> dict:
        from apps.finance.services.finance_service import FinanceService

        return FinanceService.get_dashboard_summary()

    @staticmethod
    def get_executive_summary(request=None) -> dict:
        from apps.reports.services.dashboard_service import ReportsDashboardService

        return ReportsDashboardService.get_executive_summary(request=request)

    @staticmethod
    def get_system_summary() -> dict:
        from apps.settings.services.settings_service import SettingsService

        return SettingsService.get_system_dashboard()
