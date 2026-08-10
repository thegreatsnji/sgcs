import { Link } from "react-router-dom";

import { RoleDashboardHero } from "@/components/dashboards/RoleDashboardHero";
import { TriageCheckInWizard } from "@/features/reception/components/TriageCheckInWizard";
import { Card } from "@/design-system";

export function NurseTriagePage() {
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <RoleDashboardHero
        tone="teal"
        eyebrow="Enfermagem"
        title="Triagem clínica"
        description="Pesquise o utente, registe sinais vitais e prioridade. A receção trata do pagamento depois."
        primaryAction={{ to: "/reception/queue", label: "Fila de espera" }}
        secondaryAction={{ to: "/dashboard/nurse", label: "Painel" }}
      />

      <Card title="Registo de triagem" description="Após concluir, o utente entra na fila para a receção.">
        <TriageCheckInWizard />
      </Card>

      <p className="text-center text-xs text-text-muted">
        Precisa de marcar consulta?{" "}
        <Link to="/appointments" className="font-semibold text-primary-600 hover:text-primary-700">
          Abrir agenda
        </Link>
      </p>
    </div>
  );
}
