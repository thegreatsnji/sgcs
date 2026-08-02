import { Link } from "react-router-dom";

import { Card } from "@/design-system";

export function NurseRoleDashboardPage() {
  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-slate-200/80 bg-gradient-to-br from-teal-600 to-slate-900 p-6 text-white shadow-lg sm:p-8">
        <p className="text-xs font-semibold tracking-widest text-teal-100 uppercase">Enfermagem</p>
        <h1 className="mt-2 text-2xl font-bold tracking-tight sm:text-3xl">Painel de Enfermagem</h1>
        <p className="mt-2 text-sm text-teal-100">
          Acompanhamento de pacientes e apoio às consultas em curso.
        </p>
      </div>

      <Card title="Acções rápidas">
        <div className="grid gap-2 sm:grid-cols-2">
          <Link
            to="/patients"
            className="rounded-xl bg-primary-600 px-4 py-3 text-center text-sm font-medium text-white hover:bg-primary-700"
          >
            Pacientes
          </Link>
          <Link
            to="/appointments"
            className="rounded-xl border border-slate-200 px-4 py-3 text-center text-sm font-medium text-slate-700 hover:bg-slate-50"
          >
            Agenda de consultas
          </Link>
        </div>
      </Card>
    </div>
  );
}
