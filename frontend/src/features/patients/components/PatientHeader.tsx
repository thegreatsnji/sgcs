import { Link } from "react-router-dom";

import { Avatar, Badge, Button, useToast } from "@/design-system";
import { PATIENT_GENDER_LABELS } from "@/constants/patients";
import { usePermissions } from "@/hooks/usePermissions";
import { patientsService } from "@/services/patients";
import type { PatientDetail } from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate } from "@/utils/date";

interface PatientHeaderProps {
  patient: PatientDetail;
}

export function PatientHeader({ patient }: PatientHeaderProps) {
  const { hasPermission } = usePermissions();
  const { showToast } = useToast();

  const handlePrint = async () => {
    try {
      const result = await patientsService.print(patient.id);
      showToast(
        result.ready ? "Impressão iniciada." : "Impressão de ficha em desenvolvimento.",
        result.ready ? "success" : "info",
      );
    } catch (error) {
      showToast(getApiErrorMessage(error), "error");
    }
  };

  return (
    <div className="flex flex-wrap items-start justify-between gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="flex items-start gap-4">
        <Avatar
          name={patient.full_name}
          src={patient.primary_photo_url ?? undefined}
          size="lg"
        />
        <div>
          <h2 className="text-2xl font-bold text-slate-900">{patient.full_name}</h2>
          <p className="text-sm text-slate-500">N.º processo: {patient.patient_number}</p>
          <div className="mt-2 flex flex-wrap gap-2">
            <Badge variant={patient.is_active ? "success" : "default"}>
              {patient.is_active ? "Ativo" : "Inativo"}
            </Badge>
            {patient.gender && (
              <Badge variant="default">{PATIENT_GENDER_LABELS[patient.gender]}</Badge>
            )}
            {patient.age !== undefined && <Badge variant="default">{patient.age} anos</Badge>}
          </div>
          <p className="mt-2 text-sm text-slate-600">
            {patient.phone ?? "—"} · {patient.email ?? "—"} · Nasc.{" "}
            {formatDisplayDate(patient.birth_date)}
          </p>
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        {hasPermission("patients.print") && (
          <Button variant="outline" onClick={() => void handlePrint()}>
            Imprimir ficha
          </Button>
        )}
        {hasPermission("patients.edit") && (
          <Link to={`/patients/${patient.id}/edit`}>
            <Button variant="outline">Editar</Button>
          </Link>
        )}
      </div>
    </div>
  );
}
