import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { Badge, Card, ErrorState, LoadingState } from "@/design-system";
import { AllergyAlertBanner } from "@/features/patients/components/AllergyAlertBanner";
import { PatientHeader } from "@/features/patients/components/PatientHeader";
import { PatientSubNav } from "@/features/patients/components/PatientSubNav";
import {
  DOCUMENT_TYPE_LABELS,
  EMERGENCY_RELATIONSHIP_LABELS,
  PATIENT_GENDER_LABELS,
} from "@/constants/patients";
import { patientsService } from "@/services/patients";
import { formatDisplayDate } from "@/utils/date";

export function PatientDetailPage() {
  const { id } = useParams();
  const patientId = Number(id);

  const { data: patient, isLoading, isError, refetch } = useQuery({
    queryKey: ["patient", id],
    queryFn: () => patientsService.get(patientId),
  });

  const { data: allergiesData } = useQuery({
    queryKey: ["patient-allergies", id],
    queryFn: () => patientsService.listAllergies(patientId),
    enabled: Boolean(id),
  });

  if (isLoading) return <LoadingState message="A carregar ficha do paciente..." />;
  if (isError || !patient) {
    return <ErrorState message="Não foi possível carregar o paciente." onRetry={() => void refetch()} />;
  }

  const allergies = allergiesData?.results ?? [];

  return (
    <div className="space-y-6">
      <PatientHeader patient={patient} />
      <PatientSubNav />
      <AllergyAlertBanner allergies={allergies} />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Dados pessoais">
          <dl className="grid gap-3 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Documento</dt>
              <dd className="text-right text-slate-900">
                {patient.document_type ? DOCUMENT_TYPE_LABELS[patient.document_type] : "—"}{" "}
                {patient.document_number ?? ""}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Género</dt>
              <dd>{patient.gender ? PATIENT_GENDER_LABELS[patient.gender] : "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Data de nascimento</dt>
              <dd>{formatDisplayDate(patient.birth_date)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Idade</dt>
              <dd>{patient.age ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Nacionalidade</dt>
              <dd>{patient.nationality ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Profissão</dt>
              <dd>{patient.occupation ?? "—"}</dd>
            </div>
          </dl>
        </Card>

        <Card title="Contactos">
          <dl className="grid gap-3 text-sm">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Telefone</dt>
              <dd>{patient.phone ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">E-mail</dt>
              <dd>{patient.email ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Morada</dt>
              <dd className="text-right">
                {[patient.address_street, patient.address_city, patient.address_region]
                  .filter(Boolean)
                  .join(", ") || "—"}
              </dd>
            </div>
          </dl>
        </Card>

        <Card title="Resumo clínico">
          <div className="flex flex-wrap gap-2">
            <Badge variant="info">{patient.allergies_count ?? 0} alergias</Badge>
            <Badge variant="info">{patient.chronic_diseases_count ?? 0} doenças crónicas</Badge>
          </div>
        </Card>

        <Card title="Contactos de emergência">
          {patient.emergency_contacts && patient.emergency_contacts.length > 0 ? (
            <ul className="space-y-3 text-sm">
              {patient.emergency_contacts.map((contact) => (
                <li key={contact.id} className="rounded-lg border border-slate-200 p-3">
                  <div className="font-medium text-slate-900">{contact.name}</div>
                  <div className="text-slate-600">
                    {EMERGENCY_RELATIONSHIP_LABELS[contact.relationship]} · {contact.phone}
                  </div>
                  {contact.is_primary && <Badge variant="success">Principal</Badge>}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">Sem contactos registados.</p>
          )}
        </Card>
      </div>
    </div>
  );
}
