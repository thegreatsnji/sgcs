import { Link } from "react-router-dom";

import { Avatar, Badge } from "@/design-system";
import { PatientAgeCategoryBadge } from "@/components/patients/PatientAgeCategoryBadge";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import { getPatientAgeCategory } from "@/utils/patientAgeCategory";
import type { ClinicalPatientSummary } from "@/types/clinicalRecord";
import type { ClinicalRecord } from "@/types/clinicalRecord";
import { formatDisplayDateTime } from "@/utils/date";

interface ConsultationPatientHeaderProps {
  paciente: ClinicalPatientSummary;
  consulta: ClinicalRecord["consulta"];
}

const SEVERE_ALLERGY_LEVELS = new Set(["GRAVE", "ANAFILAXIA", "SEVERE"]);

export function ConsultationPatientHeader({ paciente, consulta }: ConsultationPatientHeaderProps) {
  const severeAllergies = paciente.allergies.filter((a) => SEVERE_ALLERGY_LEVELS.has(a.severity));

  return (
    <header className="rounded-2xl border border-slate-200/80 bg-white shadow-sm">
      <div className="border-b border-slate-100 bg-gradient-to-r from-primary-50/60 to-white p-5 sm:p-6">
        <div className="flex flex-wrap items-start gap-5">
          <Avatar name={paciente.full_name} src={paciente.photo_url ?? undefined} size="xl" />
          <div className="min-w-0 flex-1">
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <h1 className="text-xl font-bold tracking-tight text-slate-900 sm:text-2xl">
                  {paciente.full_name}
                </h1>
                <p className="mt-1 font-mono text-xs text-slate-500">{paciente.patient_number}</p>
              </div>
              <div className="text-right text-xs text-slate-500">
                <p className="font-mono">{consulta.appointment_number}</p>
                {consulta.started_at && (
                  <p className="mt-1">Início: {formatDisplayDateTime(consulta.started_at)}</p>
                )}
              </div>
            </div>

            <div className="mt-3 flex flex-wrap gap-2">
              {paciente.age != null && (
                <Badge variant="default">{paciente.age} anos</Badge>
              )}
              <PatientAgeCategoryBadge category={getPatientAgeCategory(paciente.age)} />
              {paciente.gender && (
                <Badge>
                  {PATIENT_GENDER_LABELS[paciente.gender as keyof typeof PATIENT_GENDER_LABELS] ?? paciente.gender}
                </Badge>
              )}
              {paciente.blood_type && (
                <Badge variant="info">Grupo {paciente.blood_type}</Badge>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 p-5 sm:grid-cols-3 sm:p-6">
        <div>
          <h2 className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Alergias</h2>
          {paciente.allergies.length === 0 ? (
            <p className="mt-1 text-sm text-slate-500">Nenhuma registada</p>
          ) : (
            <ul className="mt-1 space-y-1 text-sm text-slate-700">
              {paciente.allergies.slice(0, 4).map((a) => (
                <li key={a.id}>
                  {a.allergen}{" "}
                  <span className="text-slate-400">({a.severity})</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <h2 className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Consultas anteriores</h2>
          <p className="mt-1 text-sm text-slate-700">
            Ver histórico na barra lateral
          </p>
          <Link
            to={`/patients/${paciente.id}/history`}
            className="mt-2 inline-block text-xs font-medium text-primary-600 hover:text-primary-700"
          >
            Ficha completa →
          </Link>
        </div>

        <div>
          <h2 className="text-[10px] font-semibold tracking-widest text-slate-400 uppercase">Motivo actual</h2>
          <p className="mt-1 text-sm text-slate-700">{consulta.chief_complaint || "—"}</p>
          <p className="mt-1 text-[11px] text-slate-500">
            Queixas registadas na triagem/receção — não repetir na ficha do utente.
          </p>
          <p className="mt-2 text-xs text-slate-500">
            {paciente.phone ?? "—"} · {paciente.email ?? "—"}
          </p>
        </div>
      </div>

      {severeAllergies.length > 0 && (
        <div className="mx-5 mb-5 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800 sm:mx-6">
          <strong className="font-semibold">Alerta clínico — alergias graves:</strong>{" "}
          {severeAllergies.map((a) => a.allergen).join(", ")}
        </div>
      )}
    </header>
  );
}
