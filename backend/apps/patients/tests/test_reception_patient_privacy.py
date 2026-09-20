"""Sprint 23.3 — Privacidade Pacientes (RECECIONISTA): admin OK, clínico bloqueado."""

from datetime import date

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status

from apps.appointments.services.appointment_service import AppointmentService
from apps.authentication.models import UserRole
from apps.files.models import StoredFile
from apps.patients.constants import (
    AllergySeverity,
    ChronicDiseaseStatus,
    HistoryEventType,
    ObservationType,
    PatientDocumentType,
)
from apps.patients.models import (
    PatientAllergy,
    PatientChronicDisease,
    PatientDocument,
    PatientObservation,
)
from apps.patients.privacy import REDACTED_HISTORY_DESCRIPTION
from apps.patients.services.history_service import PatientHistoryService
from apps.patients.services.patient_service import PatientService

User = get_user_model()


@pytest.fixture
def doctor_user(db):
    return User.objects.create_user(
        email="medico.priv@test.gw",
        password="Medico@123",
        first_name="Paulo",
        last_name="Médico",
        role=UserRole.MEDICO,
    )


@pytest.fixture
def privacy_patient(db, receptionist_user):
    patient = PatientService.create(
        {
            "first_name": "Nijeoma",
            "last_name": "Joaozinho",
            "birth_date": date(1990, 3, 15),
            "gender": "F",
            "phone": "+245955100200",
            "document_number": "PRIV-DOC-001",
            "document_type": "BI",
            "address_street": "Bairro Teste",
            "blood_type": "O+",
        },
        user=receptionist_user,
        emergency_contacts=[
            {
                "name": "Contacto Priv",
                "phone": "+245955300400",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )
    patient.metadata = {
        "source": "MIGRACAO_EXCEL_SAUVIDA",
        "migration_id": "MIG-PRIV-001",
        "import_batch": "BATCH-PRIV-2026",
        "dados_verificados": False,
        "verification_state": "PENDENTE",
        "created_via": "historical_import",
        "record_class": "patient",
    }
    patient.save(update_fields=["metadata"])
    return patient


def _seed_clinical(patient, doctor_user):
    allergy = PatientAllergy.objects.create(
        patient=patient,
        allergen="Penicilina",
        severity=AllergySeverity.GRAVE,
        reaction="Urticária",
        notes="Nota clínica alergia",
        recorded_by=doctor_user,
    )
    disease = PatientChronicDisease.objects.create(
        patient=patient,
        disease_name="Hipertensão",
        status=ChronicDiseaseStatus.ATIVA,
        notes="Nota crónica",
        recorded_by=doctor_user,
    )
    obs_clin = PatientObservation.objects.create(
        patient=patient,
        observation_type=ObservationType.CLINICA,
        content="Observação médica confidencial",
        created_by=doctor_user,
    )
    PatientObservation.objects.create(
        patient=patient,
        observation_type=ObservationType.ADMINISTRATIVA,
        content="Contacto preferencial: manhã",
        created_by=doctor_user,
    )
    PatientHistoryService.record(
        patient=patient,
        event_type=HistoryEventType.DIAGNOSTICO,
        title="Diagnóstico migrado",
        description="Malária confirmada em 2019",
        user=doctor_user,
        metadata={"icd": "B54"},
    )
    clinical_doc = PatientDocument.objects.create(
        patient=patient,
        stored_file=StoredFile.objects.create(
            name="exame.pdf",
            file=SimpleUploadedFile("exame.pdf", b"%PDF-1.4 fake", content_type="application/pdf"),
            mime_type="application/pdf",
            size=12,
            uploaded_by=doctor_user,
        ),
        document_type=PatientDocumentType.EXAME_EXTERNO,
        title="Exame externo sensível",
        uploaded_by=doctor_user,
    )
    admin_doc = PatientDocument.objects.create(
        patient=patient,
        stored_file=StoredFile.objects.create(
            name="bi.pdf",
            file=SimpleUploadedFile("bi.pdf", b"%PDF-1.4 bi", content_type="application/pdf"),
            mime_type="application/pdf",
            size=10,
            uploaded_by=doctor_user,
        ),
        document_type=PatientDocumentType.BI,
        title="Cópia BI",
        uploaded_by=doctor_user,
    )
    return {
        "allergy": allergy,
        "disease": disease,
        "obs_clin": obs_clin,
        "clinical_doc": clinical_doc,
        "admin_doc": admin_doc,
    }


@pytest.mark.django_db
class TestReceptionAdministrativeCapabilities:
    def test_search_and_retrieve_admin(self, api_client, receptionist_user, privacy_patient):
        api_client.force_authenticate(user=receptionist_user)
        listed = api_client.get("/api/v1/patients/", {"search": "Nijeoma"})
        assert listed.status_code == status.HTTP_200_OK
        assert listed.data["data"]["count"] >= 1

        detail = api_client.get(f"/api/v1/patients/{privacy_patient.pk}/")
        assert detail.status_code == status.HTTP_200_OK
        data = detail.data["data"]
        assert data["phone"] == "+245955100200"
        assert data["address_street"] == "Bairro Teste"
        assert "blood_type" not in data
        assert data["chronic_diseases_count"] == 0

    def test_update_phone_and_address(self, api_client, receptionist_user, privacy_patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/patients/{privacy_patient.pk}/",
            {
                "phone": "+245955999001",
                "address_street": "Rua Nova 12",
                "birth_date": "15/03/1990",
                "gender": "F",
            },
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        privacy_patient.refresh_from_db()
        assert privacy_patient.phone == "+245955999001"
        assert privacy_patient.address_street == "Rua Nova 12"

    def test_confirm_imported_data(self, api_client, receptionist_user, privacy_patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/confirm-imported-data/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["dados_verificados"] is True
        privacy_patient.refresh_from_db()
        assert privacy_patient.metadata["dados_verificados"] is True


@pytest.mark.django_db
class TestReceptionClinicalWriteBlocked:
    def test_cannot_create_allergy(self, api_client, receptionist_user, privacy_patient):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/allergies/",
            {"allergen": "Aspirina", "severity": "LEVE"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_patch_allergy(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        seeded = _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/patients/{privacy_patient.pk}/allergies/{seeded['allergy'].pk}/",
            {"allergen": "Alterado"},
            format="json",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_edit_chronic_disease(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        seeded = _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        create = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/chronic-diseases/",
            {"disease_name": "Diabetes", "status": "ATIVA"},
            format="json",
        )
        assert create.status_code == status.HTTP_403_FORBIDDEN
        patch = api_client.patch(
            f"/api/v1/patients/{privacy_patient.pk}/chronic-diseases/{seeded['disease'].pk}/",
            {"disease_name": "Alterada"},
            format="json",
        )
        assert patch.status_code == status.HTTP_403_FORBIDDEN

    def test_cannot_edit_clinical_observation(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        seeded = _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        create = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/observations/",
            {"observation_type": "CLINICA", "content": "Tentativa"},
            format="json",
        )
        assert create.status_code == status.HTTP_403_FORBIDDEN
        patch = api_client.patch(
            f"/api/v1/patients/{privacy_patient.pk}/observations/{seeded['obs_clin'].pk}/",
            {"content": "Hack"},
            format="json",
        )
        assert patch.status_code == status.HTTP_403_FORBIDDEN

    def test_blood_type_not_updated_by_reception(
        self, api_client, receptionist_user, privacy_patient
    ):
        assert privacy_patient.blood_type == "O+"
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.patch(
            f"/api/v1/patients/{privacy_patient.pk}/",
            {"blood_type": "A+", "phone": "+245955100200"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        privacy_patient.refresh_from_db()
        assert privacy_patient.blood_type == "O+"


@pytest.mark.django_db
class TestReceptionClinicalReadScoped:
    def test_appointment_hides_diagnosis_and_notes(
        self, api_client, receptionist_user, privacy_patient
    ):
        appointment = AppointmentService.criar_consulta(
            patient_id=privacy_patient.pk, user=receptionist_user
        )
        appointment.diagnosis = "Malária grave"
        appointment.clinical_notes = "Plano terapêutico confidencial"
        appointment.notes = "Nota interna clínica"
        appointment.save(update_fields=["diagnosis", "clinical_notes", "notes"])

        api_client.force_authenticate(user=receptionist_user)
        detail = api_client.get(f"/api/v1/appointments/{appointment.pk}/")
        assert detail.status_code == status.HTTP_200_OK
        data = detail.data["data"]
        assert "diagnosis" not in data
        assert "clinical_notes" not in data
        assert "notes" not in data
        assert data["status"]

        nested = api_client.get(f"/api/v1/patients/{privacy_patient.pk}/appointments/")
        assert nested.status_code == status.HTTP_200_OK
        row = nested.data["data"]["results"][0]
        assert "diagnosis" not in row
        assert "clinical_notes" not in row

        clinical = api_client.get(f"/api/v1/appointments/{appointment.pk}/clinical/")
        assert clinical.status_code == status.HTTP_403_FORBIDDEN

    def test_chronic_diseases_empty_for_reception(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(
            f"/api/v1/patients/{privacy_patient.pk}/chronic-diseases/"
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["count"] == 0

    def test_clinical_observations_hidden(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{privacy_patient.pk}/observations/")
        assert response.status_code == status.HTTP_200_OK
        results = response.data["data"]["results"]
        assert all(r["observation_type"] == ObservationType.ADMINISTRATIVA for r in results)
        assert any("manhã" in r["content"] for r in results)
        assert not any("confidencial" in r["content"] for r in results)

    def test_history_clinical_redacted(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{privacy_patient.pk}/history/")
        assert response.status_code == status.HTTP_200_OK
        clinical = [
            r
            for r in response.data["data"]["results"]
            if r["event_type"] == HistoryEventType.DIAGNOSTICO
        ]
        assert clinical
        assert clinical[0]["description"] == REDACTED_HISTORY_DESCRIPTION
        assert clinical[0]["metadata"] == {}

    def test_clinical_document_hidden(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        seeded = _seed_clinical(privacy_patient, doctor_user)
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get(f"/api/v1/patients/{privacy_patient.pk}/documents/")
        assert response.status_code == status.HTTP_200_OK
        ids = {r["id"] for r in response.data["data"]["results"]}
        assert seeded["admin_doc"].pk in ids
        assert seeded["clinical_doc"].pk not in ids

    def test_lab_results_forbidden(self, api_client, receptionist_user):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.get("/api/v1/laboratory/results/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patient_history_not_writable(
        self, api_client, receptionist_user, privacy_patient
    ):
        api_client.force_authenticate(user=receptionist_user)
        response = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/history/",
            {"event_type": "DIAGNOSTICO", "title": "Hack"},
            format="json",
        )
        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
class TestProvenancePreserved:
    def test_phone_update_and_confirm_keep_migration_keys(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        history = PatientHistoryService.record(
            patient=privacy_patient,
            event_type=HistoryEventType.DIAGNOSTICO,
            title="Histórico migrado",
            description="Conteúdo clínico antigo",
            user=doctor_user,
            metadata={"source_sheet": "Sheet1", "source_row": 12},
        )
        history_desc = history.description
        history_meta = dict(history.metadata)

        api_client.force_authenticate(user=receptionist_user)
        patch = api_client.patch(
            f"/api/v1/patients/{privacy_patient.pk}/",
            {"phone": "+245955777666"},
            format="json",
        )
        assert patch.status_code == status.HTTP_200_OK
        privacy_patient.refresh_from_db()
        assert privacy_patient.metadata["migration_id"] == "MIG-PRIV-001"
        assert privacy_patient.metadata["import_batch"] == "BATCH-PRIV-2026"
        assert privacy_patient.metadata.get("dados_verificados") is False

        confirm = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/confirm-imported-data/"
        )
        assert confirm.status_code == status.HTTP_200_OK
        privacy_patient.refresh_from_db()
        assert privacy_patient.metadata["dados_verificados"] is True
        assert privacy_patient.metadata["migration_id"] == "MIG-PRIV-001"
        assert privacy_patient.metadata["import_batch"] == "BATCH-PRIV-2026"
        assert privacy_patient.patient_number.startswith("PAC-")

        history.refresh_from_db()
        assert history.description == history_desc
        assert history.metadata == history_meta


@pytest.mark.django_db
class TestDoctorClinicalStillWorks:
    def test_doctor_sees_diagnosis_and_can_write_allergy(
        self, api_client, receptionist_user, doctor_user, privacy_patient
    ):
        appointment = AppointmentService.criar_consulta(
            patient_id=privacy_patient.pk, user=receptionist_user
        )
        appointment.diagnosis = "Gripe"
        appointment.clinical_notes = "Repouso"
        appointment.save(update_fields=["diagnosis", "clinical_notes"])

        api_client.force_authenticate(user=doctor_user)
        detail = api_client.get(f"/api/v1/appointments/{appointment.pk}/")
        assert detail.status_code == status.HTTP_200_OK
        assert detail.data["data"]["diagnosis"] == "Gripe"
        assert detail.data["data"]["clinical_notes"] == "Repouso"

        allergy = api_client.post(
            f"/api/v1/patients/{privacy_patient.pk}/allergies/",
            {"allergen": "Ibuprofeno", "severity": "MODERADA"},
            format="json",
        )
        assert allergy.status_code == status.HTTP_201_CREATED
        assert PatientAllergy.objects.filter(
            patient=privacy_patient, allergen="Ibuprofeno"
        ).exists()

        diseases = api_client.get(
            f"/api/v1/patients/{privacy_patient.pk}/chronic-diseases/"
        )
        assert diseases.status_code == status.HTTP_200_OK
