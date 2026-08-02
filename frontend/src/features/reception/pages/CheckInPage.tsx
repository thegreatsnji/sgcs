import { TriageCheckInWizard } from "@/features/reception/components/TriageCheckInWizard";
import { ReceptionSubNav } from "@/features/reception/components/ReceptionSubNav";
import { PageHeader } from "@/components/layout/PageHeader";

export function CheckInPage() {
  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Receção"
        title="Triagem"
        description="Pesquise o paciente, registe novos utentes e defina a prioridade de atendimento."
      />

      <ReceptionSubNav />

      <div className="max-w-4xl">
        <TriageCheckInWizard />
      </div>
    </div>
  );
}
