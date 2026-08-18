import { Link } from "react-router-dom";
import { useMutation, useQueryClient } from "@tanstack/react-query";

import { Avatar, Badge, Button, useToast } from "@/design-system";
import {
  EMERGENCY_RELATIONSHIP_LABELS,
  PATIENT_GENDER_LABELS,
} from "@/constants/patients";
import { usePermissions } from "@/hooks/usePermissions";
import { patientsService } from "@/services/patients";
import type { PatientDetail } from "@/types/patient";
import { getApiErrorMessage } from "@/utils/api-error";
import { formatDisplayDate } from "@/utils/date";

import { PatientSubNav } from "./PatientSubNav";

interface PatientProfileShellProps {
  patient: PatientDetail;
  children: React.ReactNode;
}

export function PatientProfileShell({ patient, children }: PatientProfileShellProps) {
  const { hasPermission } = usePermissions();
  const { showToast } = useToast();
  const queryClient = useQueryClient();
  const isHistorical = patient.import_origin === "MIGRACAO_EXCEL_SAUVIDA";
  const needsConfirmation = isHistorical && !patient.dados_verificados;

  const confirmMutation = useMutation({
    mutationFn: () => patientsService.confirmImportedData(patient.id),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["patient", String(patient.id)] });
      showToast("Dados verificados", "success");
    },
    onError: (error) => {
      showToast(getApiErrorMessage(error), "error");
    },
  });

  const primaryContact = patient.emergency_contacts?.find((c) => c.is_primary) ?? patient.emergency_contacts?.[0];

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
    <div className="space-y-6">
      {needsConfirmation && (
        <div
          className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-950"
          role="status"
        >
          <p>
            Dados provenientes do registo anterior da clínica. Confirme as informações do utente.
          </p>
          {hasPermission("patients.edit") && (
            <Button
              type="button"
              variant="outline"
              className="border-amber-300 bg-white"
              disabled={confirmMutation.isPending}
              onClick={() => confirmMutation.mutate()}
            >
              Confirmar dados
            </Button>
          )}
        </div>
      )}
      {isHistorical && patient.dados_verificados && (
        <p className="text-sm text-slate-600" role="status">
          Dados verificados
        </p>
      )}
      <div className="grid gap-6 xl:grid-cols-[300px_1fr]">
        {/* Left panel — patient identity */}
        <aside className="space-y-4">
          <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-sm">
            <div className="flex flex-col items-center text-center">
              <Avatar
                name={patient.full_name}
                src={patient.primary_photo_url ?? undefined}
                size="xl"
              />
              <h1 className="mt-4 text-xl font-bold text-slate-900">{patient.full_name}</h1>
              <p className="mt-1 font-mono text-xs text-slate-500">{patient.patient_number}</p>
              <div className="mt-3 flex flex-wrap justify-center gap-2">
                <Badge variant={patient.is_active ? "success" : "default"}>
                  {patient.is_active ? "Ativo" : "Inativo"}
                </Badge>
                {patient.gender && (
                  <Badge variant="info">{PATIENT_GENDER_LABELS[patient.gender]}</Badge>
                )}
                {patient.age !== undefined && <Badge variant="default">{patient.age} anos</Badge>}
              </div>
            </div>

            <dl className="mt-6 space-y-4 border-t border-slate-100 pt-6 text-sm">
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-400 uppercase">Telefone</dt>
                <dd className="mt-1 font-medium text-slate-900">{patient.phone ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-400 uppercase">E-mail</dt>
                <dd className="mt-1 break-all font-medium text-slate-900">{patient.email ?? "—"}</dd>
              </div>
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-400 uppercase">Nascimento</dt>
                <dd className="mt-1 font-medium text-slate-900">
                  {formatDisplayDate(patient.birth_date)}
                </dd>
              </div>
              <div>
                <dt className="text-xs font-semibold tracking-wide text-slate-400 uppercase">
                  Contacto de emergência
                </dt>
                <dd className="mt-1">
                  {primaryContact ? (
                    <>
                      <p className="font-medium text-slate-900">{primaryContact.name}</p>
                      <p className="text-slate-600">
                        {EMERGENCY_RELATIONSHIP_LABELS[primaryContact.relationship]} · {primaryContact.phone}
                      </p>
                    </>
                  ) : (
                    <span className="text-slate-500">Sem contacto registado</span>
                  )}
                </dd>
              </div>
            </dl>

            <div className="mt-6 flex flex-col gap-2 border-t border-slate-100 pt-6">
              {hasPermission("patients.edit") && (
                <Link to={`/patients/${patient.id}/edit`}>
                  <Button variant="outline" className="w-full">
                    Editar paciente
                  </Button>
                </Link>
              )}
              {hasPermission("patients.print") && (
                <Button variant="ghost" className="w-full" onClick={() => void handlePrint()}>
                  Imprimir ficha
                </Button>
              )}
            </div>
          </div>
        </aside>

        {/* Right panel — tabs + content */}
        <div className="min-w-0 space-y-6">
          <PatientSubNav />
          {children}
        </div>
      </div>
    </div>
  );
}
