import type { ReactNode } from "react";

import { PrintDocument, type PrintDocumentProps, type PrintSignatureBlock } from "./PrintDocument";

export interface PrescriptionPrintProps extends Omit<PrintDocumentProps, "title"> {
  patientName?: string;
  prescriberName?: string;
  items?: ReactNode;
  notes?: string;
  signature?: PrintSignatureBlock;
}

export function PrescriptionPrint({
  patientName,
  prescriberName,
  items,
  notes,
  signature,
  ...props
}: PrescriptionPrintProps) {
  return (
    <PrintDocument
      title="Receita Médica"
      signature={
        signature ?? {
          label: "Médico prescriptor",
          name: prescriberName,
        }
      }
      {...props}
    >
      {patientName && (
        <p className="mb-4">
          <span className="text-slate-500">Paciente:</span>{" "}
          <span className="font-semibold">{patientName}</span>
        </p>
      )}
      <div className="space-y-2">{items}</div>
      {notes && (
        <p className="mt-6 text-xs text-slate-600">
          <span className="font-medium">Observações:</span> {notes}
        </p>
      )}
    </PrintDocument>
  );
}
