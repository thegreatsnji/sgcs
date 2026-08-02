import { Link, useLocation } from "react-router-dom";

const links = [
  { to: "/consultations", label: "Painel", exact: true },
  { to: "/consultations/queue", label: "Fila médica" },
  { to: "/consultations/history", label: "Histórico" },
];

export function ConsultationSubNav() {
  const location = useLocation();

  return (
    <nav
      className="flex flex-wrap gap-1 rounded-2xl border border-slate-200/80 bg-white p-1.5 shadow-sm"
      aria-label="Navegação de consultas médicas"
    >
      {links.map((link) => {
        const isActive = link.exact
          ? location.pathname === link.to
          : location.pathname.startsWith(link.to);
        return (
          <Link
            key={link.to}
            to={link.to}
            className={`rounded-xl px-4 py-2.5 text-sm font-medium transition focus-ring ${
              isActive
                ? "bg-primary-600 text-white shadow-md shadow-primary-600/20"
                : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
            }`}
          >
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}
