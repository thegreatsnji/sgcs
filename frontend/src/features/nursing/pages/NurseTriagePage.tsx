import { useSearchParams } from "react-router-dom";

import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
import { TriageCheckInWizard } from "@/features/reception/components/TriageCheckInWizard";
import { Card } from "@/design-system";

export function NurseTriagePage() {
  const [searchParams] = useSearchParams();
  const patientId = Number(searchParams.get("paciente")) || null;

  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <RoleDashboardHero
        tone="teal"
        eyebrow="Enfermagem"
        title="Triagem clínica"
        description="Pesquise o utente, registe sinais vitais e prioridade. O médico vê os sinais na consulta."
        primaryAction={{ to: "/dashboard/nurse", label: "Painel" }}
      />

      <Card
        title="Registo de triagem"
        description="Após guardar, o utente entra na fila. A Receção trata pagamento e encaminhamento."
      >
        <TriageCheckInWizard
          initialPatientId={patientId}
          nursingMode
        />
      </Card>
    </div>
  );
}
