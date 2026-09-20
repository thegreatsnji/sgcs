import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { isAxiosError } from "axios";
import { useEffect, useMemo, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";

import { Badge, Button, Card, Input, LoadingState, Modal, useToast } from "@/design-system";
import { usePermissions } from "@/hooks/usePermissions";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import {
  pharmacyService,
  type StockStatus,
  type UrgentMedicine,
} from "@/services/pharmacy/pharmacy.service";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate } from "@/utils/date";

const FILTERS = [
  { id: "todos", label: "Todos" },
  { id: "MEDICAMENTO", label: "Medicamentos" },
  { id: "MATERIAL_CLINICO", label: "Materiais" },
  { id: "TESTE_RAPIDO", label: "Testes rápidos" },
  { id: "STOCK_BAIXO", label: "Stock baixo" },
  { id: "SEM_STOCK", label: "Sem stock" },
  { id: "PROXIMO_DA_VALIDADE", label: "Próximo da validade" },
  { id: "EXPIRADO", label: "Expirado" },
];

const PERDA_MOTIVOS = [
  { id: "EXPIRADO", label: "Expirado" },
  { id: "DANIFICADO", label: "Danificado" },
  { id: "PERDIDO", label: "Perdido" },
  { id: "OUTRO", label: "Outro" },
];

type ModalKind = "entrada" | "saida" | "ajuste" | "perda" | "novo" | "inicial" | null;

function statusBadge(estado: StockStatus): { label: string; variant: "success" | "warning" | "danger" } {
  if (estado === "EXPIRADO") return { label: "Expirado", variant: "danger" };
  if (estado === "SEM_STOCK") return { label: "Sem stock", variant: "danger" };
  if (estado === "PROXIMO_DA_VALIDADE") return { label: "Próximo da validade", variant: "warning" };
  if (estado === "STOCK_BAIXO") return { label: "Stock baixo", variant: "warning" };
  return { label: "Normal", variant: "success" };
}

export function UrgentStockPage() {
  const { showToast } = useToast();
  const { hasPermission } = usePermissions();
  const [searchParams] = useSearchParams();
  const canMutate =
    hasPermission("stock.entry") || hasPermission("stock.exit") || hasPermission("pharmacy.edit");
  const canAdjust = hasPermission("stock.adjust") || hasPermission("pharmacy.edit");
  const canCreate = hasPermission("stock.create") || hasPermission("pharmacy.create");
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search, 250);
  const estadoFromUrl = searchParams.get("estado") || "";
  const initialFilter = FILTERS.some((f) => f.id === estadoFromUrl) ? estadoFromUrl : "todos";
  const [filter, setFilter] = useState(initialFilter);

  useEffect(() => {
    if (FILTERS.some((f) => f.id === estadoFromUrl)) {
      setFilter(estadoFromUrl);
    }
  }, [estadoFromUrl]);
  const [modal, setModal] = useState<ModalKind>(null);
  const [selected, setSelected] = useState<UrgentMedicine | null>(null);
  const [qty, setQty] = useState("1");
  const [note, setNote] = useState("");
  const [perdaMotivo, setPerdaMotivo] = useState("EXPIRADO");
  const [initialForm, setInitialForm] = useState({ quantidade: "", stock_minimo: "5", validade: "", unidade: "" });
  const [newItem, setNewItem] = useState({
    nome: "",
    forma_apresentacao: "",
    categoria: "MEDICAMENTO",
    unidade: "frasco",
    quantidade_inicial: "0",
    stock_minimo: "5",
    validade: "",
  });
  const [duplicateHint, setDuplicateHint] = useState<{ id: number; codigo: string } | null>(null);

  const params = useMemo(() => {
    const categoria = ["MEDICAMENTO", "MATERIAL_CLINICO", "TESTE_RAPIDO"].includes(filter)
      ? filter
      : undefined;
    const estado = ["STOCK_BAIXO", "SEM_STOCK", "EXPIRADO", "PROXIMO_DA_VALIDADE"].includes(filter)
      ? filter
      : undefined;
    return { search: debouncedSearch || undefined, categoria, estado };
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
    void queryClient.invalidateQueries({ queryKey: ["stock-urgencia-dash-nurse"] });
  };

  const movementKind =
    modal === "saida" ? "saida" : modal === "ajuste" ? "ajuste" : modal === "perda" ? "perda" : "entrada";

  const movement = useMutation({
    mutationFn: () => {
      const quantidade = Number(qty) || 0;
      const motivo =
        modal === "perda" ? (perdaMotivo === "OUTRO" ? note || "Outro" : perdaMotivo) : note;
      return pharmacyService.registerMovement(selected!.id, { quantidade, motivo }, movementKind);
    },
    onSuccess: () => {
      const labels: Record<string, string> = {
        saida: "Saída registada com sucesso.",
        ajuste: "Ajuste registado com sucesso.",
        perda: "Perda / expiração registada.",
        entrada: "Entrada registada com sucesso.",
      };
      showToast(labels[movementKind] ?? "Movimento registado.", "success");
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
        validade: newItem.validade || undefined,
      }),
    onSuccess: () => {
      showToast("Item criado com sucesso.", "success");
      setModal(null);
      setDuplicateHint(null);
      setNewItem({
        nome: "",
        forma_apresentacao: "",
        categoria: "MEDICAMENTO",
        unidade: "frasco",
        quantidade_inicial: "0",
        stock_minimo: "5",
        validade: "",
      });
      invalidate();
    },
    onError: (e) => {
      if (isAxiosError(e)) {
        const errors = e.response?.data?.errors as { existing_id?: number; existing_codigo?: string } | undefined;
        if (errors?.existing_id) {
          setDuplicateHint({ id: errors.existing_id, codigo: String(errors.existing_codigo ?? "") });
        }
      }
      showToast(getApiErrorMessage(e), "error");
    },
  });

  const defineInitial = useMutation({
    mutationFn: () =>
      pharmacyService.defineInitialStock(selected!.id, {
        quantidade: Number(initialForm.quantidade) || 0,
        stock_minimo: Number(initialForm.stock_minimo) || 0,
        validade: initialForm.validade || undefined,
        unidade: initialForm.unidade || undefined,
      }),
    onSuccess: () => {
      showToast("Stock inicial definido.", "success");
      setModal(null);
      invalidate();
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  const rows = data?.results ?? [];
  const qtyNum = Number(qty) || 0;
  const preview = selected
    ? modal === "saida" || modal === "perda"
      ? Math.max(0, selected.quantidade_stock - qtyNum)
      : modal === "ajuste"
        ? qtyNum
        : selected.quantidade_stock + qtyNum
    : 0;
  const ajusteDiff = selected && modal === "ajuste" ? qtyNum - selected.quantidade_stock : 0;

  const openModal = (kind: ModalKind, row: UrgentMedicine) => {
    setSelected(row);
    setQty(kind === "ajuste" ? String(row.quantidade_stock) : "1");
    setNote("");
    setPerdaMotivo("EXPIRADO");
    setInitialForm({
      quantidade: "",
      stock_minimo: String(row.stock_minimo),
      validade: row.validade ? row.validade.slice(0, 10) : "",
      unidade: row.unidade,
    });
    setModal(kind);
  };

  if (isLoading) return <LoadingState message="A carregar stock de urgência…" />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold tracking-widest text-teal-800 uppercase">Enfermagem</p>
          <h1 className="text-2xl font-bold text-text">Stock de urgência</h1>
          <p className="mt-1 text-sm text-text-muted">
            Medicamentos e materiais de uso clínico. Não é farmácia comercial.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void refetch()}>
            Actualizar
          </Button>
          {canCreate ? (
            <Button variant="primary" onClick={() => { setDuplicateHint(null); setModal("novo"); }}>
              Novo item
            </Button>
          ) : null}
        </div>
      </div>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
        {[
          ["Itens", dash.data?.total_itens ?? rows.length],
          ["Stock baixo", dash.data?.stock_baixo ?? 0],
          ["Sem stock", dash.data?.sem_stock ?? 0],
          ["Próximos da validade", dash.data?.proximos_validade ?? 0],
          ["Expirados", dash.data?.expirados ?? 0],
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
        autoFocus
      />

      <div className="flex flex-wrap gap-2">
        {FILTERS.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`rounded-lg px-3 py-1.5 text-sm font-medium ${
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
          <p className="text-sm text-text-muted">Ainda não há itens. Crie o primeiro com «Novo item».</p>
        </Card>
      ) : (
        <Card title={`Itens (${data?.count ?? 0})`}>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr className="border-b border-border text-left text-xs text-text-muted uppercase">
                  <th className="py-2 pr-4">Nome</th>
                  <th className="py-2 pr-4">Quantidade</th>
                  <th className="py-2 pr-4">Unidade</th>
                  <th className="py-2 pr-4">Validade</th>
                  <th className="py-2 pr-4">Estado</th>
                  <th className="py-2">Acções</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => {
                  const expired = row.estado === "EXPIRADO";
                  const badge = statusBadge(row.estado);
                  return (
                    <tr key={row.id} className="border-b border-border/60">
                      <td className="py-2.5 pr-4 font-medium">
                        {row.nome}
                        {row.stock_inicial_por_confirmar ? (
                          <span className="mt-0.5 block text-xs font-normal text-amber-800">
                            Stock inicial por confirmar
                          </span>
                        ) : null}
                      </td>
                      <td className="py-2.5 pr-4 tabular-nums font-semibold">{row.quantidade_stock}</td>
                      <td className="py-2.5 pr-4">{row.unidade}</td>
                      <td className="py-2.5 pr-4">{row.validade ? formatDisplayDate(row.validade) : "—"}</td>
                      <td className="py-2.5 pr-4">
                        <Badge variant={badge.variant}>{badge.label}</Badge>
                      </td>
                      <td className="py-2.5">
                        <div className="flex flex-wrap items-center gap-1">
                          {canMutate ? (
                            <>
                              <Button
                                variant="secondary"
                                className="!px-2 !py-1 text-xs"
                                disabled={expired}
                                title={expired ? "Este item está expirado e não pode ser utilizado." : undefined}
                                onClick={() => openModal("saida", row)}
                              >
                                Saída
                              </Button>
                              <Button
                                variant="primary"
                                className="!px-2 !py-1 text-xs"
                                onClick={() => openModal("entrada", row)}
                              >
                                Entrada
                              </Button>
                            </>
                          ) : null}
                          {canAdjust ? (
                            <>
                              <Button
                                variant="outline"
                                className="!px-2 !py-1 text-xs"
                                onClick={() => openModal("ajuste", row)}
                              >
                                Ajustar
                              </Button>
                              <Button
                                variant="outline"
                                className="!px-2 !py-1 text-xs"
                                onClick={() => openModal("perda", row)}
                              >
                                Perda
                              </Button>
                            </>
                          ) : null}
                          {row.stock_inicial_por_confirmar && canAdjust ? (
                            <Button
                              variant="outline"
                              className="!px-2 !py-1 text-xs"
                              onClick={() => openModal("inicial", row)}
                            >
                              Definir stock inicial
                            </Button>
                          ) : null}
                          <Link
                            to={`/stock/historico?item=${row.id}`}
                            className="text-xs font-semibold text-teal-800"
                          >
                            Histórico
                          </Link>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      <Link to="/stock/historico" className="inline-block text-sm font-semibold text-teal-800">
        Ver todo o histórico
      </Link>

      <Modal
        open={modal === "entrada" || modal === "saida"}
        title={modal === "saida" ? "Saída" : "Entrada"}
        onClose={() => setModal(null)}
      >
        {selected ? (
          <div className="space-y-3">
            <p className="font-medium">{selected.nome}</p>
            {modal === "saida" && selected.estado === "EXPIRADO" ? (
              <p className="text-sm text-red-600">Este item está expirado e não pode ser utilizado.</p>
            ) : (
              <>
                <p className="text-sm text-text-muted">
                  Antes: <strong>{selected.quantidade_stock}</strong> {selected.unidade}
                </p>
                <Input
                  label="Quantidade *"
                  type="number"
                  min={1}
                  max={modal === "saida" ? selected.quantidade_stock : undefined}
                  value={qty}
                  onChange={(e) => setQty(e.target.value)}
                  autoFocus
                />
                <Input label="Observação (opcional)" value={note} onChange={(e) => setNote(e.target.value)} />
                {modal === "saida" && qtyNum > selected.quantidade_stock ? (
                  <p className="text-sm text-red-600">Não há quantidade suficiente.</p>
                ) : (
                  <p className="text-sm">
                    {modal === "saida" ? "Saída" : "Entrada"}: <strong>{qtyNum}</strong>
                    {" · "}
                    Depois: <strong>{preview}</strong>
                  </p>
                )}
                <Button
                  variant="primary"
                  disabled={
                    movement.isPending ||
                    qtyNum < 1 ||
                    (modal === "saida" && qtyNum > selected.quantidade_stock)
                  }
                  onClick={() => movement.mutate()}
                >
                  {modal === "saida" ? "Confirmar saída" : "Confirmar entrada"}
                </Button>
              </>
            )}
          </div>
        ) : null}
      </Modal>

      <Modal open={modal === "ajuste"} title="Ajustar stock" onClose={() => setModal(null)}>
        {selected ? (
          <div className="space-y-3">
            <p className="font-medium">{selected.nome}</p>
            <p className="text-sm">
              Quantidade no sistema: <strong>{selected.quantidade_stock}</strong> {selected.unidade}
            </p>
            <Input
              label="Nova quantidade física *"
              type="number"
              min={0}
              value={qty}
              onChange={(e) => setQty(e.target.value)}
              autoFocus
            />
            <p className="text-sm">
              Diferença:{" "}
              <strong>
                {ajusteDiff > 0 ? "+" : ""}
                {ajusteDiff}
              </strong>
            </p>
            <Input
              label="Motivo *"
              value={note}
              onChange={(e) => setNote(e.target.value)}
              placeholder="Contagem física"
            />
            <Button
              variant="primary"
              disabled={movement.isPending || qtyNum < 0 || !note.trim()}
              onClick={() => movement.mutate()}
            >
              Confirmar ajuste
            </Button>
          </div>
        ) : null}
      </Modal>

      <Modal open={modal === "perda"} title="Perda / expiração" onClose={() => setModal(null)}>
        {selected ? (
          <div className="space-y-3">
            <p className="font-medium">{selected.nome}</p>
            <p className="text-sm text-text-muted">
              Stock actual: <strong>{selected.quantidade_stock}</strong> {selected.unidade}
            </p>
            <Input
              label="Quantidade *"
              type="number"
              min={1}
              max={selected.quantidade_stock}
              value={qty}
              onChange={(e) => setQty(e.target.value)}
              autoFocus
            />
            <label className="text-sm">
              Motivo *
              <select
                className="mt-1 w-full rounded-lg border px-3 py-2"
                value={perdaMotivo}
                onChange={(e) => setPerdaMotivo(e.target.value)}
              >
                {PERDA_MOTIVOS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </label>
            <Input
              label="Observação (opcional)"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
            <p className="text-sm">
              Depois: <strong>{preview}</strong>
            </p>
            <Button
              variant="primary"
              disabled={movement.isPending || qtyNum < 1 || qtyNum > selected.quantidade_stock}
              onClick={() => movement.mutate()}
            >
              Confirmar perda
            </Button>
          </div>
        ) : null}
      </Modal>

      <Modal open={modal === "inicial"} title="Definir stock inicial" onClose={() => setModal(null)}>
        {selected ? (
          <div className="space-y-3">
            <p className="font-medium">{selected.nome}</p>
            <p className="text-sm text-text-muted">Cria um movimento de entrada. A quantidade não é editada directamente.</p>
            <Input
              label="Quantidade actual *"
              type="number"
              min={1}
              value={initialForm.quantidade}
              onChange={(e) => setInitialForm({ ...initialForm, quantidade: e.target.value })}
            />
            <Input
              label="Unidade"
              value={initialForm.unidade}
              onChange={(e) => setInitialForm({ ...initialForm, unidade: e.target.value })}
            />
            <Input
              label="Stock mínimo"
              type="number"
              min={0}
              value={initialForm.stock_minimo}
              onChange={(e) => setInitialForm({ ...initialForm, stock_minimo: e.target.value })}
            />
            <Input
              label="Validade (opcional)"
              type="date"
              value={initialForm.validade}
              onChange={(e) => setInitialForm({ ...initialForm, validade: e.target.value })}
            />
            <Button
              variant="primary"
              disabled={defineInitial.isPending || Number(initialForm.quantidade) < 1}
              onClick={() => defineInitial.mutate()}
            >
              Confirmar stock inicial
            </Button>
          </div>
        ) : null}
      </Modal>

      <Modal
        open={modal === "novo"}
        title="Novo item"
        onClose={() => {
          setModal(null);
          setDuplicateHint(null);
        }}
      >
        <div className="grid gap-3">
          {duplicateHint ? (
            <p className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-950">
              Já existe um item semelhante ({duplicateHint.codigo}).
              <button
                type="button"
                className="ml-2 font-semibold underline"
                onClick={() => {
                  setSearch(newItem.nome);
                  setModal(null);
                  setDuplicateHint(null);
                }}
              >
                Abrir o item existente
              </button>
            </p>
          ) : null}
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
            label="Quantidade inicial"
            type="number"
            min={0}
            hint="0 = stock inicial por confirmar"
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
          <Input
            label="Validade (opcional)"
            type="date"
            value={newItem.validade}
            onChange={(e) => setNewItem({ ...newItem, validade: e.target.value })}
          />
          <Button variant="primary" disabled={create.isPending || !newItem.nome} onClick={() => create.mutate()}>
            Guardar
          </Button>
        </div>
      </Modal>
    </div>
  );
}
