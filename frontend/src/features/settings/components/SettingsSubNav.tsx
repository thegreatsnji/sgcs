import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

const tabs = [
  { to: "/settings", label: UI_COPY.nav.dashboard, end: true },
  { to: "/settings/clinic", label: "Clínica" },
  { to: "/settings/departments", label: "Departamentos" },
  { to: "/settings/specialties", label: "Especialidades" },
  { to: "/settings/medicos", label: "Médicos" },
  { to: "/settings/security", label: "Segurança" },
  { to: "/settings/feature-flags", label: UI_COPY.nav.featureFlags },
  { to: "/settings/system", label: "Sistema" },
];

export function SettingsSubNav() {
  return <PillSubNav tabs={tabs} ariaLabel="Navegação de definições" />;
}
