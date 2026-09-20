import { useQuery } from "@tanstack/react-query";
import { useSearchParams } from "react-router-dom";

import { Card, LoadingState } from "@/design-system";
import { pharmacyService } from "@/services/pharmacy/pharmacy.service";
import { formatDisplayDateTime } from "@/utils/date";

const TYPE_FILTERS = [
  { id: "", label: "Todos" },
  { id: "ENTRADA", label: "Entrada" },
  { id: "SAIDA", label: "Saída" },
  { id: "AJUSTE", label: "Ajuste" },
  { id: "PERDA_EXPIRACAO", label: "Perda / Expiração" },
];

export function UrgentStockHistoryPage() {
  const [params, setParams] = useSearchParams();
  const tipo = params.get("tipo") || "";
  const item = params.get("item");

  const { data, isLoading, isError } = useQuery({
    queryKey: ["stock-movements", tipo, item],
    queryFn: () =>
      pharmacyService.listMovements({
        tipo: tipo || undefined,
        medicamento: item ? Number(item) : undefined,
      }),
  });

  if (isLoading) return <LoadingState message="A carregar histórico…" />;

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Histórico de stock</h1>
        <p className="text-sm text-text-muted">Os movimentos não podem ser editados nem apagados.</p>
      </div>
      <div className="flex flex-wrap gap-2">
        {TYPE_FILTERS.map((itemFilter) => (
          <button
            key={itemFilter.id || "all"}
            type="button"
            className={`rounded-lg px-3 py-1.5 text-sm ${
              tipo === itemFilter.id ? "bg-teal-700 text-white" : "bg-surface-muted"
            }`}
            onClick={() => {
              const next = new URLSearchParams(params);
              if (itemFilter.id) next.set("tipo", itemFilter.id);
              else next.delete("tipo");
              setParams(next);
            }}
          >
            {itemFilter.label}
          </button>
        ))}
      </div>
      {isError ? (
        <p className="text-sm text-red-600">Não foi possível carregar o histórico.</p>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b text-left text-xs uppercase text-text-muted">
                  <th className="py-2 pr-3">Data</th>
                  <th className="py-2 pr-3">Item</th>
                  <th className="py-2 pr-3">Tipo</th>
                  <th className="py-2 pr-3">Qtd</th>
                  <th className="py-2 pr-3">Antes</th>
                  <th className="py-2 pr-3">Depois</th>
                  <th className="py-2 pr-3">Utilizador</th>
                  <th className="py-2 pr-3">Utente</th>
                  <th className="py-2">Obs.</th>
                </tr>
              </thead>
              <tbody>
                {(data?.results ?? []).map((row) => (
                  <tr key={row.id} className="border-b border-border/60">
                    <td className="py-2 pr-3 whitespace-nowrap">{formatDisplayDateTime(row.created_at)}</td>
                    <td className="py-2 pr-3">{row.medicamento_nome}</td>
                    <td className="py-2 pr-3">{row.tipo_label || row.tipo}</td>
                    <td className="py-2 pr-3 tabular-nums">{row.quantidade}</td>
                    <td className="py-2 pr-3 tabular-nums">{row.quantidade_antes}</td>
                    <td className="py-2 pr-3 tabular-nums">{row.quantidade_depois}</td>
                    <td className="py-2 pr-3">{row.operador_nome || "—"}</td>
                    <td className="py-2 pr-3">{row.paciente_nome || "—"}</td>
                    <td className="py-2">{row.motivo || "—"}</td>
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
