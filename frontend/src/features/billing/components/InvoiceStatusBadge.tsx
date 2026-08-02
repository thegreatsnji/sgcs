import { Badge } from "@/design-system";
import { FATURA_ESTADO_LABEL, FATURA_ESTADO_VARIANT } from "@/features/billing/utils/formatBilling";
import type { FaturaEstado } from "@/types/billing";

export function InvoiceStatusBadge({ estado }: { estado: FaturaEstado }) {
  return <Badge variant={FATURA_ESTADO_VARIANT[estado]}>{FATURA_ESTADO_LABEL[estado]}</Badge>;
}
