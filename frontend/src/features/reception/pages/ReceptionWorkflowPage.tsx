import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";

import { Button, Card, SkeletonCard } from "@/design-system";
import { PatientSearchSelect } from "@/features/reception/components/PatientSearchSelect";
import { useReceptionDashboard } from "@/features/reception/hooks/useReceptionDashboard";
import { useReceptionHotkeys } from "@/hooks/useReceptionHotkeys";
import { appointmentsService } from "@/services/appointments/appointments.service";
import type { PatientListItem } from "@/types/patient";

const STEPS = [
  "Pesquisar paciente",
  "Serviços e pagamento",
  "Recibo",
  "Encaminhar",
] as const;

export function ReceptionWorkflowPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [patientId, setPatientId] = useState<number | null>(null);
  const [selected, setSelected] = useState<PatientListItem | null>(null);

  const { data, isLoading, refetch, isFetching } = useReceptionDashboard();

  useReceptionHotkeys(true, {
    onRefresh: () => {
      void refetch();
      void queryClient.invalidateQueries({ queryKey: ["reception-queue"] });
    },
    onCancel: () => {
      setPatientId(null);
      setSelected(null);
    },
  });

  const appointments = useQuery({
    queryKey: ["consultas-dashboard-reception"],
    queryFn: appointmentsService.getDashboard,
    refetchInterval: 30_000,
  });

  function goInvoice() {
    if (!patientId) return;
    void navigate(`/billing/invoices/new?paciente=${patientId}`);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <p className="text-xs font-semibold tracking-widest text-emerald-700 uppercase dark:text-emerald-400">
            Fluxo rápido
          </p>
          <h1 className="mt-1 text-2xl font-bold tracking-tight text-text sm:text-3xl">
            Atendimento na receção
          </h1>
          <p className="mt-2 max-w-2xl text-sm text-text-muted">
            Pesquise o utente, registe serviços e pagamento com o mínimo de passos. Atalhos: F2 novo
            paciente · F3 nova fatura · F4 pagamentos · F5 actualizar fila · Esc limpar.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Link to="/reception/queue">
            <Button variant="outline">Fila completa</Button>
          </Link>
          <Link to="/reception/check-in">
            <Button variant="secondary">Triagem</Button>
          </Link>
        </div>
      </div>

      <ol className="grid gap-2 sm:grid-cols-4" aria-label="Passos do atendimento">
        {STEPS.map((label, index) => (
          <li
            key={label}
            className="flex items-center gap-2 rounded-xl border border-border bg-surface-muted/50 px-3 py-2 text-xs font-medium text-text-muted"
          >
            <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-primary-600 text-[11px] font-bold text-white">
              {index + 1}
            </span>
            {label}
          </li>
        ))}
      </ol>

      <div className="grid gap-6 xl:grid-cols-[1fr_320px]">
        <Card title="1. Paciente" description="Nome, telefone ou n.º de processo (pesquisa parcial)">
          <PatientSearchSelect
            value={patientId}
            onChange={(id) => {
              setPatientId(id);
              if (!id) setSelected(null);
            }}
            onSelectPatient={setSelected}
          />

          {selected ? (
            <div className="mt-6 flex flex-wrap gap-2 border-t border-border pt-6">
              <Button variant="primary" onClick={goInvoice}>
                Nova fatura para {selected.full_name.split(" ")[0]}
              </Button>
              <Link to={`/patients/${selected.id}`}>
                <Button variant="outline">Abrir ficha</Button>
              </Link>
              <Link to={`/reception/referrals?paciente=${selected.id}`}>
                <Button variant="ghost">Encaminhar</Button>
              </Link>
            </div>
          ) : (
            <div className="mt-6 flex flex-wrap gap-2 border-t border-border pt-6">
              <Link to="/patients/new">
                <Button variant="primary">Novo paciente (F2)</Button>
              </Link>
            </div>
          )}
        </Card>

        <div className="space-y-4">
          <Card title="Fila agora" description={isFetching ? "A actualizar…" : "Pré-visualização"}>
            {isLoading || !data ? (
              <SkeletonCard />
            ) : data.queue_preview.length === 0 ? (
              <p className="text-sm text-text-muted">Sem utentes em espera.</p>
            ) : (
              <ul className="space-y-2 text-sm">
                {data.queue_preview.slice(0, 5).map((e) => (
                  <li key={e.id} className="flex justify-between gap-2 rounded-lg bg-surface-muted/60 px-3 py-2">
                    <span className="truncate font-medium">{e.patient__full_name}</span>
                    <span className="shrink-0 text-xs text-text-muted">#{e.position}</span>
                  </li>
                ))}
              </ul>
            )}
            <Link
              to="/reception/queue"
              className="mt-3 inline-block text-sm font-semibold text-primary-600 hover:text-primary-700"
            >
              Ver fila (F5) →
            </Link>
          </Card>

          <Card title="Consultas hoje">
            <p className="text-3xl font-bold tabular-nums text-text">
              {appointments.data?.indicadores.consultas_do_dia ?? "—"}
            </p>
            <p className="mt-1 text-xs text-text-muted">
              {appointments.data?.indicadores.consultas_concluidas ?? 0} concluídas
            </p>
          </Card>
        </div>
      </div>
    </div>
  );
}
