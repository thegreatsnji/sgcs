import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, Input, LoadingState, Modal, useToast } from "@/design-system";
import { usePermissions } from "@/hooks/usePermissions";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import {
  pharmacyService,
  type StockStatus,
  type UrgentMedicine,
} from "@/services/pharmacy/pharmacy.service";
import { getApiErrorMessage } from "@/utils/api-error";

const FILTERS = [
  { id: "todos", label: "Todos" },
  { id: "MEDICAMENTO", label: "Medicamentos" },
  { id: "MATERIAL_CLINICO", label: "Materiais" },
  { id: "TESTE_RAPIDO", label: "Testes rápidos" },
  { id: "STOCK_BAIXO", label: "Stock baixo" },
  { id: "SEM_STOCK", label: "Sem stock" },
];

function statusBadge(estado: StockStatus) {
  if (estado === "SEM_STOCK" || estado === "EXPIRADO") return <Badge variant="danger">{estado.replaceAll("_", " ")}</Badge>;
  if (estado === "STOCK_BAIXO" || estado === "PROXIMO_DA_VALIDADE")
    return <Badge variant="warning">{estado.replaceAll("_", " ")}</Badge>;
  return <Badge variant="success">Disponível</Badge>;
}

export function UrgentStockPage() {
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();
  const canMutate =
    hasPermission("stock.entry") || hasPermission("stock.exit") || hasPermission("pharmacy.edit");
  const canCreate = hasPermission("stock.create") || hasPermission("pharmacy.create");
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 250);
  const [filter, setFilter] = useState("todos");
  const [modal, setModal] = useState<"entrada" | "saida" | "novo" | null>(null);
  const [selected, setSelected] = useState<UrgentMedicine | null>(null);
  const [qty, setQty] = useState("1");
  const [note, setNote] = useState("");
  const [newItem, setNewItem] = useState({
    nome: "",
    forma_apresentacao: "",
    categoria: "MEDICAMENTO",
    unidade: "frasco",
    quantidade_inicial: "0",
    stock_minimo: "5",
  });

  const params = useMemo(() => {
    const categoria = ["MEDICAMENTO", "MATERIAL_CLINICO", "TESTE_RAPIDO"].includes(filter)
      ? filter
      : undefined;
    const estado = filter === "STOCK_BAIXO" || filter === "SEM_STOCK" ? filter : undefined;
    return {
      search: debouncedSearch || undefined,
      categoria,
      estado,
    };
  }, [debouncedSearch, filter]);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["stock-urgencia", params],
    queryFn: () => pharmacyService.listUrgentMedicines(params),
  });

  const dash = useQuery({
    queryKey: ["stock-urgencia-dash"],
    queryFn: pharmacyService.dashboard,
  });

  const invalidate = () => {
    void queryClient.invalidateQueries({ queryKey: ["stock-urgencia"] });
    void queryClient.invalidateQueries({ queryKey: ["stock-urgencia-dash"] });
  };

  const movement = useMutation({
    mutationFn: () =>
      pharmacyService.registerMovement(
        selected!.id,
        { quantidade: Math.max(1, Number(qty) || 1), motivo: note },
        modal === "saida" ? "saida" : "entrada",
      ),
    onSuccess: () => {
      showToast(modal === "saida" ? "Saída registada com sucesso." : "Entrada registada com sucesso.", "success");
      setModal(null);
      setNote("");
      invalidate();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const create = useMutation({
    mutationFn: () =>
      pharmacyService.createItem({
        ...newItem,
        quantidade_inicial: Number(newItem.quantidade_inicial) || 0,
        stock_minimo: Number(newItem.stock_minimo) || 0,
      }),
    onSuccess: () => {
      showToast("Item criado com sucesso.", "success");
      setModal(null);
      setNewItem({
        nome: "",
        forma_apresentacao: "",
        categoria: "MEDICAMENTO",
        unidade: "frasco",
        quantidade_inicial: "0",
        stock_minimo: "5",
      });
      invalidate();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const rows = data?.results ?? [];
  const preview = selected
    ? modal === "saida"
      ? Math.max(0, selected.quantidade_stock - (Number(qty) || 0))
      : selected.quantidade_stock + (Number(qty) || 0)
    : 0;

  if (isLoading) return <LoadingState message="A carregar stock de urgência…" />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold tracking-widest text-teal-800 uppercase">Enfermagem</p>
          <h1 className="text-2xl font-bold text-text">Stock de urgência</h1>
          <p className="mt-1 text-sm text-text-muted">
            Gestão simples de medicamentos e materiais de uso clínico. Não é farmácia comercial.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void refetch()}>
            Actualizar
          </Button>
          {canCreate ? (
            <Button variant="primary" onClick={() => setModal("novo")}>
              + Novo item
            </Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-4">
        {[
          ["Itens", dash.data?.total_itens ?? rows.length],
          ["Stock baixo", dash.data?.stock_baixo ?? 0],
          ["Sem stock", dash.data?.sem_stock ?? 0],
          ["Próximos da validade", dash.data?.proximos_validade ?? 0],
        ].map(([label, value]) => (
          <Card key={String(label)}>
            <p className="text-xs text-text-muted">{label}</p>
            <p className="text-2xl font-bold tabular-nums">{value}</p>
          </Card>
        ))}
      </div>

      <Input
        label="Pesquisar"
        placeholder="Pesquisar medicamento ou material…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`rounded-full px-3 py-1.5 text-sm font-medium ${
              filter === item.id ? "bg-teal-700 text-white" : "bg-surface-muted text-text"
            }`}
            onClick={() => setFilter(item.id)}
          >
            {item.label}
          </button>
        ))}
      </div>

      {isError ? (
        <p className="text-sm text-red-600">Não foi possível carregar o stock.</p>
      ) : rows.length === 0 ? (
        <Card>
          <p className="text-sm text-text-muted">Ainda não há itens. Crie o primeiro com “Novo item”.</p>
        </Card>
      ) : (
        <Card title={`Itens (${data?.count ?? 0})`}>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-text-muted uppercase">
                  <th className="py-2 pr-4">Nome</th>
                  <th className="py-2 pr-4">Apresentação</th>
                  <th className="py-2 pr-4">Qtd</th>
                  <th className="py-2 pr-4">Unidade</th>
                  <th className="py-2 pr-4">Mín.</th>
                  <th className="py-2 pr-4">Estado</th>
                  <th className="py-2 pr-4">Validade</th>
                  <th className="py-2">Acções</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={row.id} className="border-b border-border/60">
                    <td className="py-2.5 pr-4 font-medium">{row.nome}</td>
                    <td className="py-2.5 pr-4 text-text-muted">{row.forma_apresentacao || "—"}</td>
                    <td className="py-2.5 pr-4 tabular-nums font-semibold">{row.quantidade_stock}</td>
                    <td className="py-2.5 pr-4">{row.unidade}</td>
                    <td className="py-2.5 pr-4 tabular-nums">{row.stock_minimo}</td>
                    <td className="py-2.5 pr-4">{statusBadge(row.estado)}</td>
                    <td className="py-2.5 pr-4">{row.validade || "—"}</td>
                    <td className="py-2.5">
                      <div className="flex flex-wrap gap-1">
                        {canMutate ? (
                          <>
                            <Button
                              variant="secondary"
                              className="!px-2 !py-1 text-xs"
                              onClick={() => {
                                setSelected(row);
                                setQty("1");
                                setModal("saida");
                              }}
                            >
                              − Saída
                            </Button>
                            <Button
                              variant="primary"
                              className="!px-2 !py-1 text-xs"
                              onClick={() => {
                                setSelected(row);
                                setQty("1");
                                setModal("entrada");
                              }}
                            >
                              + Entrada
                            </Button>
                          </>
                        ) : null}
                        <Link to={`/stock/historico?item=${row.id}`} className="text-xs font-semibold text-teal-800">
                          Histórico
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Link to="/stock/historico" className="inline-block text-sm font-semibold text-teal-800">
        Ver todo o histórico →
      </Link>

      <Modal
        open={modal === "entrada" || modal === "saida"}
        title={modal === "saida" ? "Saída" : "Entrada"}
        onClose={() => setModal(null)}
      >
        {selected ? (
          <div className="space-y-3">
            <p className="font-medium">{selected.nome}</p>
            <p className="text-sm text-text-muted">
              Stock actual: <strong>{selected.quantidade_stock}</strong> {selected.unidade}
            </p>
            <Input label="Quantidade *" type="number" min={1} value={qty} onChange={(e) => setQty(e.target.value)} />
            <Input label="Observação (opcional)" value={note} onChange={(e) => setNote(e.target.value)} />
            <p className="text-sm">
              Novo stock: <strong>{preview}</strong>
            </p>
            <Button
              variant="primary"
              disabled={movement.isPending}
              onClick={() => movement.mutate()}
            >
              {modal === "saida" ? "Confirmar saída" : "Confirmar entrada"}
            </Button>
          </div>
        ) : null}
      </Modal>

      <Modal open={modal === "novo"} title="Novo item" onClose={() => setModal(null)}>
        <div className="grid gap-3">
          <Input label="Nome *" value={newItem.nome} onChange={(e) => setNewItem({ ...newItem, nome: e.target.value })} />
          <Input
            label="Apresentação"
            value={newItem.forma_apresentacao}
            onChange={(e) => setNewItem({ ...newItem, forma_apresentacao: e.target.value })}
          />
          <label className="text-sm">
            Categoria *
            <select
              className="mt-1 w-full rounded-lg border px-3 py-2"
              value={newItem.categoria}
              onChange={(e) => setNewItem({ ...newItem, categoria: e.target.value })}
            >
              <option value="MEDICAMENTO">Medicamento</option>
              <option value="MATERIAL_CLINICO">Material clínico</option>
              <option value="TESTE_RAPIDO">Teste rápido</option>
              <option value="OUTRO">Outro</option>
            </select>
          </label>
          <Input
            label="Unidade *"
            value={newItem.unidade}
            onChange={(e) => setNewItem({ ...newItem, unidade: e.target.value })}
          />
          <Input
            label="Quantidade inicial *"
            type="number"
            min={0}
            value={newItem.quantidade_inicial}
            onChange={(e) => setNewItem({ ...newItem, quantidade_inicial: e.target.value })}
          />
          <Input
            label="Stock mínimo"
            type="number"
            min={0}
            value={newItem.stock_minimo}
            onChange={(e) => setNewItem({ ...newItem, stock_minimo: e.target.value })}
          />
          <Button variant="primary" disabled={create.isPending || !newItem.nome} onClick={() => create.mutate()}>
            Guardar
          </Button>
        </div>
      </Modal>
    </div>
  );
}
