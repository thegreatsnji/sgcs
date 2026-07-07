"""Serviço principal de gestão de pacientes."""

from django.db import transaction

from apps.audit_logs.models import AuditAction
from apps.audit_logs.services import AuditService
from apps.patients.models import Patient, PatientEmergencyContact
from apps.patients.services.dependency_service import PatientDependencyService
from apps.patients.services.duplicate_service import DuplicateService
from apps.patients.services.history_service import PatientHistoryService
from apps.patients.services.number_service import PatientNumberService
from core.events import EventNames, event_bus


class PatientService:
    @staticmethod
    def get_active_queryset():
        return Patient.objects.filter(is_deleted=False)

    @staticmethod
    @transaction.atomic
    def create(validated_data: dict, user, request=None, emergency_contacts: list | None = None) -> Patient:
        document_number = validated_data.get("document_number", "")
        existing = DuplicateService.document_exists(document_number)
        if existing:
            raise ValueError(
                "Já existe um paciente com este documento de identificação."
            )

        emergency_contacts = emergency_contacts or []
        patient = Patient.objects.create(
            patient_number=PatientNumberService.generate_next(),
            created_by=user,
            updated_by=user,
            **validated_data,
        )

        for contact_data in emergency_contacts:
            PatientEmergencyContact.objects.create(
                patient=patient,
                created_by=user,
                **contact_data,
            )

        if patient.age < 18 and not patient.emergency_contacts.filter(is_active=True).exists():
            raise ValueError(
                "Paciente menor de idade requer pelo menos um contacto de emergência."
            )

        PatientHistoryService.record_registration(patient, user=user)
        AuditService.log(
            action=AuditAction.PATIENT_CREATE,
            user=user,
            request=request,
            description=f"Paciente {patient.full_name} registado (nº {patient.patient_number}).",
            resource_type="patient",
            resource_id=str(patient.pk),
            metadata={"patient_number": patient.patient_number},
        )
        event_bus.publish(
            EventNames.PATIENT_CREATED,
            {"patient_id": patient.pk, "patient_number": patient.patient_number},
        )
        return patient

    @staticmethod
    @transaction.atomic
    def update(patient: Patient, validated_data: dict, user, request=None) -> Patient:
        document_number = validated_data.get("document_number", patient.document_number)
        existing = DuplicateService.document_exists(document_number, exclude_id=patient.pk)
        if existing:
            raise ValueError(
                "Já existe um paciente com este documento de identificação."
            )

        changed_fields = []
        for field, value in validated_data.items():
            if getattr(patient, field) != value:
                changed_fields.append(field)
                setattr(patient, field, value)

        patient.updated_by = user
        patient.save()

        AuditService.log(
            action=AuditAction.PATIENT_UPDATE,
            user=user,
            request=request,
            description=f"Paciente {patient.full_name} atualizado.",
            resource_type="patient",
            resource_id=str(patient.pk),
            metadata={"changed_fields": changed_fields},
        )
        event_bus.publish(
            EventNames.PATIENT_UPDATED,
            {"patient_id": patient.pk, "changed_fields": changed_fields},
        )
        return patient

    @staticmethod
    @transaction.atomic
    def soft_delete(patient: Patient, user, request=None) -> Patient:
        dependencies = PatientDependencyService.get_blocking_dependencies(patient.pk)
        if dependencies:
            raise ValueError(
                f"Não é possível eliminar o paciente: dependências ativas ({', '.join(dependencies)})."
            )

        patient.soft_delete()
        patient.updated_by = user
        patient.save(update_fields=["updated_by", "updated_at"])

        AuditService.log(
            action=AuditAction.PATIENT_DELETE,
            user=user,
            request=request,
            description=f"Paciente {patient.full_name} eliminado (soft delete).",
            resource_type="patient",
            resource_id=str(patient.pk),
        )
        event_bus.publish(
            EventNames.PATIENT_DEACTIVATED,
            {"patient_id": patient.pk},
        )
        return patient

    @staticmethod
    def activate(patient: Patient, user, request=None) -> Patient:
        patient.restore()
        patient.updated_by = user
        patient.save(update_fields=["updated_by", "updated_at"])

        AuditService.log(
            action=AuditAction.PATIENT_ACTIVATE,
            user=user,
            request=request,
            description=f"Paciente {patient.full_name} ativado.",
            resource_type="patient",
            resource_id=str(patient.pk),
        )
        return patient

    @staticmethod
    def deactivate(patient: Patient, user, request=None) -> Patient:
        patient.is_active = False
        patient.updated_by = user
        patient.save(update_fields=["is_active", "updated_by", "updated_at"])

        AuditService.log(
            action=AuditAction.PATIENT_DEACTIVATE,
            user=user,
            request=request,
            description=f"Paciente {patient.full_name} desativado.",
            resource_type="patient",
            resource_id=str(patient.pk),
        )
        event_bus.publish(
            EventNames.PATIENT_DEACTIVATED,
            {"patient_id": patient.pk},
        )
        return patient

    @staticmethod
    def clear_primary_emergency_contacts(patient: Patient, exclude_id: int | None = None):
        queryset = patient.emergency_contacts.filter(is_primary=True, is_active=True)
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        queryset.update(is_primary=False)

    @staticmethod
    def clear_primary_insurances(patient: Patient, exclude_id: int | None = None):
        queryset = patient.insurances.filter(is_primary=True, is_active=True)
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        queryset.update(is_primary=False)

    @staticmethod
    def clear_primary_photos(patient: Patient, exclude_id: int | None = None):
        queryset = patient.photos.filter(is_primary=True, is_active=True)
        if exclude_id:
            queryset = queryset.exclude(pk=exclude_id)
        queryset.update(is_primary=False)
