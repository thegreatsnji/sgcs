import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/admin/dashboard", label: "Dashboard" },
  { to: "/admin/users", label: "Utilizadores" },
  { to: "/admin/permissions", label: "Permissões" },
  { to: "/admin/groups", label: "Grupos" },
  { to: "/admin/audit", label: "Auditoria" },
  { to: "/admin/profile", label: "Meu Perfil" },
];

export function AdminLayout() {
  return (
    <div className="space-y-6">
      <nav className="flex flex-wrap gap-2 rounded-xl border border-slate-200 bg-white p-2 shadow-sm">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              `rounded-lg px-4 py-2 text-sm font-medium transition ${
                isActive
                  ? "bg-primary-600 text-white"
                  : "text-slate-600 hover:bg-slate-100"
              }`
            }
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
