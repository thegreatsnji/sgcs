import { Link } from "react-router-dom";

import { Badge, Card } from "@/design-system";
import {
  DOCUMENT_TYPE_LABELS,
  EMERGENCY_RELATIONSHIP_LABELS,
  PATIENT_GENDER_LABELS,
} from "@/constants/patients";
import type { PatientAllergy, PatientDetail } from "@/types/patient";
import { formatDisplayDate } from "@/utils/date";

interface PatientOverviewContentProps {
  patient: PatientDetail;
  allergies: PatientAllergy[];
}

export function PatientOverviewContent({ patient, allergies }: PatientOverviewContentProps) {
  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <Card title="Resumo clínico">
          <div className="flex flex-wrap gap-2">
            <Badge variant="info">{patient.allergies_count ?? 0} alergias</Badge>
            <Badge variant="info">{patient.chronic_diseases_count ?? 0} doenças crónicas</Badge>
          </div>
          {allergies.length > 0 && (
            <p className="mt-3 text-sm text-slate-600">
              Alergias registadas: {allergies.map((a) => a.allergen).join(", ")}
            </p>
          )}
          <Link
            to={`/patients/${patient.id}/clinical`}
            className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Ver ficha clínica completa →
          </Link>
        </Card>

        <Card title="Linha do tempo">
          <p className="text-sm text-slate-600">
            Consulte o histórico completo de eventos clínicos e administrativos.
          </p>
          <Link
            to={`/patients/${patient.id}/history`}
            className="mt-4 inline-block text-sm font-medium text-primary-600 hover:text-primary-700"
          >
            Ver histórico →
          </Link>
        </Card>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Dados pessoais">
          <dl className="grid gap-4 text-sm">
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">Documento</dt>
              <dd className="text-right font-medium text-slate-900">
                {patient.document_type ? DOCUMENT_TYPE_LABELS[patient.document_type] : "—"}{" "}
                {patient.document_number ?? ""}
              </dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">Género</dt>
              <dd className="font-medium">{patient.gender ? PATIENT_GENDER_LABELS[patient.gender] : "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">Data de nascimento</dt>
              <dd className="font-medium">{formatDisplayDate(patient.birth_date)}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">Idade</dt>
              <dd className="font-medium">{patient.age ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">Nacionalidade</dt>
              <dd className="font-medium">{patient.nationality ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Profissão</dt>
              <dd className="font-medium">{patient.occupation ?? "—"}</dd>
            </div>
          </dl>
        </Card>

        <Card title="Morada e contactos">
          <dl className="grid gap-4 text-sm">
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">Telefone</dt>
              <dd className="font-medium">{patient.phone ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4 border-b border-slate-50 pb-3">
              <dt className="text-slate-500">E-mail</dt>
              <dd className="font-medium">{patient.email ?? "—"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Morada</dt>
              <dd className="text-right font-medium">
                {[patient.address_street, patient.address_city, patient.address_region]
                  .filter(Boolean)
                  .join(", ") || "—"}
              </dd>
            </div>
          </dl>
        </Card>
      </div>

      <Card title="Contactos de emergência">
        {patient.emergency_contacts && patient.emergency_contacts.length > 0 ? (
          <ul className="divide-y divide-slate-100">
            {patient.emergency_contacts.map((contact) => (
              <li key={contact.id} className="flex items-start justify-between gap-4 py-4 first:pt-0 last:pb-0">
                <div>
                  <p className="font-medium text-slate-900">{contact.name}</p>
                  <p className="text-sm text-slate-600">
                    {EMERGENCY_RELATIONSHIP_LABELS[contact.relationship]} · {contact.phone}
                  </p>
                  {contact.email && <p className="text-sm text-slate-500">{contact.email}</p>}
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
  );
}
