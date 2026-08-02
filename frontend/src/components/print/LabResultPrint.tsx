import type { ReactNode } from "react";

import { PrintDocument, type PrintDocumentProps, type PrintSignatureBlock } from "./PrintDocument";

export interface LabResultPrintProps extends Omit<PrintDocumentProps, "title"> {
  patientName?: string;
  orderNumber?: string;
  results?: ReactNode;
  validatedBy?: string;
  signature?: PrintSignatureBlock;
}

export function LabResultPrint({
  patientName,
  orderNumber,
  documentNumber,
  results,
  validatedBy,
  signature,
  ...props
}: LabResultPrintProps) {
  return (
    <PrintDocument
      title="Resultado de Laboratório"
      documentNumber={documentNumber ?? orderNumber}
      signature={
        signature ?? {
          label: "Validado por",
          name: validatedBy,
          title: "Responsável de laboratório",
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
      <div>{results}</div>
    </PrintDocument>
  );
}
