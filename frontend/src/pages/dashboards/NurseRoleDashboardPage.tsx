import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { IconCalendar, IconLab, IconPatients } from "@/components/icons";
import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card, ErrorState, SkeletonCard } from "@/design-system";
import { usePermissions } from "@/hooks/usePermissions";
import { useReceptionDashboard } from "@/features/reception/hooks/useReceptionDashboard";
import { appointmentsService } from "@/services/appointments/appointments.service";
import { pharmacyService } from "@/services/pharmacy/pharmacy.service";

export function NurseRoleDashboardPage() {
  const { hasPermission } = usePermissions();

  const canTriage = hasPermission("reception.view") && hasPermission("reception.create");

  const reception = useReceptionDashboard({
    enabled: canTriage,
  });

  const appointments = useQuery({
    queryKey: ["consultas-dashboard-nurse"],
    queryFn: appointmentsService.getDashboard,
    enabled: hasPermission("appointments.view"),
    refetchInterval: 60_000,
  });

  const pharmacy = useQuery({
    queryKey: ["pharmacy-urgent-dashboard"],
    queryFn: () => pharmacyService.listUrgentMedicines(),
    enabled: hasPermission("pharmacy.view"),
    refetchInterval: 60_000,
  });

  const lowStock =
    pharmacy.data?.results.filter((m) => Number(m.quantidade_stock) <= 0).length ?? 0;
  const totalMeds = pharmacy.data?.count ?? pharmacy.data?.results.length ?? 0;

  if (appointments.isLoading && hasPermission("appointments.view")) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 3 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (appointments.isError) {
    return (
      <ErrorState
        message="Não foi possível carregar o painel de enfermagem."
        onRetry={() => void appointments.refetch()}
      />
    );
  }

  const indicadores = appointments.data?.indicadores;
  const waiting = reception.data?.cards.patients_waiting ?? 0;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <RoleDashboardHero
        tone="teal"
        eyebrow="Enfermagem"
        title="Painel de Enfermagem"
        description={
          canTriage && waiting > 0
            ? `${waiting} utente${waiting > 1 ? "s" : ""} na fila. Registe triagem ou acompanhe a espera.`
            : "Triagem, stock de urgência e consultas do dia — foco operacional."
        }
        primaryAction={
          canTriage
            ? { to: "/nursing/triage", label: "Nova triagem" }
            : hasPermission("pharmacy.view")
              ? { to: "/stock", label: "Stock de urgência" }
              : { to: "/patients", label: "Pacientes" }
        }
        secondaryAction={
          canTriage
            ? { to: "/reception/queue", label: "Fila de espera" }
            : { to: "/appointments", label: "Agenda" }
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {canTriage ? (
          <KpiCard
            label="Na fila (receção)"
            value={waiting}
            badge={{
              text: waiting > 0 ? "Aguardam receção/médico" : "Fila vazia",
              variant: waiting > 0 ? "warning" : "success",
            }}
            icon={<IconPatients />}
          />
        ) : null}
        {hasPermission("pharmacy.view") ? (
          <KpiCard
            label="Medicamentos (urg.)"
            value={totalMeds}
            badge={{
              text: lowStock > 0 ? `${lowStock} sem stock` : "Stock OK",
              variant: lowStock > 0 ? "warning" : "success",
            }}
            icon={<IconLab />}
          />
        ) : null}
        {indicadores ? (
          <>
            <KpiCard
              label="Consultas hoje"
              value={indicadores.consultas_do_dia}
              badge={{ text: `${indicadores.consultas_em_curso} em curso`, variant: "info" }}
              icon={<IconCalendar />}
            />
            <KpiCard
              label="Em espera"
              value={indicadores.consultas_em_espera}
              badge={{ text: "Sala de espera", variant: "warning" }}
              icon={<IconPatients />}
            />
          </>
        ) : null}
      </div>

      {hasPermission("pharmacy.view") && lowStock > 0 ? (
        <Card title="Stock crítico" description="Registe entradas no stock de urgência.">
          <ul className="space-y-2 text-sm">
            {pharmacy.data?.results
              .filter((m) => Number(m.quantidade_stock) <= 0)
              .slice(0, 5)
              .map((m) => (
                <li key={m.id} className="flex justify-between gap-2 rounded-lg bg-surface-muted/60 px-3 py-2">
                  <span className="font-medium text-text">{m.nome}</span>
                  <span className="text-text-muted">{m.codigo}</span>
                </li>
              ))}
          </ul>
          <Link
            to="/stock"
            className="mt-4 inline-block text-sm font-semibold text-primary-600 hover:text-primary-700"
          >
            Gerir stock →
          </Link>
        </Card>
      ) : null}

      {canTriage ? (
        <Card title="Triagem" description="Registo clínico antes do pagamento na receção.">
          <div className="grid gap-2 sm:grid-cols-2">
            <Link
              to="/nursing/triage"
              className="rounded-xl bg-teal-600 px-4 py-3 text-center text-sm font-semibold text-white hover:bg-teal-700"
            >
              Nova triagem
            </Link>
            <Link
              to="/reception/queue"
              className="rounded-xl border border-border px-4 py-3 text-center text-sm font-semibold hover:bg-surface-muted"
            >
              Ver fila de espera
            </Link>
          </div>
        </Card>
      ) : null}

      <Card title="Módulos">
        <div className="grid gap-2 sm:grid-cols-2">
          {canTriage ? (
            <Link
              to="/nursing/triage"
              className="rounded-xl bg-primary-600 px-4 py-3 text-center text-sm font-semibold text-white hover:bg-primary-700"
            >
              Triagem clínica
            </Link>
          ) : hasPermission("pharmacy.view") ? (
            <Link
              to="/stock"
              className="rounded-xl bg-primary-600 px-4 py-3 text-center text-sm font-semibold text-white hover:bg-primary-700"
            >
              Stock de urgência
            </Link>
          ) : null}
          <Link
            to="/patients"
            className="rounded-xl border border-border px-4 py-3 text-center text-sm font-semibold hover:bg-surface-muted"
          >
            Pacientes
          </Link>
          <Link
            to="/appointments"
            className="rounded-xl border border-border px-4 py-3 text-center text-sm font-semibold hover:bg-surface-muted"
          >
            Consultas / agenda
          </Link>
        </div>
      </Card>
    </div>
  );
}
