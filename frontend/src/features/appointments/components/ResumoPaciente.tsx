import { Avatar, Badge } from "@/design-system";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import type { ClinicalPatientSummary } from "@/types/clinicalRecord";

interface ResumoPacienteProps {
  paciente: ClinicalPatientSummary;
}

export function ResumoPaciente({ paciente }: ResumoPacienteProps) {
  const severeAllergies = paciente.allergies.filter((a) => a.severity === "SEVERE");

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-wrap items-start gap-4">
        <Avatar name={paciente.full_name} src={paciente.photo_url ?? undefined} size="lg" />
        <div className="min-w-0 flex-1">
          <h2 className="text-xl font-bold text-slate-900">{paciente.full_name}</h2>
          <p className="text-sm text-slate-500">N.º {paciente.patient_number}</p>
          <div className="mt-2 flex flex-wrap gap-2 text-sm">
            {paciente.age != null && <Badge>{paciente.age} anos</Badge>}
            {paciente.gender && (
              <Badge>{PATIENT_GENDER_LABELS[paciente.gender as keyof typeof PATIENT_GENDER_LABELS] ?? paciente.gender}</Badge>
            )}
            {paciente.blood_type && <Badge variant="info">Grupo {paciente.blood_type}</Badge>}
          </div>
          <p className="mt-2 text-sm text-slate-600">
            {paciente.phone ?? "—"} · {paciente.email ?? "—"}
          </p>
        </div>
      </div>

      {severeAllergies.length > 0 && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
          <strong>Alergias graves:</strong>{" "}
          {severeAllergies.map((a) => a.allergen).join(", ")}
        </div>
      )}

      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Alergias</h3>
          {paciente.allergies.length === 0 ? (
            <p className="mt-1 text-sm text-slate-500">Nenhuma registada.</p>
          ) : (
            <ul className="mt-1 space-y-1 text-sm">
              {paciente.allergies.map((a) => (
                <li key={a.id}>
                  {a.allergen} <span className="text-slate-400">({a.severity})</span>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div>
          <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Doenças crónicas</h3>
          {paciente.chronic_diseases.length === 0 ? (
            <p className="mt-1 text-sm text-slate-500">Nenhuma registada.</p>
          ) : (
            <ul className="mt-1 space-y-1 text-sm">
              {paciente.chronic_diseases.map((d) => (
                <li key={d.id}>{d.disease_name}</li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
