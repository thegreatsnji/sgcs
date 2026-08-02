import type { ReactNode } from "react";

import { CurrencyDisplay } from "@/design-system";

import { PrintDocument, type PrintDocumentProps } from "./PrintDocument";

export interface InvoicePrintProps extends Omit<PrintDocumentProps, "title"> {
  patientName?: string;
  items?: ReactNode;
  subtotal?: string | number;
  discount?: string | number;
  tax?: string | number;
  total?: string | number;
}

export function InvoicePrint({
  patientName,
  items,
  subtotal,
  discount,
  tax,
  total,
  ...props
}: InvoicePrintProps) {
  return (
    <PrintDocument title="Fatura" {...props}>
      {patientName && (
        <p className="mb-4">
          <span className="text-slate-500">Cliente:</span>{" "}
          <span className="font-semibold">{patientName}</span>
        </p>
      )}
      <div className="mb-6">{items}</div>
      <dl className="ml-auto max-w-xs space-y-1 text-sm">
        {subtotal !== undefined && (
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Subtotal</dt>
            <dd><CurrencyDisplay value={subtotal} /></dd>
          </div>
        )}
        {discount !== undefined && (
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Desconto</dt>
            <dd><CurrencyDisplay value={discount} /></dd>
          </div>
        )}
        {tax !== undefined && (
          <div className="flex justify-between gap-4">
            <dt className="text-slate-500">Imposto</dt>
            <dd><CurrencyDisplay value={tax} /></dd>
          </div>
        )}
        {total !== undefined && (
          <div className="flex justify-between gap-4 border-t border-slate-200 pt-2 font-semibold">
            <dt>Total</dt>
            <dd><CurrencyDisplay value={total} /></dd>
          </div>
        )}
      </dl>
    </PrintDocument>
  );
}
