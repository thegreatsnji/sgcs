import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useSearchParams } from "react-router-dom";
import { useMemo } from "react";

import { Button, Card, ErrorState, Input, LoadingState, Table, useToast } from "@/design-system";
import { SERVICE_CATEGORY_OPTIONS, categoryLabel } from "@/constants/serviceCategories";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { usePermissions } from "@/hooks/usePermissions";
import { billingService } from "@/services/billing/billing.service";
import { settingsService } from "@/services/settings/settings.service";
import type { BillingService as BillingServiceType } from "@/types/billing";
import { getApiErrorMessage } from "@/utils/api-error";

const VALIDACAO_LABEL: Record<string, string> = {
  CONFIRMADO: "Confirmado",
  PENDENTE: "Pendente",
  NECESSITA_REVISAO: "Necessita revisão",
};

function validationLabel(code?: string) {
  if (!code) return "—";
  return VALIDACAO_LABEL[code] ?? code;
}

function exportCsv(rows: BillingServiceType[]) {
  const header = "codigo,nome,categoria,departamento,preco,estado,validacao\n";
  const body = rows
    .map((r) =>
      [
        r.codigo,
        `"${r.nome.replace(/"/g, '""')}"`,
        r.categoria,
        r.departamento_nome ?? "",
        r.preco,
        r.activo ? "Activo" : "Inactivo",
        r.estado_validacao ?? "",
      ].join(","),
    )
    .join("\n");
  const blob = new Blob([header + body], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "servicos-sauvida.csv";
  a.click();
  URL.revokeObjectURL(url);
}

export function ServicesListPage() {
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const { hasPermission } = usePermissions();
  const canEditCatalog = hasPermission("billing.delete");
  const [searchParams, setSearchParams] = useSearchParams();

  const search = searchParams.get("search") ?? "";
  const debouncedSearch = useDebouncedValue(search, 300);
  const categoria = searchParams.get("categoria") ?? "";
  const departamento = searchParams.get("departamento") ?? "";
  const especialidade = searchParams.get("especialidade") ?? "";
  const activo = searchParams.get("activo") ?? "";
  const estadoValidacao = searchParams.get("estado_validacao") ?? "";
  const semPreco = searchParams.get("sem_preco_confirmado") === "1";
  const ordering = searchParams.get("ordering") ?? "nome";
  const page = Number(searchParams.get("page") ?? "1");

  const queryParams = useMemo(
    () => ({
      search: debouncedSearch || undefined,
      categoria: categoria || undefined,
      departamento: departamento || undefined,
      especialidade: especialidade || undefined,
      activo: activo === "" ? undefined : activo === "1",
      estado_validacao: estadoValidacao || undefined,
      sem_preco_confirmado: semPreco || undefined,
      ordering,
      page,
      page_size: 25,
      include_excluded: true,
    }),
    [
      debouncedSearch,
      categoria,
      departamento,
      especialidade,
      activo,
      estadoValidacao,
      semPreco,
      ordering,
      page,
    ],
  );

  const { data: departments } = useQuery({
    queryKey: ["departments"],
    queryFn: settingsService.listDepartments,
  });
  const { data: specialties } = useQuery({
    queryKey: ["specialties"],
    queryFn: settingsService.listSpecialties,
  });

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["billing-services", queryParams],
    queryFn: () => billingService.listServices(queryParams),
  });

  const toggleMutation = useMutation({
    mutationFn: ({ id, activo: next }: { id: number; activo: boolean }) =>
      billingService.updateService(id, { activo: next }),
    onSuccess: () => {
      showToast("Serviço actualizado.", "success");
      void queryClient.invalidateQueries({ queryKey: ["billing-services"] });
    },
    onError: (e) => showToast(getApiErrorMessage(e), "error"),
  });

  function setFilter(key: string, value: string) {
    const next = new URLSearchParams(searchParams);
    if (value) next.set(key, value);
    else next.delete(key);
    if (key !== "page") next.set("page", "1");
    setSearchParams(next);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <h2 className="text-2xl font-bold text-slate-900">Serviços</h2>
        <div className="flex flex-wrap gap-2">
          {data?.results?.length ? (
            <Button variant="secondary" type="button" onClick={() => exportCsv(data.results)}>
              Exportar CSV
            </Button>
          ) : null}
          {canEditCatalog ? (
            <Link to="/billing/services/new">
              <Button variant="primary">Novo serviço</Button>
            </Link>
          ) : null}
        </div>
      </div>
      <BillingSubNav />

      <Card>
        <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Input
            label="Pesquisar"
            placeholder="Código ou nome"
            value={search}
            onChange={(e) => setFilter("search", e.target.value)}
          />
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Categoria</span>
            <select
              className="rounded-lg border border-border px-3 py-2"
              value={categoria}
              onChange={(e) => setFilter("categoria", e.target.value)}
            >
              <option value="">Todas</option>
              {SERVICE_CATEGORY_OPTIONS.map((c) => (
                <option key={c.value} value={c.value}>
                  {c.label}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Departamento</span>
            <select
              className="rounded-lg border border-border px-3 py-2"
              value={departamento}
              onChange={(e) => setFilter("departamento", e.target.value)}
            >
              <option value="">Todos</option>
              {departments?.results.map((d) => (
                <option key={d.id} value={String(d.id)}>
                  {d.nome}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Especialidade</span>
            <select
              className="rounded-lg border border-border px-3 py-2"
              value={especialidade}
              onChange={(e) => setFilter("especialidade", e.target.value)}
            >
              <option value="">Todas</option>
              {specialties?.results.map((s) => (
                <option key={s.id} value={String(s.id)}>
                  {s.nome}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Estado</span>
            <select
              className="rounded-lg border border-border px-3 py-2"
              value={activo}
              onChange={(e) => setFilter("activo", e.target.value)}
            >
              <option value="">Todos</option>
              <option value="1">Activos</option>
              <option value="0">Inactivos</option>
            </select>
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Validação de preço</span>
            <select
              className="rounded-lg border border-border px-3 py-2"
              value={estadoValidacao}
              onChange={(e) => setFilter("estado_validacao", e.target.value)}
            >
              <option value="">Todas</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="PENDENTE">Pendente</option>
              <option value="NECESSITA_REVISAO">Necessita revisão</option>
            </select>
          </label>
          <label className="flex items-center gap-2 text-sm sm:col-span-2">
            <input
              type="checkbox"
              checked={semPreco}
              onChange={(e) => setFilter("sem_preco_confirmado", e.target.checked ? "1" : "")}
            />
            Apenas sem preço confirmado
          </label>
          <label className="flex flex-col gap-1 text-sm">
            <span className="font-medium text-slate-700">Ordenar</span>
            <select
              className="rounded-lg border border-border px-3 py-2"
              value={ordering}
              onChange={(e) => setFilter("ordering", e.target.value)}
            >
              <option value="nome">Nome</option>
              <option value="-nome">Nome (Z–A)</option>
              <option value="preco">Preço</option>
              <option value="-preco">Preço (desc)</option>
              <option value="departamento">Departamento</option>
            </select>
          </label>
        </div>

        {isLoading || !data ? (
          <LoadingState />
        ) : isError ? (
          <ErrorState onRetry={() => void refetch()} message="Erro ao carregar serviços." />
        ) : (
          <>
            <Table<BillingServiceType>
              data={data.results}
              getRowKey={(r) => r.id}
              columns={[
                { key: "codigo", header: "Código" },
                { key: "nome", header: "Serviço" },
                {
                  key: "categoria",
                  header: "Categoria",
                  render: (r) => categoryLabel(r.categoria),
                },
                { key: "departamento_nome", header: "Departamento", render: (r) => r.departamento_nome ?? "—" },
                {
                  key: "especialidade_nome",
                  header: "Especialidade",
                  render: (r) => r.especialidade_nome ?? "—",
                },
                {
                  key: "preco",
                  header: "Preço",
                  render: (r) =>
                    r.preco_confirmado ? `${Number(r.preco).toLocaleString("pt-PT")} FCFA` : "Pendente",
                },
                {
                  key: "activo",
                  header: "Estado",
                  render: (r) => (r.activo ? "Activo" : "Inactivo"),
                },
                {
                  key: "estado_validacao",
                  header: "Validação",
                  render: (r) => validationLabel(r.estado_validacao),
                },
                {
                  key: "updated_at",
                  header: "Última alteração",
                  render: (r) => (r.updated_at ? new Date(r.updated_at).toLocaleString("pt-PT") : "—"),
                },
                {
                  key: "actions",
                  header: "Acções",
                  render: (r) => (
                    <div className="flex flex-wrap gap-2">
                      <Link to={`/billing/services/${r.id}`} className="text-primary-600 hover:underline text-sm">
                        Detalhes
                      </Link>
                      {canEditCatalog ? (
                        <>
                          <Link to={`/billing/services/${r.id}/edit`} className="text-primary-600 hover:underline text-sm">
                            Editar
                          </Link>
                          <button
                            type="button"
                            className="text-sm text-slate-600 hover:underline"
                            onClick={() => toggleMutation.mutate({ id: r.id, activo: !r.activo })}
                          >
                            {r.activo ? "Desactivar" : "Activar"}
                          </button>
                        </>
                      ) : null}
                    </div>
                  ),
                },
              ]}
            />
            {data.count > 25 ? (
              <div className="mt-4 flex justify-between text-sm">
                <span>
                  Página {page}: {data.count} serviços
                </span>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={!data.previous}
                    onClick={() => setFilter("page", String(Math.max(1, page - 1)))}
                  >
                    Anterior
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={!data.next}
                    onClick={() => setFilter("page", String(page + 1))}
                  >
                    Seguinte
                  </Button>
                </div>
              </div>
            ) : null}
          </>
        )}
      </Card>
    </div>
  );
}
