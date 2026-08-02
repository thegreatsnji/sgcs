import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { KpiCard } from "@/components/ui/KpiCard";
import { Button, Card, ErrorState } from "@/design-system";
import { LaboratorySubNav } from "@/features/laboratory/components/LaboratorySubNav";
import { LaboratoryDashboardSkeleton, LaboratoryTableSkeleton } from "@/features/laboratory/components/LaboratorySkeleton";
import { TabelaResultados } from "@/features/laboratory/results/components/TabelaResultados";
import { laboratoryResultsService, laboratoryService } from "@/services/laboratory";

export function ResultsDashboardPage() {
  const [estadoFiltro, setEstadoFiltro] = useState<string>("");

  const { data: dashboard, isLoading: dashLoading, isError: dashError, refetch: refetchDash } = useQuery({
    queryKey: ["laboratory-dashboard"],
    queryFn: laboratoryService.getDashboard,
  });

  const { data: results, isLoading, isError, refetch } = useQuery({
    queryKey: ["laboratory-results"],
    queryFn: () => laboratoryResultsService.list({ page: 1 }),
  });

  const kpis = dashboard?.resultados;

  const filteredResults = useMemo(() => {
    const rows = results?.results ?? [];
    if (!estadoFiltro) return rows;
    return rows.filter((r) => r.estado === estadoFiltro);
  }, [results?.results, estadoFiltro]);

  const FILTROS = [
    { id: "", label: "Todos" },
    { id: "RESULTADO_PENDENTE", label: "Pendentes" },
    { id: "EM_PROCESSAMENTO", label: "Em processamento" },
    { id: "VALIDADO", label: "Validados" },
    { id: "ENTREGUE", label: "Entregues" },
  ] as const;

  if (dashLoading) return <LaboratoryDashboardSkeleton />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">Resultados Laboratoriais</h1>
        <p className="mt-1 text-slate-500">Gestão, validação e entrega de resultados analíticos.</p>
      </div>
      <LaboratorySubNav />

      {dashError && (
        <ErrorState message="Não foi possível carregar indicadores." onRetry={() => void refetchDash()} />
      )}

      {kpis && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <KpiCard label="Pendentes" value={kpis.resultados_pendentes} badge={{ text: "Aguardam validação", variant: "warning" }} />
          <KpiCard label="Validados" value={kpis.resultados_validados} badge={{ text: "Prontos a publicar", variant: "success" }} />
          <KpiCard label="Entregues Hoje" value={kpis.resultados_entregues_hoje} badge={{ text: "Ao médico", variant: "info" }} />
          <KpiCard label="Tempo de validação" value={`${kpis.tempo_medio_validacao_minutos} min`} badge={{ text: "Médio", variant: "default" }} />
        </div>
      )}

      <div className="flex flex-wrap gap-2" role="tablist" aria-label="Filtrar por estado">
        {FILTROS.map((f) => (
          <Button
            key={f.id || "all"}
            variant={estadoFiltro === f.id ? "primary" : "outline"}
            className="!rounded-full"
            onClick={() => setEstadoFiltro(f.id)}
          >
            {f.label}
          </Button>
        ))}
      </div>

      {isLoading || !results ? (
        <LaboratoryTableSkeleton />
      ) : isError ? (
        <ErrorState message="Não foi possível carregar resultados." onRetry={() => void refetch()} />
      ) : (
        <Card title="Resultados recentes">
          <TabelaResultados resultados={filteredResults} />
        </Card>
      )}
    </div>
  );
}
