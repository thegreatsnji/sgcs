import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/reception", label: "Painel", exact: true },
  { to: "/reception/check-in", label: "Check-in" },
  { to: "/reception/queue", label: "Fila de espera" },
  { to: "/reception/referrals", label: "Encaminhamentos" },
];

export function ReceptionSubNav() {
  const location = useLocation();

  return (
    <nav className="flex flex-wrap gap-2 border-b border-slate-200 pb-3">
      {links.map((link) => {
        const isActive = link.exact
          ? location.pathname === link.to
          : location.pathname.startsWith(link.to);
        return (
          <Link
            key={link.to}
            to={link.to}
            className={`rounded-lg px-3 py-1.5 text-sm font-medium transition ${
              isActive
                ? "bg-primary-600 text-white"
                : "text-slate-600 hover:bg-slate-100 hover:text-primary-700"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
