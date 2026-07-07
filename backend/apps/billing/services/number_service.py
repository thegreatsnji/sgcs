"""Geração de números sequenciais de faturação."""

from django.utils import timezone


class BillingNumberService:
    @staticmethod
    def _next_number(model, field: str, prefix: str) -> str:
        year = timezone.now().year
        full_prefix = f"{prefix}-{year}-"
        last = (
            model.objects.filter(**{f"{field}__startswith": full_prefix})
            .order_by(f"-{field}")
            .values_list(field, flat=True)
            .first()
        )
        if last:
            try:
                sequence = int(last.split("-")[-1]) + 1
            except ValueError:
                sequence = 1
        else:
            sequence = 1
        return f"{full_prefix}{sequence:06d}"

    @classmethod
    def generate_quote(cls) -> str:
        from apps.billing.constants import QUOTE_NUMBER_PREFIX
        from apps.billing.models import Orcamento

        return cls._next_number(Orcamento, "numero", QUOTE_NUMBER_PREFIX)

    @classmethod
    def generate_invoice(cls) -> str:
        from apps.billing.constants import INVOICE_NUMBER_PREFIX
        from apps.billing.models import Fatura

        return cls._next_number(Fatura, "numero", INVOICE_NUMBER_PREFIX)

    @classmethod
    def generate_receipt(cls) -> str:
        from apps.billing.constants import RECEIPT_NUMBER_PREFIX
        from apps.billing.models import Recibo

        return cls._next_number(Recibo, "numero", RECEIPT_NUMBER_PREFIX)
