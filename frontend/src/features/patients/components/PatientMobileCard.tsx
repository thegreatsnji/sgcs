import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Badge } from "@/design-system";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import type { PatientListItem } from "@/types/patient";
import { formatDisplayDateTime } from "@/utils/date";

import { PatientRowActions } from "./PatientRowActions";
import { getPatientAge } from "../utils/patientUtils";

interface PatientMobileCardProps {
  patient: PatientListItem;
  onDeactivate?: (patient: PatientListItem) => void;
  onActivate?: (id: number) => void;
}

function PatientMobileCardComponent({ patient, onDeactivate, onActivate }: PatientMobileCardProps) {
  const age = getPatientAge(patient.birth_date);

  return (
    <article className="rounded-2xl border border-slate-200/80 bg-white p-4 shadow-sm transition hover:shadow-md">
      <div className="flex items-start gap-3">
        <Link to={`/patients/${patient.id}`} className="shrink-0 focus-ring rounded-full">
          <Avatar name={patient.full_name} size="md" />
        </Link>
        <div className="min-w-0 flex-1">
          <div className="flex items-start justify-between gap-2">
            <div className="min-w-0">
              <Link
                to={`/patients/${patient.id}`}
                className="block truncate font-semibold text-slate-900 hover:text-primary-600"
              >
                {patient.full_name}
              </Link>
              <p className="text-xs text-slate-500">{patient.patient_number}</p>
            </div>
            <PatientRowActions
              patient={patient}
              onDeactivate={onDeactivate}
              onActivate={onActivate}
            />
          </div>

          <div className="mt-3 grid grid-cols-2 gap-2 text-xs text-slate-600">
            <div>
              <span className="text-slate-400">Idade</span>
              <p className="font-medium">{age !== null ? `${age} anos` : "—"}</p>
            </div>
            <div>
              <span className="text-slate-400">Género</span>
              <p className="font-medium">
                {patient.gender ? PATIENT_GENDER_LABELS[patient.gender] : "—"}
              </p>
            </div>
            <div>
              <span className="text-slate-400">Telefone</span>
              <p className="font-medium">{patient.phone ?? "—"}</p>
            </div>
            <div>
              <span className="text-slate-400">Última visita</span>
              <p className="font-medium">{formatDisplayDateTime(patient.updated_at)}</p>
            </div>
          </div>

          <div className="mt-3">
            <Badge variant={patient.is_active ? "success" : "default"}>
              {patient.is_active ? "Ativo" : "Inativo"}
            </Badge>
          </div>
        </div>
      </div>
    </article>
  );
}

export const PatientMobileCard = memo(PatientMobileCardComponent);
