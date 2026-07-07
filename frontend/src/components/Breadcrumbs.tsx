import { Link, useLocation } from "react-router-dom";

const rotulos: Record<string, string> = {
  patients: "Pacientes",
  reception: "Receção",
  appointments: "Consultas",
  laboratory: "Laboratório",
  billing: "Faturação",
  finance: "Financeiro",
  reports: "Relatórios",
  settings: "Configurações",
  doctor: "Médico",
  notifications: "Notificações",
};

export function Breadcrumbs() {
  const location = useLocation();
  const partes = location.pathname.split("/").filter(Boolean);

  if (!partes.length) return null;

  let caminho = "";
  return (
    <nav aria-label="Navegação" className="mb-4 text-sm text-slate-500">
      <Link to="/" className="hover:text-primary-700">
        Início
      </Link>
      {partes.map((parte, i) => {
        caminho += `/${parte}`;
        const label = rotulos[parte] ?? parte;
        const ultimo = i === partes.length - 1;
        return (
          <span key={caminho}>
            {" / "}
            {ultimo ? (
              <span className="font-medium text-slate-700">{label}</span>
            ) : (
              <Link to={caminho} className="hover:text-primary-700">
                {label}
              </Link>
            )}
          </span>
        );
      })}
    </nav>
  );
}
