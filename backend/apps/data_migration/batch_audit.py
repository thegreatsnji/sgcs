"""Auditoria agregada de um lote histórico (sem PII, sem escrita)."""

from __future__ import annotations

from collections import Counter
from typing import Any

from apps.appointments.models import Appointment
from apps.audit_logs.models import AuditLog
from apps.billing.models import Fatura, Pagamento, Recibo
from apps.data_migration.constants import FONTE_MIGRACAO
from apps.finance.models import MovimentoFinanceiro
from apps.laboratory.models import PedidoLaboratorial
from apps.patients.constants import HistoryEventType
from apps.patients.models import Patient, PatientHistory
from apps.pharmacy.models import MedicamentoUrgencia, MovimentoStockUrgencia
from apps.data_migration.rollback import rollback_batch


def _meta(obj) -> dict:
    return obj.metadata if isinstance(obj.metadata, dict) else {}


def audit_batch(batch_id: str) -> dict[str, Any]:
    patients = Patient.objects.filter(metadata__import_batch=batch_id, is_deleted=False)
    histories = PatientHistory.objects.filter(
        source_module=FONTE_MIGRACAO,
        metadata__import_batch=batch_id,
    )
    clinical = histories.exclude(event_type=HistoryEventType.REGISTO)
    registo = histories.filter(event_type=HistoryEventType.REGISTO)
    finance_kind = histories.filter(metadata__kind="REGISTO_FINANCEIRO_HISTORICO")
    audit_logs = AuditLog.objects.filter(metadata__import_batch=batch_id)

    mids = [(p.pk, _meta(p).get("migration_id") or "") for p in patients]
    mid_values = [mid for _, mid in mids]
    dup_mids = len(mid_values) - len(set(mid_values))
    empty_name = patients.filter(first_name="").count()
    provenance_incomplete_patients = sum(
        1
        for patient in patients
        if not (
            _meta(patient).get("source") == FONTE_MIGRACAO
            and _meta(patient).get("import_batch") == batch_id
            and _meta(patient).get("migration_id")
        )
    )
    hids = [(_meta(row).get("historico_id") or "") for row in clinical]
    orphan_events = clinical.filter(patient__isnull=True).count()
    orphan_patient_missing = sum(
        1
        for row in clinical
        if not Patient.objects.filter(pk=row.patient_id, is_deleted=False).exists()
    )
    patient_link_bad = sum(
        1
        for row in clinical
        if (_meta(row).get("migration_id") or "") != (_meta(row.patient).get("migration_id") or "")
    )
    provenance_incomplete_history = sum(
        1
        for row in clinical
        if not (
            _meta(row).get("source") == FONTE_MIGRACAO
            and _meta(row).get("import_batch") == batch_id
            and _meta(row).get("historico_id")
            and _meta(row).get("source_sheet")
            and (_meta(row).get("source_row") not in (None, ""))
        )
    )
    histories_on_foreign_patients = sum(
        1
        for row in histories
        if _meta(row.patient).get("import_batch") != batch_id
        and _meta(row.patient).get("source") != FONTE_MIGRACAO
    )

    financial_leakage = {
        "fatura_com_batch": _count_meta(Fatura, batch_id),
        "pagamento_com_batch": _count_meta(Pagamento, batch_id),
        "recibo_com_batch": _count_meta(Recibo, batch_id),
        "movimento_financeiro_com_batch": _count_meta(MovimentoFinanceiro, batch_id),
        "appointment_com_batch": _count_meta(Appointment, batch_id),
        "pedido_laboratorial_com_batch": _count_meta(PedidoLaboratorial, batch_id),
    }
    stock_leakage = {
        "medicamento_urgencia_com_batch": _count_meta(MedicamentoUrgencia, batch_id),
        "movimento_stock_com_batch": _count_meta(MovimentoStockUrgencia, batch_id),
    }
    rollback = rollback_batch(batch_id, apply=False)
    unexpected = {key: value for key, value in {**financial_leakage, **stock_leakage}.items() if value}

    return {
        "import_batch": batch_id,
        "fonte": FONTE_MIGRACAO,
        "escrita_bd": False,
        "pacientes": patients.count(),
        "historicos": histories.count(),
        "historicos_registo_importacao": registo.count(),
        "historicos_clinicos": clinical.count(),
        "historicos_financeiros_extra": finance_kind.count(),
        "audit_logs_associados": audit_logs.count(),
        "por_tipo_clinico": dict(
            Counter((_meta(row).get("tipo_evento_fonte") or row.event_type) for row in clinical)
        ),
        "por_source_sheet": dict(Counter((_meta(row).get("source_sheet") or "(vazio)") for row in clinical)),
        "migration_ids_vazios": sum(1 for mid in mid_values if not mid),
        "migration_ids_duplicados": dup_mids,
        "nomes_vazios": empty_name,
        "dados_verificados_true": patients.filter(metadata__dados_verificados=True).count(),
        "dados_verificados_false": patients.filter(metadata__dados_verificados=False).count(),
        "orfos": orphan_events + orphan_patient_missing,
        "ligacao_paciente_incorrecta": patient_link_bad,
        "historicos_em_pacientes_externos": histories_on_foreign_patients,
        "provenance_incompleta_pacientes": provenance_incomplete_patients,
        "provenance_incompleta_historico": provenance_incomplete_history,
        "historico_id_duplicados": len(hids) - len(set(hids)),
        "financial_leakage": financial_leakage,
        "stock_leakage": stock_leakage,
        "tabelas_inesperadas": unexpected,
        "rollback_dry_run": rollback,
        "contagens_operacionais": {
            "Fatura": Fatura.objects.count(),
            "Pagamento": Pagamento.objects.count(),
            "Recibo": Recibo.objects.count(),
            "MovimentoFinanceiro": MovimentoFinanceiro.objects.count(),
            "Appointment": Appointment.objects.count(),
            "PedidoLaboratorial": PedidoLaboratorial.objects.count(),
            "MedicamentoUrgencia": MedicamentoUrgencia.objects.count(),
            "MovimentoStockUrgencia": MovimentoStockUrgencia.objects.count(),
        },
    }


def _has_meta(model) -> bool:
    return any(field.name == "metadata" for field in model._meta.get_fields())


def _count_meta(model, batch_id: str) -> int:
    if not _has_meta(model):
        return 0
    try:
        return model.objects.filter(metadata__import_batch=batch_id).count()
    except Exception:
        return 0
