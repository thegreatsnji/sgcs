import { Input } from "@/design-system";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import type { PatientGender } from "@/types/patient";

import { SelectField } from "./SelectField";

interface PatientFiltersProps {
  search: string;
  gender: string;
  isActive: string;
  onSearchChange: (value: string) => void;
  onGenderChange: (value: string) => void;
  onIsActiveChange: (value: string) => void;
}

export function PatientFilters({
  search,
  gender,
  isActive,
  onSearchChange,
  onGenderChange,
  onIsActiveChange,
}: PatientFiltersProps) {
  return (
    <div className="grid gap-4 md:grid-cols-3">
      <Input
        label="Pesquisar"
        placeholder="Nome, documento, telefone ou n.º processo"
        value={search}
        onChange={(event) => onSearchChange(event.target.value)}
      />
      <SelectField
        label="Género"
        placeholder="Todos"
        value={gender}
        onChange={(event) => onGenderChange(event.target.value)}
        options={(Object.entries(PATIENT_GENDER_LABELS) as [PatientGender, string][]).map(
          ([value, label]) => ({ value, label }),
        )}
      />
      <SelectField
        label="Estado"
        placeholder="Todos"
        value={isActive}
        onChange={(event) => onIsActiveChange(event.target.value)}
        options={[
          { value: "true", label: "Ativos" },
          { value: "false", label: "Inativos" },
        ]}
      />
    </div>
  );
}
