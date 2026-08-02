import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import { CurrencyDisplay, Input } from "@/design-system";
import { categoryLabel } from "@/constants/serviceCategories";
import { MOTIVOS_REDUCAO, calcReducao } from "@/features/billing/constants/reducao";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import type { BillingService } from "@/types/billing";

const RECENT_KEY = "sgcs-servicos-recentes";

export interface InvoiceLineDraft {
  servico: BillingService;
  quantidade: number;
  aplicarReducao?: boolean;
  precoCobrado?: number;
  motivoReducao?: string;
  observacaoReducao?: string;
  autorizacaoReducaoId?: number;
  estadoAutorizacao?: string;
}

interface ServiceSearchPickerProps {
  services: BillingService[];
  isLoading?: boolean;
  error?: boolean;
  onRetry?: () => void;
  lines: InvoiceLineDraft[];
  onChange: (lines: InvoiceLineDraft[]) => void;
  readOnlyPrice?: boolean;
  popularServiceIds?: number[];
}

function formatFcfa(preco: string) {
  const n = Number(preco);
  if (Number.isNaN(n)) return `${preco} FCFA`;
  return `${n.toLocaleString("pt-PT")} FCFA`;
}

function loadRecent(): number[] {
  try {
    const raw = localStorage.getItem(RECENT_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as number[];
    return Array.isArray(parsed) ? parsed.slice(0, 8) : [];
  } catch {
    return [];
  }
}

function pushRecent(id: number) {
  const next = [id, ...loadRecent().filter((x) => x !== id)].slice(0, 8);
  localStorage.setItem(RECENT_KEY, JSON.stringify(next));
}

export function ServiceSearchPicker({
  services,
  isLoading,
  error,
  onRetry,
  lines,
  onChange,
  popularServiceIds = [],
}: ServiceSearchPickerProps) {
  const [query, setQuery] = useState("");
  const debouncedQuery = useDebouncedValue(query, 250);
  const [categoria, setCategoria] = useState("");
  const [open, setOpen] = useState(false);
  const [highlight, setHighlight] = useState(0);
  const listRef = useRef<HTMLUListElement>(null);

  const byId = useMemo(() => new Map(services.map((s) => [s.id, s])), [services]);

  const recentServices = useMemo(
    () => loadRecent().map((id) => byId.get(id)).filter(Boolean) as BillingService[],
    [byId, services],
  );

  const popularServices = useMemo(
    () =>
      popularServiceIds
        .map((id) => byId.get(id))
        .filter((s): s is BillingService => Boolean(s)),
    [byId, popularServiceIds],
  );

  const filtered = useMemo(() => {
    const q = debouncedQuery.trim().toLowerCase();
    return services.filter((s) => {
      if (categoria && s.categoria !== categoria) return false;
      if (!q) return true;
      return s.nome.toLowerCase().includes(q) || s.codigo.toLowerCase().includes(q);
    });
  }, [services, debouncedQuery, categoria]);

  const displayList = useMemo(() => {
    if (debouncedQuery.trim() || categoria) return filtered.slice(0, 50);
    const merged: BillingService[] = [];
    const seen = new Set<number>();
    for (const s of [...recentServices, ...popularServices, ...services]) {
      if (seen.has(s.id)) continue;
      seen.add(s.id);
      merged.push(s);
      if (merged.length >= 30) break;
    }
    return merged;
  }, [debouncedQuery, categoria, filtered, recentServices, popularServices, services]);

  const categorias = useMemo(() => {
    const set = new Set(services.map((s) => s.categoria));
    return Array.from(set).sort();
  }, [services]);

  const subtotal = lines.reduce((acc, line) => {
    const oficial = Number(line.servico.preco);
    const unit =
      line.aplicarReducao && line.precoCobrado != null ? line.precoCobrado : oficial;
    return acc + unit * line.quantidade;
  }, 0);

  const addService = useCallback(
    (servico: BillingService) => {
      if (!servico.activo) return;
      pushRecent(servico.id);
      const existing = lines.find((l) => l.servico.id === servico.id);
      if (existing) {
        onChange(
          lines.map((l) =>
            l.servico.id === servico.id ? { ...l, quantidade: l.quantidade + 1 } : l,
          ),
        );
      } else {
        onChange([...lines, { servico, quantidade: 1 }]);
      }
      setOpen(false);
      setQuery("");
      setHighlight(0);
    },
    [lines, onChange],
  );

  useEffect(() => {
    setHighlight(0);
  }, [debouncedQuery, categoria, displayList.length]);

  useEffect(() => {
    const el = listRef.current?.children[highlight] as HTMLElement | undefined;
    el?.scrollIntoView({ block: "nearest" });
  }, [highlight]);

  function onInputKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (!open && (e.key === "ArrowDown" || e.key === "Enter")) {
      setOpen(true);
      return;
    }
    if (e.key === "Escape") {
      setOpen(false);
      return;
    }
    if (!displayList.length) return;
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setHighlight((h) => Math.min(h + 1, displayList.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setHighlight((h) => Math.max(h - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const picked = displayList[highlight];
      if (picked) addService(picked);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 sm:flex-row">
        <Input
          label="Pesquisar serviço"
          placeholder="Nome ou código…"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={onInputKeyDown}
          aria-autocomplete="list"
          aria-expanded={open}
          aria-controls="service-search-results"
        />
        <label className="flex flex-col gap-1 text-sm">
          <span className="font-medium text-slate-700">Categoria</span>
          <select
            className="rounded-lg border border-border px-3 py-2"
            value={categoria}
            onChange={(e) => {
              setCategoria(e.target.value);
              setOpen(true);
            }}
          >
            <option value="">Todas</option>
            {categorias.map((c) => (
              <option key={c} value={c}>
                {categoryLabel(c)}
              </option>
            ))}
          </select>
        </label>
      </div>

      {isLoading ? (
        <p className="text-sm text-slate-500" role="status">
          A carregar serviços…
        </p>
      ) : error ? (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          Não foi possível carregar o catálogo.{" "}
          {onRetry ? (
            <button type="button" className="underline" onClick={onRetry}>
              Tentar novamente
            </button>
          ) : null}
        </div>
      ) : open && displayList.length === 0 ? (
        <p className="text-sm text-slate-500">Nenhum serviço encontrado para esta pesquisa.</p>
      ) : open ? (
        <>
          {!debouncedQuery && !categoria && recentServices.length > 0 ? (
            <p className="text-xs text-slate-500">Recentes e serviços frequentes</p>
          ) : null}
          <ul
            id="service-search-results"
            ref={listRef}
            className="max-h-64 divide-y overflow-y-auto rounded-lg border border-border bg-white"
            role="listbox"
            aria-label="Resultados de serviços"
          >
            {displayList.map((s, index) => {
              const inactive = !s.activo;
              const semPreco = !s.preco_confirmado;
              return (
                <li key={s.id} role="option" aria-selected={index === highlight}>
                  <button
                    type="button"
                    className={`flex w-full flex-col gap-0.5 px-4 py-3 text-left hover:bg-slate-50 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary ${
                      index === highlight ? "bg-slate-50" : ""
                    } ${inactive ? "opacity-50" : ""}`}
                    disabled={inactive}
                    onClick={() => addService(s)}
                  >
                    <span className="font-medium text-slate-900">{s.nome}</span>
                    <span className="text-xs text-slate-600">
                      {s.codigo} — {categoryLabel(s.categoria)}
                      {s.departamento_nome ? ` — ${s.departamento_nome}` : ""} —{" "}
                      {semPreco ? "Preço pendente" : formatFcfa(s.preco)}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        </>
      ) : null}

      {lines.length > 0 ? (
        <div className="rounded-lg border border-border p-4">
          <h3 className="mb-2 text-sm font-semibold text-slate-800">Itens da fatura</h3>
          <ul className="space-y-2">
            {lines.map((line) => {
              const oficial = Number(line.servico.preco);
              const cobrado =
                line.aplicarReducao && line.precoCobrado != null ? line.precoCobrado : oficial;
              const { diff, pct } = calcReducao(oficial, cobrado);
              return (
              <li
                key={line.servico.id}
                className="flex flex-col gap-2 rounded border border-slate-100 p-3 text-sm"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                <span>
                  {line.servico.nome}{" "}
                  <span className="text-slate-500">
                    Preço oficial: {formatFcfa(line.servico.preco)}
                  </span>
                </span>
                <div className="flex items-center gap-2">
                  <label className="sr-only" htmlFor={`qty-${line.servico.id}`}>
                    Quantidade
                  </label>
                  <input
                    id={`qty-${line.servico.id}`}
                    type="number"
                    min={1}
                    className="w-16 rounded border px-2 py-1"
                    value={line.quantidade}
                    onChange={(e) => {
                      const quantidade = Math.max(1, Number(e.target.value) || 1);
                      onChange(
                        lines.map((l) =>
                          l.servico.id === line.servico.id ? { ...l, quantidade } : l,
                        ),
                      );
                    }}
                  />
                  <button
                    type="button"
                    className="text-red-600 hover:underline"
                    onClick={() => onChange(lines.filter((l) => l.servico.id !== line.servico.id))}
                  >
                    Remover
                  </button>
                </div>
                </div>
                <label className="flex items-center gap-2 text-xs text-slate-700">
                  <input
                    type="checkbox"
                    checked={Boolean(line.aplicarReducao)}
                    onChange={(e) => {
                      const aplicarReducao = e.target.checked;
                      onChange(
                        lines.map((l) =>
                          l.servico.id === line.servico.id
                            ? {
                                ...l,
                                aplicarReducao,
                                precoCobrado: aplicarReducao ? oficial : undefined,
                              }
                            : l,
                        ),
                      );
                    }}
                  />
                  Aplicar redução do valor
                </label>
                {line.aplicarReducao ? (
                  <div className="grid gap-2 sm:grid-cols-2">
                    <label className="text-xs">
                      Valor que será cobrado (FCFA)
                      <input
                        type="number"
                        min={0}
                        max={oficial}
                        className="mt-1 w-full rounded border px-2 py-1"
                        value={line.precoCobrado ?? oficial}
                        onChange={(e) => {
                          const precoCobrado = Math.min(
                            oficial,
                            Math.max(0, Number(e.target.value) || 0),
                          );
                          onChange(
                            lines.map((l) =>
                              l.servico.id === line.servico.id ? { ...l, precoCobrado } : l,
                            ),
                          );
                        }}
                      />
                    </label>
                    <label className="text-xs">
                      Motivo
                      <select
                        className="mt-1 w-full rounded border px-2 py-1"
                        value={line.motivoReducao ?? ""}
                        onChange={(e) =>
                          onChange(
                            lines.map((l) =>
                              l.servico.id === line.servico.id
                                ? { ...l, motivoReducao: e.target.value }
                                : l,
                            ),
                          )
                        }
                      >
                        <option value="">— Seleccionar —</option>
                        {MOTIVOS_REDUCAO.map((m) => (
                          <option key={m.value} value={m.value}>
                            {m.label}
                          </option>
                        ))}
                      </select>
                    </label>
                    {line.motivoReducao === "OUTRO" ? (
                      <label className="text-xs sm:col-span-2">
                        Observação (obrigatória)
                        <input
                          className="mt-1 w-full rounded border px-2 py-1"
                          value={line.observacaoReducao ?? ""}
                          onChange={(e) =>
                            onChange(
                              lines.map((l) =>
                                l.servico.id === line.servico.id
                                  ? { ...l, observacaoReducao: e.target.value }
                                  : l,
                              ),
                            )
                          }
                        />
                      </label>
                    ) : null}
                    {diff > 0 ? (
                      <p className="text-xs text-slate-600 sm:col-span-2">
                        Redução aplicada: {diff.toLocaleString("pt-PT")} FCFA (
                        {pct.toFixed(0)}%). O preço oficial do catálogo não será alterado.
                      </p>
                    ) : null}
                    {line.estadoAutorizacao === "PENDENTE" ? (
                      <p className="text-xs font-medium text-amber-700 sm:col-span-2">
                        Esta redução necessita de autorização da Direção.
                      </p>
                    ) : null}
                  </div>
                ) : null}
              </li>
            );
            })}
          </ul>
          <p className="mt-3 text-right text-sm font-semibold">
            Subtotal: <CurrencyDisplay value={subtotal} />
          </p>
        </div>
      ) : null}
    </div>
  );
}
