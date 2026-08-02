import { memo } from "react";
import { Link } from "react-router-dom";

import { Avatar, Badge } from "@/design-system";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import type { PatientListItem } from "@/types/patient";
import { formatDisplayDateTime } from "@/utils/date";

import { PatientRowActions } from "./PatientRowActions";
import { getPatientAge } from "../utils/patientUtils";

interface PatientsTableProps {
  patients: PatientListItem[];
  onDeactivate?: (patient: PatientListItem) => void;
  onActivate?: (id: number) => void;
}

function PatientsTableComponent({ patients, onDeactivate, onActivate }: PatientsTableProps) {
  return (
    <div className="hidden overflow-hidden rounded-2xl border border-slate-200/80 md:block">
      <div className="overflow-x-auto">
        <table className="min-w-full text-sm">
          <thead className="sticky top-0 z-10 border-b border-slate-200 bg-slate-50/95 backdrop-blur-sm">
            <tr>
              {["Paciente", "N.º Processo", "Idade", "Género", "Telefone", "Última visita", "Estado", ""].map(
                (header) => (
                  <th
                    key={header || "actions"}
                    scope="col"
                    className="px-4 py-3.5 text-left text-xs font-semibold tracking-wide text-slate-500 uppercase first:pl-6 last:pr-6"
                  >
                    {header}
                  </th>
                ),
              )}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {patients.map((patient) => {
              const age = getPatientAge(patient.birth_date);
              return (
                <tr key={patient.id} className="transition hover:bg-slate-50/80">
                  <td className="px-4 py-3.5 pl-6">
                    <Link
                      to={`/patients/${patient.id}`}
                      className="flex items-center gap-3 focus-ring rounded-lg"
                    >
                      <Avatar name={patient.full_name} size="sm" />
                      <span className="font-medium text-slate-900 hover:text-primary-600">
                        {patient.full_name}
                      </span>
                    </Link>
                  </td>
                  <td className="px-4 py-3.5 font-mono text-xs text-slate-600">{patient.patient_number}</td>
                  <td className="px-4 py-3.5 text-slate-700">{age !== null ? age : "—"}</td>
                  <td className="px-4 py-3.5 text-slate-700">
                    {patient.gender ? PATIENT_GENDER_LABELS[patient.gender] : "—"}
                  </td>
                  <td className="px-4 py-3.5 text-slate-700">{patient.phone ?? "—"}</td>
                  <td className="px-4 py-3.5 text-slate-500">
                    {formatDisplayDateTime(patient.updated_at)}
                  </td>
                  <td className="px-4 py-3.5">
                    <Badge variant={patient.is_active ? "success" : "default"}>
                      {patient.is_active ? "Ativo" : "Inativo"}
                    </Badge>
                  </td>
                  <td className="px-4 py-3.5 pr-6 text-right">
                    <PatientRowActions
                      patient={patient}
                      onDeactivate={onDeactivate}
                      onActivate={onActivate}
                    />
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export const PatientsTable = memo(PatientsTableComponent);
