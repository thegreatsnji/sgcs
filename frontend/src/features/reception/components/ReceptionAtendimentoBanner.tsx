import { Link } from "react-router-dom";

export function ReceptionAtendimentoBanner({ retorno }: { retorno: string | null }) {
  if (!retorno) return null;

  let href = retorno;
  try {
    href = decodeURIComponent(retorno);
  } catch {
    href = retorno;
  }

  return (
    <div
      className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 dark:border-emerald-800/50 dark:bg-emerald-950/40"
      role="status"
    >
      <p className="text-sm font-medium text-emerald-900 dark:text-emerald-100">
        Atendimento na receção em curso
      </p>
      <Link
        to={href}
        className="text-sm font-semibold text-emerald-800 underline-offset-2 hover:underline dark:text-emerald-200"
      >
        ← Voltar ao passo de pagamento
      </Link>
    </div>
  );
}
