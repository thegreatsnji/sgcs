import { CheckInForm } from "@/features/reception/components/CheckInForm";
import { ReceptionSubNav } from "@/features/reception/components/ReceptionSubNav";

export function CheckInPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">Check-in de paciente</h2>
        <p className="mt-1 text-slate-600">Registe a chegada do utente e adicione-o à fila de espera.</p>
      </div>

      <ReceptionSubNav />

      <div className="max-w-xl">
        <CheckInForm />
      </div>
    </div>
  );
}
