import { Outlet } from "react-router-dom";

import { PillSubNav } from "@/components/layout/PillSubNav";
import { UI_COPY } from "@/constants/uiCopy";

const links = [
  { to: "/admin/dashboard", label: UI_COPY.nav.dashboard },
  { to: "/admin/users", label: UI_COPY.nav.users },
  { to: "/admin/permissions", label: "Permissões" },
  { to: "/admin/groups", label: "Grupos" },
  { to: "/admin/audit", label: UI_COPY.nav.audit },
  { to: "/admin/profile", label: "Meu perfil" },
];

export function AdminLayout() {
  return (
    <div className="space-y-6">
      <PillSubNav tabs={links} ariaLabel="Administração do sistema" />
      <Outlet />
    </div>
  );
}
