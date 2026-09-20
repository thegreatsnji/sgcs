import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { IconSearch } from "@/components/icons";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";
import { patientsService } from "@/services/patients";
import type { PatientListItem } from "@/types/patient";

interface PatientSearchSelectProps {
  value: number | null;
  /** @deprecated Prefer onSelectPatient when patient details are needed */
  onChange?: (patientId: number | null) => void;
  onSelectPatient?: (patient: PatientListItem | null) => void;
}

function patientInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[parts.length - 1][0]}`.toUpperCase();
}

export function PatientSearchSelect({ value, onChange, onSelectPatient }: PatientSearchSelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);

  const { data, isLoading, isFetched } = useQuery({
    queryKey: ["patients-search", debouncedSearch],
    queryFn: () =>
      patientsService.list({
        search: debouncedSearch || undefined,
        is_active: true,
        page_size: 10,
      }),
    enabled: debouncedSearch.length >= 2,
  });

  const selectedLabel = useMemo(() => {
    if (!value || !data?.results) return "";
    const match = data.results.find((patient) => patient.id === value);
    return match ? `${match.full_name} (${match.patient_number})` : "";
  }, [value, data?.results]);

  return (
    <div className="space-y-3">
      <div className="relative">
        <IconSearch className="pointer-events-none absolute left-3.5 top-1/2 h-5 w-5 -translate-y-1/2 text-text-muted" />
        <input
          type="search"
          autoFocus
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Nome, telefone ou n.º de processo..."
          className="w-full rounded-xl border border-border bg-surface py-3 pl-11 pr-4 text-sm text-text shadow-sm outline-none transition placeholder:text-text-muted/70 focus:border-primary-500 focus:ring-2 focus:ring-primary-100 dark:focus:ring-primary-900"
        />
      </div>

      {search.length > 0 && search.length < 2 && (
        <p className="text-xs text-text-muted">Escreva pelo menos 2 caracteres para pesquisar.</p>
      )}

      {isLoading && debouncedSearch.length >= 2 && (
        <div className="flex items-center gap-2 rounded-xl border border-border bg-surface-muted px-4 py-3 text-sm text-text-muted">
          <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-500 border-t-transparent" />
          A pesquisar...
        </div>
      )}

      {isFetched && debouncedSearch.length >= 2 && data?.results.length === 0 && (
        <div className="rounded-xl border border-dashed border-border bg-surface-muted/60 px-5 py-8 text-center">
          <p className="text-sm font-medium text-text">Nenhum paciente encontrado</p>
          <p className="mt-1 text-xs text-text-muted">
            Sem resultados para &ldquo;{debouncedSearch}&rdquo;. Pode registar um novo utente abaixo.
          </p>
        </div>
      )}

      {data && data.results.length > 0 && (
        <ul className="divide-y divide-border overflow-hidden rounded-xl border border-border bg-surface shadow-sm">
          {data.results.map((patient) => {
            const selected = value === patient.id;
            return (
              <li key={patient.id}>
                <button
                  type="button"
                  onClick={() => {
                    onChange?.(patient.id);
                    onSelectPatient?.(patient);
                    setSearch(`${patient.full_name} (${patient.patient_number})`);
                  }}
                  className={`flex w-full items-center gap-3 px-4 py-3.5 text-left transition hover:bg-primary-50/80 dark:hover:bg-primary-950/20 ${
                    selected ? "bg-primary-50 dark:bg-primary-950/30" : ""
                  }`}
                >
                  <span
                    className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-full text-xs font-bold ${
                      selected
                        ? "bg-primary-600 text-white"
                        : "bg-surface-muted text-text-muted"
                    }`}
                  >
                    {patientInitials(patient.full_name)}
                  </span>
                  <span className="min-w-0 flex-1">
                    <span className={`block truncate text-sm ${selected ? "font-semibold text-primary-700 dark:text-primary-300" : "font-medium text-text"}`}>
                      {patient.full_name}
                    </span>
                    <span className="mt-0.5 block truncate text-xs text-text-muted">
                      {patient.patient_number}
                      {patient.phone ? ` · ${patient.phone}` : ""}
                    </span>
                  </span>
                  {selected && (
                    <span className="shrink-0 rounded-full bg-primary-600 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wide text-white">
                      Seleccionado
                    </span>
                  )}
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {value && selectedLabel && !data?.results.length && (
        <p className="flex items-center gap-2 text-xs font-medium text-emerald-700 dark:text-emerald-400">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          {selectedLabel}
        </p>
      )}
    </div>
  );
}
