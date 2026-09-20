"""Sprint 26 — Hardening perfil ENFERMEIRO (RBAC + stock)."""

from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model

from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.appointments.services.clinical_record_service import ClinicalRecordService
from apps.authentication.models import UserRole
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia
from apps.pharmacy.services.stock_service import StockUrgenciaError, StockUrgenciaService
from apps.pharmacy.status import estado_item
from apps.reception.services.reception_service import ReceptionService

User = get_user_model()


@pytest.fixture
def nurse_user(db, seed_rbac):
    return User.objects.create_user(
        email="enf.s26@test.gw",
        password="TestPass123!",
        first_name="Enf",
        last_name="Sprint26",
        role=UserRole.ENFERMEIRO,
        is_active=True,
    )


@pytest.fixture
def receptionist_user(db, seed_rbac):
    return User.objects.create_user(
        email="rec.s26@test.gw",
        password="TestPass123!",
        first_name="Rec",
        last_name="Sprint26",
        role=UserRole.RECECIONISTA,
        is_active=True,
    )


@pytest.fixture
def doctor_user(db, seed_rbac):
    return User.objects.create_user(
        email="med.s26@test.gw",
        password="TestPass123!",
        first_name="Med",
        last_name="Sprint26",
        role=UserRole.MEDICO,
        is_active=True,
    )


@pytest.fixture
def patient(db, receptionist_user):
    from apps.patients.services.patient_service import PatientService

    return PatientService.create(
        {
            "first_name": "Ana",
            "last_name": "Teste",
            "birth_date": date(1990, 1, 1),
            "gender": "F",
            "phone": "+245955111222",
            "document_number": "S26-001",
            "document_type": "BI",
        },
        user=receptionist_user,
        emergency_contacts=[
            {
                "name": "Contacto",
                "phone": "+245955333444",
                "relationship": "CONJUGE",
                "is_primary": True,
            }
        ],
    )


@pytest.mark.django_db
class TestNurseRbacIsolation:
    def test_nurse_permissions_seed(self, nurse_user, seed_rbac):
        from apps.users.services.rbac_service import RBACService

        perms = RBACService.get_user_permissions(nurse_user)
        assert "reception.create" in perms
        assert "reception.view" not in perms
        assert "reception.edit" not in perms
        assert "appointments.edit" not in perms
        assert "appointments.view" in perms
        assert "billing.edit" not in perms
        assert "stock.adjust" in perms

    def test_nurse_cannot_mark_lab_billed(
        self, api_client, nurse_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        check_in = ReceptionService.check_in(patient.pk, receptionist_user, temperature=36.5, weight=70)
        queue = check_in.queue_entry
        ReceptionService.assign_to_doctor(
            queue_id=queue.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        apt = Appointment.objects.filter(patient=patient).latest("pk")
        AppointmentService.iniciar_consulta(apt.pk, doctor_user)
        pedido = ClinicalRecordService.adicionar_pedido_laboratorio(
            apt.pk, doctor_user, {"tipo_exame": "Hemograma"}
        )
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(f"/api/v1/reception/mark-lab-order-billed/{pedido.pk}/")
        assert r.status_code == 403

    def test_reception_can_mark_lab_billed(
        self, api_client, receptionist_user, doctor_user, patient, seed_rbac
    ):
        check_in = ReceptionService.check_in(patient.pk, receptionist_user, temperature=36.5, weight=70)
        ReceptionService.assign_to_doctor(
            queue_id=check_in.queue_entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        apt = Appointment.objects.filter(patient=patient).latest("pk")
        AppointmentService.iniciar_consulta(apt.pk, doctor_user)
        pedido = ClinicalRecordService.adicionar_pedido_laboratorio(
            apt.pk, doctor_user, {"tipo_exame": "Glicemia"}
        )
        api_client.force_authenticate(user=receptionist_user)
        r = api_client.post(f"/api/v1/reception/mark-lab-order-billed/{pedido.pk}/")
        assert r.status_code == 200

    def test_nurse_cannot_assign_doctor(
        self, api_client, nurse_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            "/api/v1/reception/assign-to-doctor/",
            {"queue_id": check_in.queue_entry.pk, "doctor_id": doctor_user.pk},
            format="json",
        )
        assert r.status_code == 403

    def test_nurse_cannot_patch_appointment(
        self, api_client, nurse_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        check_in = ReceptionService.check_in(patient.pk, receptionist_user)
        ReceptionService.assign_to_doctor(
            queue_id=check_in.queue_entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        apt = Appointment.objects.filter(patient=patient).latest("pk")
        api_client.force_authenticate(user=nurse_user)
        r = api_client.patch(
            f"/api/v1/appointments/{apt.pk}/",
            {"notes": "Tentativa indevida"},
            format="json",
        )
        assert r.status_code == 403

    def test_nurse_can_check_in_triage(self, api_client, nurse_user, patient, seed_rbac):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            "/api/v1/reception/check-in/",
            {
                "patient_id": patient.pk,
                "triage_color": "YELLOW",
                "age_at_check_in": 36,
                "temperature": "37.2",
                "weight": "68",
                "blood_pressure": "120/80",
                "symptoms": "Dor de cabeça",
                "visit_purpose": "CONSULTA",
            },
            format="json",
        )
        assert r.status_code == 201
        assert r.data["data"]["check_in"]["triage_color"] == "YELLOW"

    def test_nurse_cannot_list_queue(self, api_client, nurse_user, seed_rbac):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.get("/api/v1/reception/queue/")
        assert r.status_code == 403

    def test_nurse_cannot_list_pending_lab_orders(self, api_client, nurse_user, seed_rbac):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.get("/api/v1/reception/pending-clinical-lab-orders/")
        assert r.status_code == 403

    def test_nurse_cannot_list_invoices(self, api_client, nurse_user, seed_rbac):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.get("/api/v1/billing/invoices/")
        assert r.status_code == 403

    def test_nurse_cannot_patch_clinical(
        self, api_client, nurse_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        check_in = ReceptionService.check_in(patient.pk, receptionist_user, temperature=36.5, weight=70)
        ReceptionService.assign_to_doctor(
            queue_id=check_in.queue_entry.pk, user=receptionist_user, doctor_id=doctor_user.pk
        )
        apt = Appointment.objects.filter(patient=patient).latest("pk")
        AppointmentService.iniciar_consulta(apt.pk, doctor_user)
        api_client.force_authenticate(user=nurse_user)
        r = api_client.patch(
            f"/api/v1/appointments/{apt.pk}/clinical/",
            {"subjetivo": "Tentativa indevida", "plano": "Indevido"},
            format="json",
        )
        assert r.status_code == 403


@pytest.mark.django_db
class TestStockSprint26:
    def test_expirado_nao_e_sem_stock(self):
        assert (
            estado_item(
                quantidade=5,
                stock_minimo=2,
                validade=date.today() - timedelta(days=1),
            )
            == "EXPIRADO"
        )

    def test_expirado_com_quantidade_zero_ainda_expirado(self):
        assert (
            estado_item(
                quantidade=0,
                stock_minimo=2,
                validade=date.today() - timedelta(days=1),
            )
            == "EXPIRADO"
        )

    def test_saida_expirado_bloqueada(self, nurse_user):
        item = MedicamentoUrgencia.objects.create(
            codigo="EXP-1",
            nome="Item expirado",
            quantidade_stock=5,
            stock_minimo=1,
            validade=date.today() - timedelta(days=2),
        )
        with pytest.raises(StockUrgenciaError, match="expirado"):
            StockUrgenciaService.registar_movimento(
                item, tipo="SAIDA", quantidade=1, operador=nurse_user
            )

    def test_perda_expirado_permitida(self, nurse_user):
        item = MedicamentoUrgencia.objects.create(
            codigo="EXP-2",
            nome="Item expirado 2",
            quantidade_stock=5,
            stock_minimo=1,
            validade=date.today() - timedelta(days=2),
        )
        StockUrgenciaService.registar_movimento(
            item, tipo="PERDA_EXPIRACAO", quantidade=2, motivo="EXPIRADO", operador=nurse_user
        )
        item.refresh_from_db()
        assert item.quantidade_stock == 3

    def test_ajuste_requer_motivo(self, nurse_user):
        item = MedicamentoUrgencia.objects.create(
            codigo="AJ-1", nome="Ajuste", quantidade_stock=10, stock_minimo=1
        )
        with pytest.raises(StockUrgenciaError, match="motivo"):
            StockUrgenciaService.registar_movimento(
                item, tipo="AJUSTE", quantidade=8, motivo="", operador=nurse_user
            )

    def test_ajuste_ok(self, nurse_user):
        item = MedicamentoUrgencia.objects.create(
            codigo="AJ-2", nome="Ajuste 2", quantidade_stock=20, stock_minimo=1
        )
        StockUrgenciaService.registar_movimento(
            item, tipo="AJUSTE", quantidade=18, motivo="Contagem física", operador=nurse_user
        )
        item.refresh_from_db()
        assert item.quantidade_stock == 18
        mov = MovimentoStockUrgencia.objects.filter(medicamento=item, tipo="AJUSTE").latest("pk")
        assert mov.quantidade_antes == 20
        assert mov.quantidade_depois == 18

    def test_stock_inicial_idempotente(self, nurse_user):
        item = StockUrgenciaService.criar_item(
            nome="Oxitocina S26",
            categoria="MEDICAMENTO",
            unidade="ampola",
            quantidade_inicial=0,
            operador=nurse_user,
        )
        assert item.stock_inicial_por_confirmar is True
        StockUrgenciaService.definir_stock_inicial(item, quantidade=10, operador=nurse_user)
        item.refresh_from_db()
        assert item.quantidade_stock == 10
        assert item.stock_inicial_por_confirmar is False
        with pytest.raises(StockUrgenciaError, match="já foi definido"):
            StockUrgenciaService.definir_stock_inicial(item, quantidade=5, operador=nurse_user)

    def test_duplicado_exacto(self, nurse_user):
        StockUrgenciaService.criar_item(
            nome="Ceftriaxona 1g",
            categoria="MEDICAMENTO",
            unidade="frasco",
            forma_apresentacao="1g",
            quantidade_inicial=1,
            operador=nurse_user,
        )
        with pytest.raises(StockUrgenciaError, match="semelhante"):
            StockUrgenciaService.criar_item(
                nome="ceftriaxona 1g",
                categoria="MEDICAMENTO",
                unidade="frasco",
                forma_apresentacao="1g",
                quantidade_inicial=1,
                operador=nurse_user,
            )

    def test_doctor_ve_vitais_triagem_nurse(
        self, api_client, nurse_user, receptionist_user, doctor_user, patient, seed_rbac
    ):
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            "/api/v1/reception/check-in/",
            {
                "patient_id": patient.pk,
                "triage_color": "GREEN",
                "age_at_check_in": 36,
                "temperature": "36.8",
                "weight": "72",
                "blood_pressure": "118/76",
                "symptoms": "Controlo",
                "visit_purpose": "CONSULTA",
            },
            format="json",
        )
        assert r.status_code == 201
        queue_id = r.data["data"]["queue_entry"]["id"]
        ReceptionService.assign_to_doctor(
            queue_id=queue_id, user=receptionist_user, doctor_id=doctor_user.pk
        )
        apt = Appointment.objects.filter(patient=patient).latest("pk")
        AppointmentService.iniciar_consulta(apt.pk, doctor_user)
        api_client.force_authenticate(user=doctor_user)
        prontuario = api_client.get(f"/api/v1/appointments/{apt.pk}/clinical/")
        assert prontuario.status_code == 200
        vitais = prontuario.data["data"]["sinais_vitais_triagem"]
        assert vitais["temperatura"] == 36.8
        assert vitais["peso"] == 72.0
        assert vitais["origem"] == "TRIAGEM"

    def test_cenario_e2e_b_movimentos(self, nurse_user):
        item = StockUrgenciaService.criar_item(
            nome="Ceftriaxona E2E",
            categoria="MEDICAMENTO",
            unidade="frasco",
            quantidade_inicial=10,
            operador=nurse_user,
        )
        StockUrgenciaService.registar_movimento(
            item, tipo="ENTRADA", quantidade=5, operador=nurse_user
        )
        item.refresh_from_db()
        assert item.quantidade_stock == 15
        StockUrgenciaService.registar_movimento(
            item, tipo="SAIDA", quantidade=2, operador=nurse_user
        )
        item.refresh_from_db()
        assert item.quantidade_stock == 13
        StockUrgenciaService.registar_movimento(
            item, tipo="AJUSTE", quantidade=12, motivo="Contagem física", operador=nurse_user
        )
        item.refresh_from_db()
        assert item.quantidade_stock == 13 - 1
        StockUrgenciaService.registar_movimento(
            item, tipo="PERDA_EXPIRACAO", quantidade=2, motivo="PERDIDO", operador=nurse_user
        )
        item.refresh_from_db()
        assert item.quantidade_stock == 10
        tipos = list(
            MovimentoStockUrgencia.objects.filter(medicamento=item)
            .order_by("pk")
            .values_list("tipo", flat=True)
        )
        assert tipos == ["ENTRADA", "ENTRADA", "SAIDA", "AJUSTE", "PERDA_EXPIRACAO"]

    def test_api_saida_expirado_bloqueada(self, api_client, nurse_user):
        item = MedicamentoUrgencia.objects.create(
            codigo="EXP-API",
            nome="Expirado API",
            quantidade_stock=5,
            stock_minimo=1,
            validade=date.today() - timedelta(days=1),
        )
        api_client.force_authenticate(user=nurse_user)
        r = api_client.post(
            f"/api/v1/stock/items/{item.pk}/saida/",
            {"quantidade": 1},
            format="json",
        )
        assert r.status_code == 400
        assert "expirado" in r.data["message"].lower()
        item.refresh_from_db()
        assert item.quantidade_stock == 5

    def test_api_definir_stock_inicial_idempotente(self, api_client, nurse_user):
        api_client.force_authenticate(user=nurse_user)
        created = api_client.post(
            "/api/v1/stock/items/",
            {
                "nome": "Soro S26",
                "categoria": "MATERIAL_CLINICO",
                "unidade": "saco",
                "quantidade_inicial": 0,
            },
            format="json",
        )
        assert created.status_code == 201
        item_id = created.data["data"]["id"]
        assert created.data["data"]["stock_inicial_por_confirmar"] is True
        first = api_client.post(
            f"/api/v1/stock/items/{item_id}/definir-stock-inicial/",
            {"quantidade": 8, "stock_minimo": 2},
            format="json",
        )
        assert first.status_code == 200
        second = api_client.post(
            f"/api/v1/stock/items/{item_id}/definir-stock-inicial/",
            {"quantidade": 3},
            format="json",
        )
        assert second.status_code == 400

    def test_api_duplicado_exacto(self, api_client, nurse_user):
        api_client.force_authenticate(user=nurse_user)
        payload = {
            "nome": "Adrenalina 1mg",
            "forma_apresentacao": "ampola",
            "categoria": "MEDICAMENTO",
            "unidade": "ampola",
            "quantidade_inicial": 1,
        }
        first = api_client.post("/api/v1/stock/items/", payload, format="json")
        assert first.status_code == 201
        second = api_client.post("/api/v1/stock/items/", payload, format="json")
        assert second.status_code == 400
        assert second.data["errors"]["existing_id"] == first.data["data"]["id"]
