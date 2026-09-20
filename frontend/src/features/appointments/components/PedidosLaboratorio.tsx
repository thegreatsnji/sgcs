import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Badge, Button, Card, Table } from "@/design-system";
import { PRIORITY_LABELS } from "@/constants/appointments";
import { LAB_FATURACAO_LABELS } from "@/constants/laboratory";
import { appointmentsService } from "@/services/appointments";
import type { ExamOrder, LaboratoryCatalogItem } from "@/types/clinicalRecord";

interface PedidosLaboratorioProps {
  pedidos: ExamOrder[];
  disabled?: boolean;
  onAdd: (data: {
    tipo_exame?: string;
    servico_id?: number;
    prioridade?: string;
    observacoes?: string;
  }) => void | Promise<unknown>;
  isPending?: boolean;
}

export function PedidosLaboratorio({ pedidos, disabled, onAdd, isPending }: PedidosLaboratorioProps) {
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [query, setQuery] = useState("");
  const [prioridade, setPrioridade] = useState("NORMAL");
  const [observacoes, setObservacoes] = useState("");
  const [freeText, setFreeText] = useState("");

  const { data: catalog = [], isLoading: catalogLoading } = useQuery({
    queryKey: ["laboratory-catalog"],
    queryFn: () => appointmentsService.getLaboratoryCatalog(),
    staleTime: 60_000,
  });

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return catalog.slice(0, 40);
    return catalog
      .filter(
        (s) =>
          s.nome.toLowerCase().includes(q) || s.codigo.toLowerCase().includes(q),
      )
      .slice(0, 40);
  }, [catalog, query]);

  function toggleService(item: LaboratoryCatalogItem) {
    setSelectedIds((prev) =>
      prev.includes(item.id) ? prev.filter((id) => id !== item.id) : [...prev, item.id],
    );
  }

  async function emitSelected() {
    if (selectedIds.length === 0 && !freeText.trim()) return;
    for (const id of selectedIds) {
      await onAdd({
        servico_id: id,
        prioridade,
        observacoes: observacoes.trim() || undefined,
      });
    }
    if (freeText.trim()) {
      await onAdd({
        tipo_exame: freeText.trim(),
        prioridade,
        observacoes: observacoes.trim() || undefined,
      });
    }
    setSelectedIds([]);
    setFreeText("");
    setObservacoes("");
  }

  return (
    <div className="space-y-4">
      <Card title="Pedidos de laboratório">
        <p className="mb-3 text-sm text-slate-500">
          Os pedidos ficam a aguardar regularização na Receção. O utente paga o exame sem nova
          triagem; o laboratório só processa depois do pagamento.
        </p>
        <Table<ExamOrder>
          data={pedidos}
          getRowKey={(row) => row.id}
          emptyMessage="Nenhum pedido emitido nesta consulta."
          columns={[
            {
              key: "tipo_exame",
              header: "Exame",
              render: (row) => (
                <div>
                  <p className="font-medium text-slate-900">{row.tipo_exame}</p>
                  {row.servico_nome ? (
                    <p className="text-xs text-slate-500">{row.servico_nome}</p>
                  ) : null}
                </div>
              ),
            },
            {
              key: "prioridade",
              header: "Prioridade",
              render: (row) =>
                PRIORITY_LABELS[row.prioridade as keyof typeof PRIORITY_LABELS] ?? row.prioridade,
            },
            {
              key: "estado_faturacao",
              header: "Faturação",
              render: (row) => (
                <Badge
                  variant={row.estado_faturacao === "REGULARIZADO" ? "success" : "warning"}
                >
                  {row.estado_faturacao_label ??
                    (row.estado_faturacao
                      ? LAB_FATURACAO_LABELS[
                          row.estado_faturacao as keyof typeof LAB_FATURACAO_LABELS
                        ] ?? row.estado_faturacao
                      : row.estado)}
                </Badge>
              ),
            },
          ]}
        />
      </Card>

      {!disabled && (
        <Card title="Novo pedido">
          <div className="space-y-4">
            <p className="text-sm text-slate-600">
              Escolha exames do catálogo (sem preços). O utente regressa à Receção só para pagar.
            </p>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Pesquisar no catálogo
              </label>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Nome ou código…"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>

            {catalogLoading ? (
              <p className="text-sm text-slate-500">A carregar catálogo…</p>
            ) : filtered.length === 0 ? (
              <p className="text-sm text-amber-800">
                Nenhum exame no catálogo. Use texto livre abaixo ou peça à direcção para activar
                serviços LABORATORIO.
              </p>
            ) : (
              <ul className="max-h-56 space-y-1 overflow-y-auto rounded-xl border border-slate-200 p-2">
                {filtered.map((item) => {
                  const selected = selectedIds.includes(item.id);
                  return (
                    <li key={item.id}>
                      <label
                        className={[
                          "flex cursor-pointer items-center gap-2 rounded-lg px-2 py-2 text-sm",
                          selected ? "bg-primary-50 text-primary-900" : "hover:bg-slate-50",
                        ].join(" ")}
                      >
                        <input
                          type="checkbox"
                          checked={selected}
                          onChange={() => toggleService(item)}
                        />
                        <span className="min-w-0 flex-1">
                          <span className="font-medium">{item.nome}</span>
                          <span className="ml-2 font-mono text-xs text-slate-500">{item.codigo}</span>
                        </span>
                      </label>
                    </li>
                  );
                })}
              </ul>
            )}

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">
                Outro exame (texto livre)
              </label>
              <input
                value={freeText}
                onChange={(e) => setFreeText(e.target.value)}
                placeholder="Só se não estiver no catálogo"
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Prioridade</label>
              <select
                value={prioridade}
                onChange={(e) => setPrioridade(e.target.value)}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                {Object.entries(PRIORITY_LABELS).map(([v, l]) => (
                  <option key={v} value={v}>
                    {l}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-slate-700">Observações</label>
              <textarea
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                rows={2}
                className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
              />
            </div>

            <Button
              type="button"
              disabled={isPending || (selectedIds.length === 0 && !freeText.trim())}
              onClick={emitSelected}
            >
              {isPending
                ? "A emitir…"
                : selectedIds.length > 1
                  ? `Emitir ${selectedIds.length} pedidos`
                  : "Emitir pedido"}
            </Button>
            {selectedIds.length > 0 || freeText.trim() ? (
              <p className="text-xs text-emerald-800">
                Após emitir: estado «Aguarda regularização na Receção».
              </p>
            ) : null}
          </div>
        </Card>
      )}
    </div>
  );
}
