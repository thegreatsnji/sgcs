"""Definições de eventos de domínio do SGCS."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4

from django.utils import timezone


@dataclass(frozen=True, slots=True)
class DomainEvent:
    name: str
    payload: dict[str, Any] = field(default_factory=dict)
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: datetime = field(default_factory=timezone.now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "name": self.name,
            "payload": self.payload,
            "occurred_at": self.occurred_at.isoformat(),
        }


class EventNames:
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    USER_DELETED = "user.deleted"
    USER_LOGIN = "user.login"
    USER_LOGOUT = "user.logout"
    FILE_UPLOADED = "file.uploaded"
    SETTINGS_UPDATED = "settings.updated"
    ANALYTICS_RECORDED = "analytics.recorded"
    PATIENT_CREATED = "patient.created"
    PATIENT_UPDATED = "patient.updated"
    PATIENT_DEACTIVATED = "patient.deactivated"
    LABORATORY_RESULT_VALIDATED = "laboratory.result.validated"
    LABORATORY_RESULT_PUBLISHED = "laboratory.result.published"
    LABORATORY_RESULT_CREATED = "laboratory.result.created"
    BILLING_QUOTE_CREATED = "billing.quote.created"
    BILLING_INVOICE_CREATED = "billing.invoice.created"
    BILLING_PAYMENT_CONFIRMED = "billing.payment.confirmed"
    BILLING_RECEIPT_CREATED = "billing.receipt.created"
    FINANCE_CASH_OPENED = "finance.cash.opened"
    FINANCE_CASH_CLOSED = "finance.cash.closed"
    FINANCE_EXPENSE_CREATED = "finance.expense.created"
    FINANCE_PAYMENT_RECEIVED = "finance.payment.received"
    FINANCE_REPORT_GENERATED = "finance.report.generated"
    REPORT_GENERATED = "report.generated"
    DASHBOARD_UPDATED = "dashboard.updated"
    STATISTICS_UPDATED = "statistics.updated"
    SETTINGS_UPDATED = "settings.updated"
    BACKUP_CREATED = "backup.created"
    BACKUP_RESTORED = "backup.restored"
    SYSTEM_UPDATED = "system.updated"
    DOCTOR_PRESCRIPTION_CREATED = "doctor.prescription.created"
    DOCTOR_DISCHARGE_CREATED = "doctor.discharge.created"
    DOCTOR_FOLLOWUP_CREATED = "doctor.followup.created"
