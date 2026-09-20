import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";

import { Button, Card, ErrorState, LoadingState, Table } from "@/design-system";
import { categoryLabel } from "@/constants/serviceCategories";
import { BillingSubNav } from "@/features/billing/components/BillingSubNav";
import { usePermissions } from "@/hooks/usePermissions";
import { billingService } from "@/services/billing/billing.service";
import { getApiErrorMessage } from "@/utils/api-error";

export interface PriceHistoryRow {
  id: number;
  preco_anterior: string;
  preco_novo: string;
  motivo: string;
  origem: string;
  alterado_por_nome: string | null;
  created_at: string;
}

export function ServiceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const serviceId = Number(id);
  const { hasPermission } = usePermissions();
  const canEdit = hasPermission("billing.delete");

  const { data: service, isLoading, isError, error, refetch } = useQuery({
    queryKey: ["billing-service", serviceId],
    queryFn: () => billingService.getService(serviceId),
    enabled: Number.isFinite(serviceId),
  });

  const { data: history } = useQuery({
    queryKey: ["billing-service-history", serviceId],
    queryFn: () => billingService.getServicePriceHistory(serviceId),
    enabled: Number.isFinite(serviceId) && !!service,
  });

  if (isLoading) return <LoadingState />;
  if (isError || !service) {
    return (
      <ErrorState
        message={getApiErrorMessage(error) || "Serviço não encontrado."}
        onRetry={() => void refetch()}
      />
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{service.nome}</h2>
          <p className="text-sm text-slate-600">{service.codigo}</p>
        </div>
        <div className="flex gap-2">
          <Link to="/billing/services">
            <Button variant="ghost">Voltar</Button>
          </Link>
          {canEdit ? (
            <Link to={`/billing/services/${service.id}/edit`}>
              <Button variant="primary">Editar</Button>
            </Link>
          ) : null}
        </div>
      </div>
      <BillingSubNav />

      <Card title="Detalhes">
        <dl className="grid gap-3 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-slate-500">Categoria</dt>
            <dd className="font-medium">{categoryLabel(service.categoria)}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Departamento</dt>
            <dd className="font-medium">{service.departamento_nome ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Especialidade</dt>
            <dd className="font-medium">{service.especialidade_nome ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Preço oficial</dt>
            <dd className="font-medium">
              {service.preco_confirmado
                ? `${Number(service.preco).toLocaleString("pt-PT")} ${service.moeda ?? "FCFA"}`
                : "Pendente de confirmação"}
            </dd>
          </div>
          <div>
            <dt className="text-slate-500">Validação</dt>
            <dd className="font-medium">{service.estado_validacao ?? "—"}</dd>
          </div>
          <div>
            <dt className="text-slate-500">Estado</dt>
            <dd className="font-medium">{service.activo ? "Activo" : "Inactivo"}</dd>
          </div>
          {service.descricao ? (
            <div className="sm:col-span-2">
              <dt className="text-slate-500">Descrição</dt>
              <dd>{service.descricao}</dd>
            </div>
          ) : null}
        </dl>
      </Card>

      <Card title="Histórico de preços">
        {!history?.length ? (
          <p className="text-sm text-slate-500">Sem alterações registadas.</p>
        ) : (
          <Table<PriceHistoryRow>
            data={history}
            getRowKey={(r) => r.id}
            columns={[
              {
                key: "created_at",
                header: "Data",
                render: (r) => new Date(r.created_at).toLocaleString("pt-PT"),
              },
              { key: "preco_anterior", header: "Anterior", render: (r) => `${r.preco_anterior} FCFA` },
              { key: "preco_novo", header: "Novo", render: (r) => `${r.preco_novo} FCFA` },
              { key: "origem", header: "Origem" },
              { key: "alterado_por_nome", header: "Por", render: (r) => r.alterado_por_nome ?? "—" },
              { key: "motivo", header: "Motivo" },
            ]}
          />
        )}
      </Card>
    </div>
  );
}
