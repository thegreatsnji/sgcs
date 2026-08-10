import type { ReceiptPrintData } from "@/features/billing/types/receiptPrint";
import {
  RECEIPT_BRANDING,
  resolveClinicLogoUrl,
} from "@/features/billing/constants/receiptBranding";
import { METODO_PAGAMENTO_LABEL } from "@/features/billing/utils/formatBilling";
import type { MetodoPagamento } from "@/types/billing";

function formatFcfa(value: string | number): string {
  const num = typeof value === "string" ? Number(value) : value;
  if (!Number.isFinite(num)) return "—";
  return `${num.toLocaleString("pt-PT")} FCFA`;
}

export interface SauVidaReceiptDocumentProps {
  data: ReceiptPrintData;
  className?: string;
}

export function SauVidaReceiptDocument({ data, className = "" }: SauVidaReceiptDocumentProps) {
  const cfg = data.config;
  const logoSrc = resolveClinicLogoUrl(data.clinica.logotipo_url);
  const metodoLabel =
    data.pagamento.metodo_label ||
    METODO_PAGAMENTO_LABEL[data.pagamento.metodo as MetodoPagamento] ||
    data.pagamento.metodo;

  const formatoClass =
    cfg.formato === "A5"
      ? "receipt-format-a5"
      : cfg.formato === "TERMICO_80"
        ? "receipt-format-termico_80"
        : "receipt-format-a4";

  return (
    <article
      className={`receipt-print-surface receipt-sauvida ${formatoClass} ${className}`.trim()}
      aria-label={`Recibo ${data.recibo.numero}`}
    >
      <header className="receipt-sauvida__header">
        <div className="receipt-sauvida__header-top">
          <div className="receipt-sauvida__brand-left">
            <img src={logoSrc} alt="" className="receipt-sauvida__clinic-logo" />
          </div>
          <div className="receipt-sauvida__brand-right">
            <img
              src={RECEIPT_BRANDING.nationalEmblem}
              alt=""
              className="receipt-sauvida__emblem"
              width={64}
              height={64}
            />
            <div className="receipt-sauvida__state-lines">
              <p className="receipt-sauvida__republica">{data.clinica.republica.toUpperCase()}</p>
              {data.clinica.mostrar_ministerio ? (
                <p className="receipt-sauvida__ministerio">MINISTÉRIO DA SAÚDE PÚBLICA</p>
              ) : null}
              <p className="receipt-sauvida__clinic-name">{data.clinica.nome.toUpperCase()}</p>
            </div>
          </div>
        </div>
        {(data.clinica.morada || data.clinica.telefone || data.clinica.email) && (
          <p className="receipt-sauvida__clinic-contacts">
            {[data.clinica.morada, data.clinica.telefone, data.clinica.email].filter(Boolean).join(" · ")}
          </p>
        )}

        <div className="receipt-sauvida__recibo-line">
          <h1 className="receipt-sauvida__recibo-title">RECIBO</h1>
          <p className="receipt-sauvida__recibo-number">
            N.º <span className="receipt-sauvida__num-seq">{data.recibo.numero_livro.sequencia}</span> /{" "}
            <span className="receipt-sauvida__num-ano">{data.recibo.numero_livro.ano}</span>
          </p>
          {data.recibo.tipo_documento === "SEGUNDA VIA" ? (
            <p className="receipt-sauvida__segunda-via">SEGUNDA VIA</p>
          ) : null}
        </div>
      </header>

      <section className="receipt-sauvida__body">
        <p className="receipt-sauvida__field">
          {data.textos.recebi_de}{" "}
          <span className="receipt-sauvida__fill">{data.paciente.nome}</span>
          {data.paciente.numero_processo ? (
            <span className="receipt-sauvida__muted"> (Proc. {data.paciente.numero_processo})</span>
          ) : null}
        </p>

        <p className="receipt-sauvida__field">
          {data.textos.importancia_de}{" "}
          <span className="receipt-sauvida__fill receipt-sauvida__amount">{formatFcfa(data.pagamento.valor)}</span>
          {data.pagamento.valor_extenso ? (
            <span className="receipt-sauvida__extenso"> ({data.pagamento.valor_extenso})</span>
          ) : null}
        </p>

        <p className="receipt-sauvida__field">
          {data.textos.referente_a}{" "}
          <span className="receipt-sauvida__fill">{data.referente_a}</span>
        </p>

        {cfg.mostrar_preco_oficial || cfg.mostrar_reducao ? (
          <table className="receipt-sauvida__table">
            <thead>
              <tr>
                <th>Serviço</th>
                {cfg.mostrar_preco_oficial ? <th>Oficial</th> : null}
                {cfg.mostrar_reducao ? <th>Redução</th> : null}
                <th>Cobrado</th>
              </tr>
            </thead>
            <tbody>
              {data.itens.map((it) => (
                <tr key={`${it.nome}-${it.subtotal_cobrado}`}>
                  <td>{it.nome}</td>
                  {cfg.mostrar_preco_oficial ? <td>{formatFcfa(it.preco_oficial)}</td> : null}
                  {cfg.mostrar_reducao ? <td>{formatFcfa(it.valor_reducao)}</td> : null}
                  <td>{formatFcfa(it.subtotal_cobrado)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : null}

        {cfg.mostrar_saldo ? (
          <p className="receipt-sauvida__totals">
            Total fatura: {formatFcfa(data.totais.total_cobrado)} · Pago (acum.):{" "}
            {formatFcfa(data.totais.total_pago)} · Saldo: {formatFcfa(data.totais.saldo)}
          </p>
        ) : null}

        <p className="receipt-sauvida__meta">
          Fatura {data.fatura.numero} · {metodoLabel}
        </p>
      </section>

      <footer className="receipt-sauvida__footer">
        <div className="receipt-sauvida__sign-row">
          <div className="receipt-sauvida__sign-block">
            <p className="receipt-sauvida__sign-label">{data.textos.exator}</p>
            <p className="receipt-sauvida__sign-name">{data.exator.nome || "—"}</p>
            <div className="receipt-sauvida__sign-line" aria-hidden />
          </div>
          <div className="receipt-sauvida__sign-block receipt-sauvida__date-block">
            <p className="receipt-sauvida__sign-label">{data.textos.data}</p>
            <p className="receipt-sauvida__date-value">
              {data.recibo.data_emissao.dia} / {data.recibo.data_emissao.mes} / {data.recibo.data_emissao.ano}
            </p>
          </div>
        </div>

        {data.clinica.mensagem_rodape ? (
          <p className="receipt-sauvida__footer-msg">{data.clinica.mensagem_rodape}</p>
        ) : null}
        <p className="receipt-sauvida__tagline">{RECEIPT_BRANDING.tagline}</p>
        <p className="receipt-sauvida__ref">{data.recibo.numero}</p>
      </footer>
    </article>
  );
}
