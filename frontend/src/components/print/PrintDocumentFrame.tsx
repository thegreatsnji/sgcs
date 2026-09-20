import type { ReactNode } from "react";

interface PrintDocumentFrameProps {
  title: string;
  subtitle?: string;
  operatorName?: string;
  printedAt?: Date;
  children: ReactNode;
  footerNote?: string;
  pageNumber?: number;
  pageTotal?: number;
}

/**
 * Moldura comum para impressões clínicas (recibo, fatura, resultados, etc.).
 * Usar dentro de rotas de impressão com @media print.
 */
export function PrintDocumentFrame({
  title,
  subtitle,
  operatorName,
  printedAt = new Date(),
  children,
  footerNote = "Documento emitido pelo SGCS da Clínica SauVida",
  pageNumber,
  pageTotal,
}: PrintDocumentFrameProps) {
  const when = printedAt.toLocaleString("pt-PT", {
    dateStyle: "short",
    timeStyle: "short",
  });

  return (
    <div className="mx-auto max-w-[210mm] bg-white p-8 text-slate-900 print:p-6">
      <header className="flex items-start justify-between gap-6 border-b border-slate-200 pb-4">
        <div>
          <p className="text-lg font-bold tracking-tight text-primary-800">Clínica SauVida</p>
          <h1 className="mt-1 text-xl font-semibold">{title}</h1>
          {subtitle ? <p className="mt-0.5 text-sm text-slate-600">{subtitle}</p> : null}
        </div>
        <div className="text-right text-xs text-slate-500">
          <p>{when}</p>
          {operatorName ? <p className="mt-1">Operador: {operatorName}</p> : null}
        </div>
      </header>

      <main className="py-6">{children}</main>

      <footer className="mt-8 border-t border-slate-200 pt-4 text-xs text-slate-500">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <span>{footerNote}</span>
          {pageNumber != null && pageTotal != null ? (
            <span>
              Página {pageNumber} de {pageTotal}
            </span>
          ) : null}
        </div>
      </footer>
    </div>
  );
}
