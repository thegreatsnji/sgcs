import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
import { IconLab } from "@/components/icons";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card, ErrorState, SkeletonCard } from "@/design-system";
import { laboratoryService } from "@/services/laboratory";

export function LaboratoryRoleDashboardPage() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-dashboard"],
    queryFn: laboratoryService.getDashboard,
    refetchInterval: 30_000,
  });

  const { data: pending } = useQuery({
    queryKey: ["laboratory-pending-preview"],
    queryFn: () => laboratoryService.getPending({ page: 1 }),
  });

  if (isLoading || !data) {
    return (
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonCard key={i} />
        ))}
      </div>
    );
  }

  if (isError) {
    return <ErrorState message="Não foi possível carregar o painel laboratorial." onRetry={() => void refetch()} />;
  }

  return (
    <div className="space-y-6">
      <RoleDashboardHero
        tone="amber"
        eyebrow="Laboratório diagnóstico"
        title="Painel laboratorial"
        description="Pedidos pendentes, colheitas e validação de resultados."
        primaryAction={{ to: "/laboratory/pending", label: "Pedidos pendentes" }}
        secondaryAction={{ to: "/laboratory/results", label: "Resultados" }}
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <KpiCard label="Pendentes" value={data.indicadores.pedidos_pendentes} badge={{ text: "Aguardam receção", variant: "warning" }} icon={<IconLab />} />
        <KpiCard label="Em Processamento" value={data.indicadores.em_processamento} badge={{ text: "Activos", variant: "info" }} />
        <KpiCard label="Concluídos Hoje" value={data.indicadores.concluidos_hoje} badge={{ text: "Hoje", variant: "success" }} />
        <KpiCard label="Tempo de resposta" value={`${data.indicadores.tempo_medio_minutos} min`} badge={{ text: "Tempo médio", variant: "default" }} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card title="Acções rápidas">
          <div className="grid gap-2 sm:grid-cols-2">
            <Link to="/laboratory/pending" className="rounded-xl bg-primary-600 px-4 py-3 text-center text-sm font-medium text-white hover:bg-primary-700">Pedidos Pendentes</Link>
            <Link to="/laboratory/collection" className="rounded-xl border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700 hover:bg-slate-50">Colheitas</Link>
            <Link to="/laboratory/today" className="rounded-xl border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700 hover:bg-slate-50">Processamento</Link>
            <Link to="/laboratory/results" className="rounded-xl border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700 hover:bg-slate-50">Resultados</Link>
          </div>
        </Card>

        <Card title="Amostras em fila">
          {!pending?.results?.length ? (
            <p className="text-sm text-slate-500">Sem pedidos pendentes.</p>
          ) : (
            <ul className="divide-y divide-slate-100 text-sm">
              {pending.results.slice(0, 5).map((order) => (
                <li key={order.id} className="py-3">
                  <Link to={`/laboratory/${order.id}`} className="font-medium text-primary-700 hover:underline">
                    {order.numero_pedido}
                  </Link>
                  <p className="text-xs text-slate-500">{order.paciente.full_name}</p>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
