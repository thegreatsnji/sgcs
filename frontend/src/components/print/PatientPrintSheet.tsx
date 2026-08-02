import type { ReactNode } from "react";

import { PrintDocument, type PrintDocumentProps } from "./PrintDocument";

export interface PatientPrintSheetProps extends Omit<PrintDocumentProps, "title"> {
  patientName?: string;
  patientNumber?: string;
  children?: ReactNode;
}

export function PatientPrintSheet({
  patientName,
  patientNumber,
  documentNumber,
  children,
  ...props
}: PatientPrintSheetProps) {
  return (
    <PrintDocument
      title="Ficha do Paciente"
      documentNumber={documentNumber ?? patientNumber}
      {...props}
    >
      {patientName && (
        <p className="mb-4 text-base font-semibold text-slate-900">{patientName}</p>
      )}
      {children}
    </PrintDocument>
  );
}
