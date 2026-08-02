import { IconSearch } from "@/components/icons";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import type { PatientGender } from "@/types/patient";

import { SelectField } from "./SelectField";
import { AGE_GROUP_LABELS, type AgeGroup } from "../utils/patientUtils";

interface PatientFiltersProps {
  search: string;
  gender: string;
  isActive: string;
  ageGroup: AgeGroup;
  onSearchChange: (value: string) => void;
  onGenderChange: (value: string) => void;
  onIsActiveChange: (value: string) => void;
  onAgeGroupChange: (value: AgeGroup) => void;
}

export function PatientFilters({
  search,
  gender,
  isActive,
  ageGroup,
  onSearchChange,
  onGenderChange,
  onIsActiveChange,
  onAgeGroupChange,
}: PatientFiltersProps) {
  return (
    <div className="space-y-4">
      <div className="relative">
        <IconSearch className="pointer-events-none absolute top-1/2 left-4 h-5 w-5 -translate-y-1/2 text-slate-400" />
        <input
          type="search"
          value={search}
          onChange={(event) => onSearchChange(event.target.value)}
          placeholder="Pesquisar por nome, documento, telefone ou n.º processo..."
          className="h-12 w-full rounded-2xl border border-slate-200 bg-slate-50/80 pr-4 pl-12 text-sm text-slate-800 transition focus:border-primary-300 focus:bg-white focus:ring-2 focus:ring-primary-100 focus:outline-none"
          aria-label="Pesquisar pacientes"
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <SelectField
          label="Género"
          placeholder="Todos"
          value={gender}
          onChange={(event) => onGenderChange(event.target.value)}
          options={(Object.entries(PATIENT_GENDER_LABELS) as [PatientGender, string][]).map(
            ([value, label]) => ({ value, label }),
          )}
          className="rounded-xl border-slate-200 bg-slate-50/80"
        />
        <SelectField
          label="Estado"
          placeholder="Todos"
          value={isActive}
          onChange={(event) => onIsActiveChange(event.target.value)}
          options={[
            { value: "true", label: "Ativos" },
            { value: "false", label: "Inativos" },
            { value: "", label: "Todos" },
          ]}
          className="rounded-xl border-slate-200 bg-slate-50/80"
        />
        <SelectField
          label="Faixa etária"
          placeholder="Todas"
          value={ageGroup}
          onChange={(event) => onAgeGroupChange(event.target.value as AgeGroup)}
          options={(
            Object.entries(AGE_GROUP_LABELS) as [Exclude<AgeGroup, "">, string][]
          ).map(([value, label]) => ({ value, label }))}
          className="rounded-xl border-slate-200 bg-slate-50/80"
        />
      </div>

      {ageGroup && (
        <p className="text-xs text-slate-500">
          O filtro de faixa etária aplica-se aos resultados da página actual.
        </p>
      )}
    </div>
  );
}
