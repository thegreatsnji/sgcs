import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { IconCalendar, IconLab, IconPatients } from "@/components/icons";
import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
import { KpiCard } from "@/components/ui/KpiCard";
import { Card, ErrorState, SkeletonCard } from "@/design-system";
import { usePermissions } from "@/hooks/usePermissions";
import { pharmacyService } from "@/services/pharmacy/pharmacy.service";

const STATUS_LABEL: Record<string, string> = {
  STOCK_BAIXO: "Stock baixo",
  SEM_STOCK: "Sem stock",
  PROXIMO_DA_VALIDADE: "Próximo da validade",
  EXPIRADO: "Expirado",
};

export function NurseRoleDashboardPage() {
  const { hasPermission } = usePermissions();
  const canTriage = hasPermission("reception.create");
  const canStock = hasPermission("pharmacy.view") || hasPermission("stock.view");

  const stockDash = useQuery({
    queryKey: ["stock-urgencia-dash-nurse"],
    queryFn: pharmacyService.dashboard,
    enabled: canStock,
    refetchInterval: 60_000,
  });

  if (canStock && stockDash.isLoading) {
    return (
      <div className="space-y-6">
        <SkeletonCard />
        <div className="grid gap-4 sm:grid-cols-3">
          {Array.from({ length: 4 }).map((_, i) => (
            <SkeletonCard key={i} />
          ))}
        </div>
      </div>
    );
  }

  if (canStock && stockDash.isError) {
    return (
      <ErrorState
        message="Não foi possível carregar o painel de enfermagem."
        onRetry={() => void stockDash.refetch()}
      />
    );
  }

  const dash = stockDash.data;
  const attention = dash?.precisa_atencao ?? [];

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <RoleDashboardHero
        tone="teal"
        eyebrow="Enfermagem"
        title="Painel de Enfermagem"
        description="Triagem clínica e stock de urgência."
        primaryAction={
          canTriage
            ? { to: "/nursing/triage", label: "Nova triagem" }
            : canStock
              ? { to: "/stock", label: "Stock de urgência" }
              : { to: "/patients", label: "Pacientes" }
        }
        secondaryAction={canStock ? { to: "/stock", label: "Stock de urgência" } : undefined}
      />

      {canStock && dash ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <KpiCard
            label="Stock baixo"
            value={dash.stock_baixo}
            badge={{ text: "Abaixo do mínimo", variant: dash.stock_baixo > 0 ? "warning" : "success" }}
            icon={<IconLab />}
            to="/stock?estado=STOCK_BAIXO"
          />
          <KpiCard
            label="Sem stock"
            value={dash.sem_stock}
            badge={{ text: dash.sem_stock > 0 ? "Ruptura" : "OK", variant: dash.sem_stock > 0 ? "warning" : "success" }}
            icon={<IconPatients />}
            to="/stock?estado=SEM_STOCK"
          />
          <KpiCard
            label="Próximos da validade"
            value={dash.proximos_validade}
            badge={{ text: "30 dias", variant: dash.proximos_validade > 0 ? "warning" : "success" }}
            icon={<IconCalendar />}
            to="/stock?estado=PROXIMO_DA_VALIDADE"
          />
          <KpiCard
            label="Expirados"
            value={dash.expirados}
            badge={{ text: dash.expirados > 0 ? "Não utilizar" : "Nenhum", variant: dash.expirados > 0 ? "danger" : "success" }}
            icon={<IconLab />}
            to="/stock?estado=EXPIRADO"
          />
        </div>
      ) : null}

      {canStock && attention.length > 0 ? (
        <Card title="Itens a acompanhar" description="Stock baixo, sem stock, validade ou expirados.">
          <ul className="space-y-2 text-sm">
            {attention.slice(0, 8).map((item) => (
              <li key={item.id}>
                <Link
                  to={`/stock?estado=${encodeURIComponent(item.estado)}`}
                  className="flex justify-between gap-2 rounded-lg bg-surface-muted/60 px-3 py-2 hover:bg-primary-50"
                >
                  <span className="font-medium text-text">{item.nome}</span>
                  <span className="text-text-muted">{STATUS_LABEL[item.estado] ?? item.estado}</span>
                </Link>
              </li>
            ))}
          </ul>
          <Link to="/stock" className="mt-4 inline-block text-sm font-semibold text-primary-600 hover:text-primary-700">
            Abrir stock de urgência
          </Link>
        </Card>
      ) : null}

      {canTriage ? (
        <Card title="Triagem" description="Registe sinais vitais e prioridade. A Receção trata o pagamento e o encaminhamento.">
          <Link
            to="/nursing/triage"
            className="inline-block rounded-xl bg-teal-600 px-4 py-3 text-center text-sm font-semibold text-white hover:bg-teal-700"
          >
            Nova triagem
          </Link>
        </Card>
      ) : null}
    </div>
  );
}
