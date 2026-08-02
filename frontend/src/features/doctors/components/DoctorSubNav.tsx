import { PillSubNav } from "@/components/layout/PillSubNav";

const tabs = [
  { to: "/doctor", label: "Painel", end: true },
  { to: "/doctor/prescriptions", label: "Prescrições" },
  { to: "/doctor/treatments", label: "Tratamentos" },
  { to: "/doctor/evolution", label: "Evolução clínica" },
  { to: "/doctor/history", label: "Histórico" },
  { to: "/doctor/discharge", label: "Alta médica" },
];

export function DoctorSubNav() {
  return <PillSubNav tabs={tabs} ariaLabel="Navegação médica" />;
}
