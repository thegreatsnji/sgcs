import { useQuery } from "@tanstack/react-query";

import { PrintDocument } from "@/components/print/PrintDocument";
import { billingService } from "@/services/billing/billing.service";
import { formatDisplayDateTime } from "@/utils/date";

export interface SauVidaReceiptPrintProps {
  receiptId: number;
  segundaVia?: boolean;
}

export function SauVidaReceiptPrint({ receiptId, segundaVia }: SauVidaReceiptPrintProps) {
  const { data, isLoading } = useQuery({
    queryKey: ["receipt-print", receiptId, segundaVia],
    queryFn: () => billingService.getReceiptPrint(receiptId, segundaVia),
  });

  if (isLoading || !data) {
    return <p className="text-sm text-slate-500">A preparar recibo…</p>;
  }

  const cfg = data.config;
  return (
    <PrintDocument
      clinicName={data.clinica.nome}
      title="Recibo"
      documentNumber={data.recibo.numero}
      documentDate={formatDisplayDateTime(data.recibo.emitido_em)}
      footerContacts={{
        phone: data.clinica.telefone,
        email: data.clinica.email,
        address: data.clinica.morada,
      }}
      signature={{ label: "Assinatura / Caixa" }}
      className={`receipt-sauvida receipt-format-${cfg.formato.toLowerCase()}`}
    >
      <p className="text-center text-xs text-slate-600">{data.clinica.republica}</p>
      {data.clinica.mostrar_ministerio ? (
        <p className="text-center text-xs text-slate-600">Ministério da Saúde Pública</p>
      ) : null}
      <p className="mt-2 text-center text-sm font-semibold">{data.recibo.tipo_documento}</p>

      <p className="mt-6 text-sm">
        {data.textos.recebi_de}{" "}
        <span className="font-semibold">{data.paciente.nome}</span>
        {data.paciente.numero_processo ? (
          <span className="text-slate-600"> (Proc. {data.paciente.numero_processo})</span>
        ) : null}
      </p>
      <p className="mt-2 text-sm">
        {data.textos.importancia_de}{" "}
        <span className="font-bold">{Number(data.pagamento.valor).toLocaleString("pt-PT")} FCFA</span>
        {data.pagamento.valor_extenso ? (
          <span className="block text-xs text-slate-600">({data.pagamento.valor_extenso})</span>
        ) : null}
      </p>
      <p className="mt-2 text-sm">
        {data.textos.referente_a}: {data.referente_a}
      </p>

      {cfg.mostrar_preco_oficial || cfg.mostrar_reducao ? (
        <table className="mt-4 w-full text-xs">
          <thead>
            <tr className="border-b text-left text-slate-500">
              <th>Serviço</th>
              {cfg.mostrar_preco_oficial ? <th>Oficial</th> : null}
              {cfg.mostrar_reducao ? <th>Redução</th> : null}
              <th>Cobrado</th>
            </tr>
          </thead>
          <tbody>
            {data.itens.map((it) => (
              <tr key={it.nome} className="border-b border-slate-100">
                <td>{it.nome}</td>
                {cfg.mostrar_preco_oficial ? <td>{it.preco_oficial}</td> : null}
                {cfg.mostrar_reducao ? <td>{it.valor_reducao}</td> : null}
                <td>{it.subtotal_cobrado}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : null}

      {cfg.mostrar_saldo ? (
        <p className="mt-4 text-sm">
          Total cobrado: {Number(data.totais.total_cobrado).toLocaleString("pt-PT")} FCFA — Pago:{" "}
          {Number(data.totais.total_pago).toLocaleString("pt-PT")} FCFA — Saldo:{" "}
          {Number(data.totais.saldo).toLocaleString("pt-PT")} FCFA
        </p>
      ) : null}

      <p className="mt-4 text-xs text-slate-600">
        Fatura {data.fatura.numero} — {data.pagamento.metodo}
      </p>
      {data.clinica.mensagem_rodape ? (
        <p className="mt-6 text-center text-xs text-slate-500">{data.clinica.mensagem_rodape}</p>
      ) : null}
    </PrintDocument>
  );
}
