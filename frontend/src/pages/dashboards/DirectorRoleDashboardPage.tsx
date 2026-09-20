import { useMemo, useState, type ReactNode } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { Card, ErrorState } from "@/design-system";
import { formatCurrency } from "@/features/billing/utils/formatBilling";
import {
  dashboardService,
  type DirectorDashboardData,
  type DirectorSection,
} from "@/services/dashboard";

type PeriodoModo = "hoje" | "semana" | "mes" | "personalizado";

function formatPeriodoLabel(inicio: string, fim: string): string {
  const fmt = (iso: string) => {
    const [y, m, d] = iso.slice(0, 10).split("-");
    return `${d}/${m}/${y}`;
  };
  const a = fmt(inicio);
  const b = fmt(fim);
  return a === b ? a : `${a} a ${b}`;
}

function SectionCard<T>({
  title,
  section,
  children,
}: {
  title: string;
  section: DirectorSection<T> | undefined;
  children: (data: T) => ReactNode;
}) {
  if (!section) {
    return (
      <Card title={title}>
        <p className="animate-pulse text-sm text-slate-400">A carregar…</p>
      </Card>
    );
  }
  if (!section.ok) {
    return (
      <Card title={title}>
        <p className="text-sm text-slate-600">{section.error ?? "Não foi possível carregar este indicador."}</p>
      </Card>
    );
  }
  return <Card title={title}>{children(section.data)}</Card>;
}

function KpiTile({
  label,
  value,
  hint,
  tone = "default",
}: {
  label: string;
  value: string;
  hint?: string;
  tone?: "default" | "amber" | "emerald";
}) {
  const toneClass =
    tone === "amber" ? "text-amber-800" : tone === "emerald" ? "text-emerald-800" : "text-slate-900";
  return (
    <div className="rounded-xl border border-slate-200/80 bg-white px-3 py-3 shadow-sm sm:px-4 sm:py-4">
      <p className="text-[11px] font-semibold tracking-wide text-slate-500 uppercase sm:text-xs">{label}</p>
      <p className={`mt-1 text-lg font-bold tabular-nums sm:text-2xl ${toneClass}`}>{value}</p>
      {hint ? <p className="mt-0.5 text-[11px] text-slate-500 sm:text-xs">{hint}</p> : null}
    </div>
  );
}

export function DirectorRoleDashboardPage() {
  const [modo, setModo] = useState<PeriodoModo>("hoje");
  const [customInicio, setCustomInicio] = useState("");
  const [customFim, setCustomFim] = useState("");
  const [appliedCustom, setAppliedCustom] = useState<{ inicio: string; fim: string } | null>(null);

  const queryParams = useMemo(() => {
    if (modo === "personalizado") {
      if (!appliedCustom) return null;
      return {
        periodo: "personalizado" as const,
        data_inicio: appliedCustom.inicio,
        data_fim: appliedCustom.fim,
      };
    }
    return { periodo: modo };
  }, [modo, appliedCustom]);

  const dash = useQuery({
    queryKey: ["director-dashboard", queryParams],
    queryFn: () => dashboardService.getDirectorSummary(queryParams!),
    enabled: queryParams != null,
    retry: false,
    refetchInterval: 120_000,
  });

  const data = dash.data as DirectorDashboardData | undefined;
  const fin = data?.financeiro;
  const op = data?.operacional;
  const lab = data?.laboratorio;
  const stock = data?.stock;
  const servicos = data?.servicos_faturados;

  const periodoLabel =
    data?.periodo != null
      ? formatPeriodoLabel(data.periodo.data_inicio, data.periodo.data_fim)
      : null;

  return (
    <div className="space-y-4 pb-8 sm:space-y-5">
      <header className="space-y-1">
        <p className="text-xs font-semibold tracking-wide text-slate-500 uppercase">Direcção</p>
        <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">Painel de supervisão</h1>
        <p className="text-sm text-slate-600">
          Indicadores operacionais e financeiros. Faturado por emissão; recebido por data de pagamento.
        </p>
        {periodoLabel ? (
          <p className="text-sm font-medium text-slate-800">
            Período: <span className="tabular-nums">{periodoLabel}</span>
          </p>
        ) : null}
      </header>

      <div className="flex flex-wrap gap-2">
        {(
          [
            ["hoje", "Hoje"],
            ["semana", "Esta semana"],
            ["mes", "Este mês"],
            ["personalizado", "Personalizado"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            onClick={() => {
              setModo(id);
              if (id !== "personalizado") setAppliedCustom(null);
            }}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
              modo === id
                ? "bg-slate-900 text-white"
                : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
            }`}
          >
            {label}
          </button>
        ))}
      </div>

      {modo === "personalizado" ? (
        <div className="flex flex-col gap-2 rounded-xl border border-slate-200 bg-slate-50 p-3 sm:flex-row sm:items-end">
          <label className="flex flex-1 flex-col gap-1 text-xs font-medium text-slate-600">
            Data inicial
            <input
              type="date"
              value={customInicio}
              onChange={(e) => setCustomInicio(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-sm text-slate-900"
            />
          </label>
          <label className="flex flex-1 flex-col gap-1 text-xs font-medium text-slate-600">
            Data final
            <input
              type="date"
              value={customFim}
              onChange={(e) => setCustomFim(e.target.value)}
              className="rounded-lg border border-slate-200 bg-white px-2 py-1.5 text-sm text-slate-900"
            />
          </label>
          <button
            type="button"
            disabled={!customInicio || !customFim}
            onClick={() => setAppliedCustom({ inicio: customInicio, fim: customFim })}
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white disabled:opacity-40"
          >
            Aplicar
          </button>
        </div>
      ) : null}

      {modo === "personalizado" && !appliedCustom ? (
        <p className="text-sm text-slate-600">Indique as datas e prima Aplicar.</p>
      ) : null}

      {dash.isError ? (
        <ErrorState
          message="Não foi possível carregar o painel."
          onRetry={() => void dash.refetch()}
        />
      ) : null}

      {/* KPIs financeiros — prioridade no 1.º ecrã */}
      <div className="grid grid-cols-2 gap-2 sm:gap-3 lg:grid-cols-4">
        {dash.isLoading || !fin ? (
          <>
            {["Faturado", "Recebido", "Saldo pendente", "Reduções"].map((l) => (
              <div key={l} className="h-[88px] animate-pulse rounded-xl bg-slate-100" />
            ))}
          </>
        ) : !fin.ok ? (
          <div className="col-span-2 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600 lg:col-span-4">
            {fin.error ?? "Não foi possível carregar este indicador."}
          </div>
        ) : (
          <>
            <KpiTile label="Faturado" value={formatCurrency(fin.data.total_faturado)} />
            <KpiTile
              label="Recebido"
              value={formatCurrency(fin.data.total_recebido)}
              tone="emerald"
            />
            <KpiTile
              label="Saldo pendente"
              value={formatCurrency(fin.data.saldo_pendente)}
              hint={`${fin.data.faturas_com_saldo} faturas com saldo`}
              tone="amber"
            />
            <KpiTile label="Reduções" value={formatCurrency(fin.data.total_reducoes)} />
          </>
        )}
      </div>

      <div className="grid grid-cols-2 gap-2 sm:gap-3 lg:grid-cols-4">
        {dash.isLoading || !op ? (
          <>
            {["Utentes", "Consultas", "Concluídas", "Em espera"].map((l) => (
              <div key={l} className="h-[72px] animate-pulse rounded-xl bg-slate-100" />
            ))}
          </>
        ) : !op.ok ? (
          <div className="col-span-2 rounded-xl border border-slate-200 bg-white p-4 text-sm text-slate-600 lg:col-span-4">
            {op.error ?? "Não foi possível carregar este indicador."}
          </div>
        ) : (
          <>
            <KpiTile
              label="Utentes atendidos"
              value={String(op.data.utentes_atendidos)}
              hint="Check-ins concluídos"
            />
            <KpiTile label="Consultas" value={String(op.data.consultas)} />
            <KpiTile label="Consultas concluídas" value={String(op.data.consultas_concluidas)} />
            <KpiTile label="Em espera" value={String(op.data.consultas_em_espera)} hint="Agora" />
          </>
        )}
      </div>

      <div className="grid gap-3 sm:grid-cols-2">
        <SectionCard title="Laboratório" section={lab}>
          {(d) => (
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-500">Pendentes</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.pedidos_pendentes}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Aguardam regularização</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.aguardam_regularizacao}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Aguardam validação</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.aguardam_validacao}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Concluídos no período</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.concluidos_periodo}</dd>
              </div>
            </dl>
          )}
        </SectionCard>

        <SectionCard title="Stock de urgência" section={stock}>
          {(d) => (
            <dl className="grid grid-cols-2 gap-3 text-sm">
              <div>
                <dt className="text-slate-500">Stock baixo</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.stock_baixo}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Sem stock</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.sem_stock}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Próximos da validade</dt>
                <dd className="text-lg font-semibold tabular-nums">{d.proximos_validade}</dd>
              </div>
              <div>
                <dt className="text-slate-500">Expirados</dt>
                <dd className="text-lg font-semibold tabular-nums text-red-700">{d.expirados}</dd>
              </div>
            </dl>
          )}
        </SectionCard>
      </div>

      <SectionCard title="Serviços faturados" section={servicos}>
        {(d) =>
          d.itens.length === 0 ? (
            <p className="text-sm text-slate-500">Sem linhas de fatura neste período.</p>
          ) : (
            <ul className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {d.itens.map((s) => (
                <li
                  key={s.servico}
                  className="flex justify-between rounded-lg bg-slate-50 px-3 py-2 text-sm"
                >
                  <span className="truncate font-medium text-slate-800">{s.servico}</span>
                  <span className="shrink-0 tabular-nums text-slate-600">{s.quantidade}×</span>
                </li>
              ))}
            </ul>
          )
        }
      </SectionCard>

      <p className="text-xs text-slate-500">
        Despesas e lucro não estão neste painel enquanto o fluxo de despesas não estiver validado no piloto.
      </p>

      <div className="flex flex-wrap gap-3 text-sm">
        <Link to="/reports" className="font-medium text-primary-700 hover:underline">
          Relatórios
        </Link>
        <Link to="/billing/invoices" className="font-medium text-primary-700 hover:underline">
          Faturação
        </Link>
        <Link to="/billing/reducoes/pendentes" className="font-medium text-primary-700 hover:underline">
          Reduções pendentes
        </Link>
        <Link to="/stock" className="font-medium text-primary-700 hover:underline">
          Stock
        </Link>
      </div>
    </div>
  );
}
