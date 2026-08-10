import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { Badge, Button, Card, Input, LoadingState, useToast } from "@/design-system";
import { pharmacyService } from "@/services/pharmacy/pharmacy.service";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { getApiErrorMessage } from "@/utils/api-error";

export function UrgentStockPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 250);
  const [onlyLow, setOnlyLow] = useState(false);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [qty, setQty] = useState("1");
  const [motivo, setMotivo] = useState("");

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["pharmacy-urgent", debouncedSearch, onlyLow],
    queryFn: () =>
      pharmacyService.listUrgentMedicines({
        search: debouncedSearch || undefined,
        abaixo_minimo: onlyLow,
      }),
  });

  const movement = useMutation({
    mutationFn: ({ id, tipo }: { id: number; tipo: "ENTRADA" | "SAIDA" }) =>
      pharmacyService.registerMovement(id, {
        tipo,
        quantidade: Math.max(1, Number(qty) || 1),
        motivo,
      }),
    onSuccess: () => {
      showToast("Movimento registado.", "success");
      setMotivo("");
      void queryClient.invalidateQueries({ queryKey: ["pharmacy-urgent"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const rows = data?.results ?? [];
  const selected = useMemo(() => rows.find((r) => r.id === selectedId) ?? null, [rows, selectedId]);

  if (isLoading) return <LoadingState message="A carregar stock de urgência…" />;

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs font-semibold tracking-widest text-amber-700 uppercase">Farmácia</p>
        <h1 className="text-2xl font-bold text-text">Stock — medicamentos de urgência</h1>
        <p className="mt-1 text-sm text-text-muted">
          Gestão limitada ao stock para casos urgentes. Não inclui farmácia comercial nem dispensação
          ambulatória completa.
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <Input
          label="Pesquisar"
          placeholder="Código ou nome…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="min-w-[220px] flex-1"
        />
        <label className="flex items-end gap-2 pb-2 text-sm">
          <input
            type="checkbox"
            checked={onlyLow}
            onChange={(e) => setOnlyLow(e.target.checked)}
          />
          Só abaixo do mínimo
        </label>
        <Button variant="outline" onClick={() => void refetch()}>
          Actualizar
        </Button>
      </div>

      {isError ? (
        <p className="text-sm text-red-600">Não foi possível carregar o stock.</p>
      ) : (
        <Card title={`Medicamentos (${data?.count ?? 0})`}>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-text-muted uppercase">
                  <th className="py-2 pr-4">Código</th>
                  <th className="py-2 pr-4">Nome</th>
                  <th className="py-2 pr-4">Stock</th>
                  <th className="py-2 pr-4">Mín.</th>
                  <th className="py-2">Estado</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr
                    key={row.id}
                    className={`cursor-pointer border-b border-border/60 hover:bg-surface-muted/50 ${
                      selectedId === row.id ? "bg-primary-50/50" : ""
                    }`}
                    onClick={() => setSelectedId(row.id)}
                  >
                    <td className="py-2.5 pr-4 font-mono text-xs">{row.codigo}</td>
                    <td className="py-2.5 pr-4 font-medium">{row.nome}</td>
                    <td className="py-2.5 pr-4 tabular-nums">{row.quantidade_stock}</td>
                    <td className="py-2.5 pr-4 tabular-nums">{row.stock_minimo}</td>
                    <td className="py-2.5">
                      {row.abaixo_minimo ? (
                        <Badge variant="warning">Repor</Badge>
                      ) : (
                        <Badge variant="success">OK</Badge>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {selected && (
        <Card title={`Movimento — ${selected.nome}`}>
          <div className="grid gap-4 sm:grid-cols-3">
            <Input
              label="Quantidade"
              type="number"
              min={1}
              value={qty}
              onChange={(e) => setQty(e.target.value)}
            />
            <Input
              label="Motivo (opcional)"
              value={motivo}
              onChange={(e) => setMotivo(e.target.value)}
              className="sm:col-span-2"
            />
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Button
              variant="primary"
              disabled={movement.isPending}
              onClick={() => movement.mutate({ id: selected.id, tipo: "ENTRADA" })}
            >
              Entrada
            </Button>
            <Button
              variant="secondary"
              disabled={movement.isPending}
              onClick={() => movement.mutate({ id: selected.id, tipo: "SAIDA" })}
            >
              Saída (urgência)
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
