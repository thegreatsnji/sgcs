"""Verificação de dependências cross-module."""


class PatientDependencyService:
    @staticmethod
    def has_active_appointments(patient_id: int) -> bool:
        from apps.appointments.services.appointment_service import AppointmentService

        return AppointmentService.has_active_appointments(patient_id)

    @staticmethod
    def has_pending_invoices(patient_id: int) -> bool:
        from apps.billing.constants import FaturaEstado
        from apps.billing.models import Fatura

        return Fatura.objects.filter(
            paciente_id=patient_id,
            estado__in={FaturaEstado.PENDENTE, FaturaEstado.PARCIAL},
        ).exists()

    @staticmethod
    def get_blocking_dependencies(patient_id: int) -> list[str]:
        dependencies = []
        if PatientDependencyService.has_active_appointments(patient_id):
            dependencies.append("appointments")
        if PatientDependencyService.has_pending_invoices(patient_id):
            dependencies.append("billing")
        return dependencies
