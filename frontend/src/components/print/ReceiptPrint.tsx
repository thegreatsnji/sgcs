import type { ReactNode } from "react";

import { CurrencyDisplay } from "@/design-system";

import { PrintDocument, type PrintDocumentProps } from "./PrintDocument";

export interface ReceiptPrintProps extends Omit<PrintDocumentProps, "title"> {
  patientName?: string;
  invoiceNumber?: string;
  paymentMethod?: string;
  amount?: string | number;
  children?: ReactNode;
}

export function ReceiptPrint({
  patientName,
  invoiceNumber,
  paymentMethod,
  amount,
  children,
  ...props
}: ReceiptPrintProps) {
  return (
    <PrintDocument title="Recibo de Pagamento" {...props}>
      <dl className="grid gap-2 text-sm sm:grid-cols-2">
        {patientName && (
          <div>
            <dt className="text-slate-500">Paciente</dt>
            <dd className="font-medium">{patientName}</dd>
          </div>
        )}
        {invoiceNumber && (
          <div>
            <dt className="text-slate-500">Fatura</dt>
            <dd>{invoiceNumber}</dd>
          </div>
        )}
        {paymentMethod && (
          <div>
            <dt className="text-slate-500">Método de pagamento</dt>
            <dd>{paymentMethod}</dd>
          </div>
        )}
        {amount !== undefined && (
          <div>
            <dt className="text-slate-500">Valor recebido</dt>
            <dd className="text-lg font-bold">
              <CurrencyDisplay value={amount} />
            </dd>
          </div>
        )}
      </dl>
      {children}
    </PrintDocument>
  );
}
