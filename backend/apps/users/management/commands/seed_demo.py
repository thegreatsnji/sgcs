"""
Gera dados de demonstração para desenvolvimento / demos da clínica SauVida.

Utilizadores demo (perfis operacionais da clínica; sem FINANCEIRO — funções financeiras no Director):

Uso:
  python manage.py seed_rbac
  python manage.py seed_demo
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.appointments.constants import AppointmentStatus
from apps.appointments.models import Appointment
from apps.appointments.services.appointment_service import AppointmentService
from apps.authentication.models import UserRole
from apps.billing.constants import MetodoPagamento
from apps.billing.models import Servico
from apps.billing.services.billing_service import BillingService
from apps.laboratory.constants import DEFAULT_EXAM_CATEGORY, PedidoLaboratorialEstado
from apps.laboratory.models import ExameLaboratorial, PedidoLaboratorial
from apps.laboratory.services.laboratory_service import LaboratoryService
from apps.laboratory.services.number_service import LaboratoryNumberService
from apps.notifications.constants import NotificacaoCanal, NotificacaoTipo
from apps.notifications.models import Notificacao
from apps.patients.models import Patient
from apps.patients.services.patient_service import PatientService
from apps.reception.constants import QueuePriority
from apps.reception.services.reception_service import ReceptionService

User = get_user_model()

DEMO_PASSWORD = "Demo@2026!"

DEMO_USERS = [
    {
        "email": "admin@sauvida.gw",
        "first_name": "Aminata",
        "last_name": "Administradora",
        "role": UserRole.ADMINISTRADOR,
        "is_staff": True,
        "is_superuser": True,
    },
    {
        "email": "director@sauvida.gw",
        "first_name": "Carlos",
        "last_name": "Director",
        "role": UserRole.DIRECTOR,
    },
    {
        "email": "medico1@sauvida.gw",
        "first_name": "Maria",
        "last_name": "Santos",
        "role": UserRole.MEDICO,
    },
    {
        "email": "medico2@sauvida.gw",
        "first_name": "João",
        "last_name": "Pereira",
        "role": UserRole.MEDICO,
    },
    {
        "email": "rececao@sauvida.gw",
        "first_name": "Fatima",
        "last_name": "Rececionista",
        "role": UserRole.RECECIONISTA,
    },
    {
        "email": "laboratorio@sauvida.gw",
        "first_name": "Ibrahim",
        "last_name": "Laboratório",
        "role": UserRole.LABORATORIO,
    },
    {
        "email": "enfermeiro@sauvida.gw",
        "first_name": "Helena",
        "last_name": "Enfermeira",
        "role": UserRole.ENFERMEIRO,
    },
]

PATIENTS_DATA = [
    {
        "first_name": "Aissatu",
        "last_name": "Djau",
        "birth_date": date(1990, 5, 12),
        "gender": "F",
        "phone": "+245955100001",
        "document_type": "BI",
        "document_number": "DEMO-BI-001",
        "address_city": "Bissau",
        "blood_type": "O+",
    },
    {
        "first_name": "Bacari",
        "last_name": "Camará",
        "birth_date": date(1985, 11, 3),
        "gender": "M",
        "phone": "+245955100002",
        "document_type": "BI",
        "document_number": "DEMO-BI-002",
        "address_city": "Bissau",
        "blood_type": "A+",
    },
    {
        "first_name": "Cadija",
        "last_name": "Baldé",
        "birth_date": date(1998, 2, 20),
        "gender": "F",
        "phone": "+245955100003",
        "document_type": "BI",
        "document_number": "DEMO-BI-003",
        "address_city": "Bafatá",
        "blood_type": "B+",
    },
    {
        "first_name": "Domingos",
        "last_name": "Mendes",
        "birth_date": date(1972, 8, 15),
        "gender": "M",
        "phone": "+245955100004",
        "document_type": "BI",
        "document_number": "DEMO-BI-004",
        "address_city": "Bissau",
        "blood_type": "AB+",
    },
    {
        "first_name": "Eugénia",
        "last_name": "Lopes",
        "birth_date": date(2001, 1, 9),
        "gender": "F",
        "phone": "+245955100005",
        "document_type": "PASSAPORTE",
        "document_number": "DEMO-PP-005",
        "address_city": "Cacheu",
        "blood_type": "O-",
    },
    {
        "first_name": "Francisco",
        "last_name": "Silva",
        "birth_date": date(1968, 12, 1),
        "gender": "M",
        "phone": "+245955100006",
        "document_type": "BI",
        "document_number": "DEMO-BI-006",
        "address_city": "Bissau",
        "blood_type": "A-",
    },
]


class Command(BaseCommand):
    help = "Gera utilizadores e dados de demonstração SauVida (desenvolvimento)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset-demo-users",
            action="store_true",
            help="Recria palavras-passe dos utilizadores demo existentes",
        )
        parser.add_argument(
            "--skip-if-present",
            action="store_true",
            help="Não faz nada se o utilizador admin demo já existir (arranque rápido)",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["skip_if_present"] and not options["reset_demo_users"]:
            if User.objects.filter(email="admin@sauvida.gw").exists():
                self.stdout.write("seed_demo: dados demo já presentes (skip).")
                return

        self.stdout.write(self.style.MIGRATE_HEADING("=== SGCS seed_demo ==="))
        self.stdout.write("Ambiente de desenvolvimento — palavras-passe temporárias.\n")

        users = self._ensure_users(reset=options["reset_demo_users"])
        self._deactivate_legacy_financeiro_demo()
        admin = users["admin@sauvida.gw"]
        director = users["director@sauvida.gw"]
        medico1 = users["medico1@sauvida.gw"]
        medico2 = users["medico2@sauvida.gw"]
        rececao = users["rececao@sauvida.gw"]
        lab_user = users["laboratorio@sauvida.gw"]

        patients = self._ensure_patients(rececao)
        servico = self._ensure_servico()
        appointments = self._ensure_appointments(patients, medico1, medico2, rececao)
        self._ensure_queue(patients, rececao)
        self._ensure_lab(appointments, lab_user)
        self._ensure_billing(patients, servico, director)
        self._ensure_notifications(users)

        self._print_credentials(users)
        self.stdout.write(self.style.SUCCESS("\nseed_demo concluído com sucesso."))

    def _ensure_users(self, reset: bool) -> dict:
        created_map = {}
        for spec in DEMO_USERS:
            email = spec["email"]
            existing = User.objects.filter(email=email).first()
            if existing:
                if reset:
                    existing.set_password(DEMO_PASSWORD)
                    existing.role = spec["role"]
                    existing.is_active = True
                    existing.save(update_fields=["password", "role", "is_active"])
                    self.stdout.write(f"  · palavra-passe redefinida: {email}")
                else:
                    self.stdout.write(f"  · utilizador já existe: {email}")
                created_map[email] = existing
                continue

            user = User.objects.create_user(
                email=email,
                password=DEMO_PASSWORD,
                first_name=spec["first_name"],
                last_name=spec["last_name"],
                role=spec["role"],
                is_staff=spec.get("is_staff", False),
                is_superuser=spec.get("is_superuser", False),
            )
            created_map[email] = user
            self.stdout.write(self.style.SUCCESS(f"  ✓ criado: {email} ({spec['role']})"))
        return created_map

    def _deactivate_legacy_financeiro_demo(self) -> None:
        updated = User.objects.filter(email="financeiro@sauvida.gw").update(is_active=False)
        if updated:
            self.stdout.write(
                self.style.WARNING(
                    "  · conta demo financeiro@sauvida.gw desactivada (perfil FINANCEIRO não utilizado)"
                )
            )

    def _ensure_patients(self, creator):
        patients = []
        for data in PATIENTS_DATA:
            existing = Patient.objects.filter(document_number=data["document_number"]).first()
            if existing:
                patients.append(existing)
                continue
            patient = PatientService.create(data, user=creator)
            patients.append(patient)
            self.stdout.write(f"  ✓ paciente: {patient.full_name} ({patient.patient_number})")
        return patients

    def _ensure_servico(self):
        servico, created = Servico.objects.get_or_create(
            codigo="DEMO-CONS-001",
            defaults={
                "nome": "Consulta Geral (Demo)",
                "categoria": "CONSULTA",
                "preco": Decimal("5000.00"),
                "activo": True,
            },
        )
        if created:
            self.stdout.write("  ✓ serviço de faturação demo criado")
        return servico

    def _ensure_appointments(self, patients, medico1, medico2, rececao):
        now = timezone.now()
        slots = [
            (patients[0], medico1, now + timedelta(hours=1), AppointmentStatus.CONFIRMADA),
            (patients[1], medico1, now + timedelta(hours=2), AppointmentStatus.AGENDADA),
            (patients[2], medico2, now + timedelta(hours=3), AppointmentStatus.CONFIRMADA),
            (patients[3], medico2, now + timedelta(hours=4), AppointmentStatus.AGENDADA),
        ]
        created = []
        for patient, doctor, when, status in slots:
            exists = Appointment.objects.filter(
                patient=patient,
                doctor=doctor,
                scheduled_at=when,
            ).exists()
            if exists:
                created.extend(
                    list(
                        Appointment.objects.filter(
                            patient=patient,
                            doctor=doctor,
                            scheduled_at=when,
                        )
                    )
                )
                continue
            try:
                appt = AppointmentService.create(
                    patient_id=patient.id,
                    user=rececao,
                    scheduled_at=when,
                    doctor_id=doctor.id,
                    duration_minutes=30,
                    priority=QueuePriority.NORMAL,
                    notes="Consulta de demonstração",
                    chief_complaint="Sintomas gerais (demo)",
                    receptionist_id=rececao.id,
                )
                if status == AppointmentStatus.CONFIRMADA:
                    AppointmentService.confirmar_consulta(appt.id, user=rececao)
                    appt.refresh_from_db()
                created.append(appt)
                self.stdout.write(f"  ✓ consulta: {appt.appointment_number}")
            except Exception as exc:  # noqa: BLE001 — demo seed deve continuar
                self.stdout.write(self.style.WARNING(f"  · consulta omitida: {exc}"))
        return created

    def _ensure_queue(self, patients, rececao):
        for patient, priority in (
            (patients[4], QueuePriority.NORMAL),
            (patients[5], QueuePriority.HIGH),
        ):
            try:
                check_in = ReceptionService.check_in(
                    patient.id,
                    rececao,
                    priority=priority,
                    notes="Check-in demo",
                )
                self.stdout.write(f"  ✓ fila: check-in #{check_in.pk} ({patient.full_name})")
            except Exception as exc:  # noqa: BLE001
                self.stdout.write(self.style.WARNING(f"  · fila omitida: {exc}"))

    def _ensure_lab(self, appointments, lab_user):
        if not appointments:
            self.stdout.write(self.style.WARNING("  · laboratório omitido: sem consultas"))
            return
        appt = appointments[0]
        if PedidoLaboratorial.objects.filter(consulta=appt).exists():
            return
        try:
            pedido = PedidoLaboratorial.objects.create(
                numero_pedido=LaboratoryNumberService.generate(),
                consulta=appt,
                paciente=appt.patient,
                medico=appt.doctor,
                prioridade=QueuePriority.NORMAL,
                observacoes="Pedido demo de hemograma",
                estado=PedidoLaboratorialEstado.PENDENTE,
                registado_por=lab_user,
            )
            ExameLaboratorial.objects.create(
                pedido=pedido,
                nome_exame="Hemograma Completo (Demo)",
                categoria=DEFAULT_EXAM_CATEGORY,
                estado=PedidoLaboratorialEstado.PENDENTE,
            )
            LaboratoryService.receber_pedido(pedido.pk, user=lab_user)
            self.stdout.write(f"  ✓ pedido laboratorial: {pedido.numero_pedido}")
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f"  · laboratório omitido: {exc}"))

    def _ensure_billing(self, patients, servico, director):
        patient = patients[1]
        try:
            orc = BillingService.criar_orcamento(
                patient.id,
                director,
                itens=[
                    {
                        "servico_id": servico.id,
                        "quantidade": 1,
                        "preco_unitario": str(servico.preco),
                    }
                ],
            )
            BillingService.aprovar_orcamento(orc.pk, director)
            fatura = BillingService.gerar_fatura(
                director,
                orcamento_id=orc.pk,
            )
            pagamento = BillingService.registar_pagamento(
                fatura.pk,
                director,
                valor=fatura.total,
                metodo_pagamento=MetodoPagamento.DINHEIRO,
                referencia="DEMO-PAG-001",
            )
            BillingService.confirmar_pagamento(pagamento.pk, director)
            self.stdout.write(f"  ✓ fatura/pagamento: {fatura.numero}")
        except Exception as exc:  # noqa: BLE001
            self.stdout.write(self.style.WARNING(f"  · faturação omitida: {exc}"))

    def _ensure_notifications(self, users):
        for user in users.values():
            if Notificacao.objects.filter(utilizador=user, titulo__startswith="[Demo]").exists():
                continue
            Notificacao.objects.create(
                utilizador=user,
                titulo="[Demo] Bem-vindo ao SGCS SauVida",
                mensagem=(
                    f"Olá {user.first_name}. Esta é uma notificação de demonstração "
                    "para o seu perfil operacional."
                ),
                tipo=NotificacaoTipo.INFORMATIVA,
                canal=NotificacaoCanal.INTERNO,
                lida=False,
            )
        self.stdout.write("  ✓ notificações demo")

    def _print_credentials(self, users):
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.MIGRATE_HEADING("CREDENCIAIS DEMO (apenas desenvolvimento)"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"{'Perfil':<16} {'E-mail':<28} {'Palavra-passe'}")
        self.stdout.write("-" * 60)
        role_labels = {
            UserRole.ADMINISTRADOR: "Administrador",
            UserRole.DIRECTOR: "Director",
            UserRole.MEDICO: "Médico",
            UserRole.RECECIONISTA: "Receção",
            UserRole.LABORATORIO: "Laboratório",
            UserRole.ENFERMEIRO: "Enfermagem",
        }
        for spec in DEMO_USERS:
            email = spec["email"]
            user = users[email]
            label = role_labels.get(user.role, user.role)
            self.stdout.write(f"{label:<16} {email:<28} {DEMO_PASSWORD}")
        self.stdout.write("-" * 60)
        self.stdout.write("Perfil FINANCEIRO: não utilizado — use director@sauvida.gw para financeiro.")
        self.stdout.write("=" * 60 + "\n")
