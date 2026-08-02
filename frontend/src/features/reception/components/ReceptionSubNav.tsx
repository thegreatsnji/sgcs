import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

const links = [
  { to: "/reception", label: UI_COPY.nav.dashboard, end: true },
  { to: "/reception/check-in", label: UI_COPY.nav.checkIn },
  { to: "/reception/queue", label: UI_COPY.nav.queue },
  { to: "/reception/referrals", label: UI_COPY.nav.referrals },
];

export function ReceptionSubNav() {
  return <PillSubNav tabs={links} ariaLabel="Navegação da recepção" />;
}
