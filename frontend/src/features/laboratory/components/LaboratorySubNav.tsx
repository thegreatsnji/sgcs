import { PillSubNav } from "@/components/layout/PillSubNav";

const tabs = [
  { to: "/laboratory", label: "Painel", end: true },
  { to: "/laboratory/pending", label: "Pendentes" },
  { to: "/laboratory/today", label: "Processamento" },
  { to: "/laboratory/collection", label: "Colheitas" },
  { to: "/laboratory/results", label: "Resultados" },
  { to: "/laboratory/results/history", label: "Histórico" },
];

export function LaboratorySubNav() {
  return <PillSubNav tabs={tabs} ariaLabel="Navegação do laboratório" />;
}
