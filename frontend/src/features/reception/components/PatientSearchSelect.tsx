import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { patientsService } from "@/services/patients";
import { useDebouncedValue } from "@/hooks/useDebouncedValue";

interface PatientSearchSelectProps {
  value: number | null;
  onChange: (patientId: number | null) => void;
}

export function PatientSearchSelect({ value, onChange }: PatientSearchSelectProps) {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebouncedValue(search);

  const { data, isLoading } = useQuery({
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
    <div className="space-y-2">
      <input
        type="search"
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        placeholder="Pesquisar por nome ou n.º processo..."
        className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
      />
      {isLoading && debouncedSearch.length >= 2 && (
        <p className="text-xs text-slate-500">A pesquisar...</p>
      )}
      {data && data.results.length > 0 && (
        <ul className="max-h-48 overflow-y-auto rounded-lg border border-slate-200 bg-white">
          {data.results.map((patient) => (
            <li key={patient.id}>
              <button
                type="button"
                onClick={() => {
                  onChange(patient.id);
                  setSearch(`${patient.full_name} (${patient.patient_number})`);
                }}
                className={`w-full px-3 py-2 text-left text-sm hover:bg-primary-50 ${
                  value === patient.id ? "bg-primary-50 font-medium text-primary-700" : "text-slate-700"
                }`}
              >
                {patient.full_name} — {patient.patient_number}
              </button>
            </li>
          ))}
        </ul>
      )}
      {value && selectedLabel && (
        <p className="text-xs text-green-700">Seleccionado: {selectedLabel}</p>
      )}
    </div>
  );
}
