import { Card } from "@/design-system";
import type { Receipt } from "@/types/billing";
import { formatDisplayDateTime } from "@/utils/date";

interface ReceiptPreviewProps {
  receipt: Receipt;
}

export function ReceiptPreview({ receipt }: ReceiptPreviewProps) {
  return (
    <Card title={`Recibo ${receipt.numero}`}>
      <dl className="grid gap-2 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-slate-500">Paciente</dt>
          <dd>{receipt.paciente_nome}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Fatura</dt>
          <dd>{receipt.fatura_numero}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Valor</dt>
          <dd className="font-semibold">{receipt.pagamento_valor} FCFA</dd>
        </div>
        <div>
          <dt className="text-slate-500">Método</dt>
          <dd>{receipt.metodo_pagamento}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Emitido em</dt>
          <dd>{formatDisplayDateTime(receipt.emitido_em)}</dd>
        </div>
      </dl>
    </Card>
  );
}
