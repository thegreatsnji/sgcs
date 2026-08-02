import type { ReactNode } from "react";

export interface PrintContactInfo {
  phone?: string;
  email?: string;
  address?: string;
  website?: string;
}

export interface PrintSignatureBlock {
  label?: string;
  name?: string;
  title?: string;
}

export interface PrintDocumentProps {
  clinicName?: string;
  clinicLogoUrl?: string;
  title: string;
  documentNumber?: string;
  documentDate?: string;
  footerContacts?: PrintContactInfo;
  signature?: PrintSignatureBlock;
  children?: ReactNode;
  className?: string;
}

function ContactLine({ label, value }: { label: string; value?: string }) {
  if (!value) return null;
  return (
    <span className="print-document__contact">
      <span className="font-medium">{label}:</span> {value}
    </span>
  );
}

export function PrintDocument({
  clinicName = "Clínica SauVida",
  clinicLogoUrl,
  title,
  documentNumber,
  documentDate,
  footerContacts,
  signature,
  children,
  className = "",
}: PrintDocumentProps) {
  return (
    <article className={`print-document rounded-lg border border-slate-200 bg-white p-8 text-slate-900 ${className}`}>
      <header className="print-document__header mb-8 border-b border-slate-200 pb-6">
        <div className="flex items-start justify-between gap-6">
          <div className="flex items-center gap-4">
            {clinicLogoUrl ? (
              <img
                src={clinicLogoUrl}
                alt=""
                className="h-14 w-14 rounded-lg object-contain"
              />
            ) : (
              <div
                className="flex h-14 w-14 items-center justify-center rounded-lg bg-primary-50 text-xs font-semibold text-primary-700"
                aria-hidden
              >
                LOGO
              </div>
            )}
            <div>
              <p className="text-lg font-bold tracking-tight">{clinicName}</p>
              <p className="text-xs text-slate-500">Sistema de Gestão Clínica SauVida</p>
            </div>
          </div>
          <div className="text-right text-sm">
            {documentNumber && (
              <p>
                <span className="text-slate-500">N.º</span>{" "}
                <span className="font-semibold">{documentNumber}</span>
              </p>
            )}
            {documentDate && (
              <p className="mt-1 text-slate-600">
                <span className="text-slate-500">Data:</span> {documentDate}
              </p>
            )}
          </div>
        </div>
        <h1 className="mt-6 text-xl font-bold uppercase tracking-wide text-slate-900">{title}</h1>
      </header>

      <div className="print-document__body text-sm leading-relaxed">{children}</div>

      {signature && (
        <footer className="print-signature-block mt-12 border-t border-slate-200 pt-8">
          <p className="text-xs font-medium tracking-wide text-slate-500 uppercase">
            {signature.label ?? "Assinatura"}
          </p>
          <div className="mt-10 border-b border-slate-400 pb-1" style={{ width: "220px" }} />
          {signature.name && <p className="mt-2 text-sm font-semibold">{signature.name}</p>}
          {signature.title && <p className="text-xs text-slate-500">{signature.title}</p>}
        </footer>
      )}

      {footerContacts && (
        <footer className="print-document__footer mt-10 border-t border-slate-100 pt-4 text-xs text-slate-500">
          <div className="flex flex-wrap gap-x-4 gap-y-1">
            <ContactLine label="Telefone" value={footerContacts.phone} />
            <ContactLine label="E-mail" value={footerContacts.email} />
            <ContactLine label="Morada" value={footerContacts.address} />
            <ContactLine label="Web" value={footerContacts.website} />
          </div>
        </footer>
      )}
    </article>
  );
}
