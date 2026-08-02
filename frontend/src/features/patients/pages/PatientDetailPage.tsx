import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";

import { ErrorState, LoadingState } from "@/design-system";
import { AllergyAlertBanner } from "@/features/patients/components/AllergyAlertBanner";
import { PatientOverviewContent } from "@/features/patients/components/PatientOverviewContent";
import { PatientProfileShell } from "@/features/patients/components/PatientProfileShell";
import { PatientTimeline } from "@/features/patients/components/PatientTimeline";
import { patientsService } from "@/services/patients";

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
    <PatientProfileShell patient={patient}>
      <AllergyAlertBanner allergies={allergies} />
      <PatientOverviewContent patient={patient} allergies={allergies} />
      <section className="mt-8" aria-labelledby="patient-timeline-heading">
        <h2 id="patient-timeline-heading" className="mb-4 text-lg font-semibold text-text">
          Linha temporal
        </h2>
        <PatientTimeline patientId={patient.id} />
      </section>
    </PatientProfileShell>
  );
}
