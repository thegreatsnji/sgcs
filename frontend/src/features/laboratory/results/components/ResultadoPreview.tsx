import { Card } from "@/design-system";
import { INTERPRETACAO_LABELS } from "@/constants/laboratoryResults";
import type { LaboratoryResult } from "@/types/laboratoryResult";
import { formatDisplayDateTime } from "@/utils/date";
import { ResultadoStatusBadge } from "./ResultadoStatusBadge";

interface ResultadoPreviewProps {
  resultado: LaboratoryResult;
}

export function ResultadoPreview({ resultado }: ResultadoPreviewProps) {
  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 className="text-lg font-semibold text-slate-900">{resultado.numero_pedido}</h3>
          <p className="text-sm text-slate-500">{resultado.paciente_nome}</p>
        </div>
        <ResultadoStatusBadge status={resultado.estado} />
      </div>

      <dl className="grid gap-2 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-slate-500">Responsável</dt>
          <dd>{resultado.responsavel_nome ?? "—"}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Data do resultado</dt>
          <dd>{resultado.data_resultado ? formatDisplayDateTime(resultado.data_resultado) : "—"}</dd>
        </div>
        {resultado.data_validacao && (
          <div>
            <dt className="text-slate-500">Validado em</dt>
            <dd>{formatDisplayDateTime(resultado.data_validacao)}</dd>
          </div>
        )}
        {resultado.validado_por_nome && (
          <div>
            <dt className="text-slate-500">Validado por</dt>
            <dd>{resultado.validado_por_nome}</dd>
          </div>
        )}
      </dl>

      {resultado.conclusao && (
        <Card title="Conclusão">
          <p className="text-sm text-slate-700">{resultado.conclusao}</p>
        </Card>
      )}

      {resultado.parametros.length > 0 && (
        <Card title="Parâmetros">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-500">
                  <th className="py-2 pr-4">Parâmetro</th>
                  <th className="py-2 pr-4">Valor</th>
                  <th className="py-2 pr-4">Referência</th>
                  <th className="py-2">Interpretação</th>
                </tr>
              </thead>
              <tbody>
                {resultado.parametros.map((p) => (
                  <tr key={p.id ?? p.nome} className="border-b border-slate-100">
                    <td className="py-2 pr-4">{p.nome}</td>
                    <td className="py-2 pr-4">
                      {p.valor} {p.unidade}
                    </td>
                    <td className="py-2 pr-4">
                      {p.valor_minimo && p.valor_maximo
                        ? `${p.valor_minimo} - ${p.valor_maximo}`
                        : "—"}
                    </td>
                    <td className="py-2">
                      {INTERPRETACAO_LABELS[p.interpretacao] ?? p.interpretacao}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
}
