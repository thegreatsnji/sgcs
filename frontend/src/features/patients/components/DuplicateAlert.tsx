import { Link } from "react-router-dom";

import { Button } from "@/design-system";
import type { DuplicateMatch } from "@/types/patient";

interface DuplicateAlertProps {
  matches: DuplicateMatch[];
}

export function DuplicateAlert({ matches }: DuplicateAlertProps) {
  if (matches.length === 0) return null;

  return (
    <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
      <p className="text-sm font-semibold text-amber-900">Pode já existir um utente com estes dados.</p>
      <p className="mt-1 text-sm text-amber-800">
        Verifique a ficha existente ou continue o registo se for outro utente.
      </p>
      <ul className="mt-3 space-y-2">
        {matches.map((match) => (
          <li
            key={match.id}
            className="flex flex-wrap items-center justify-between gap-2 rounded-md bg-white/70 px-3 py-2 text-sm"
          >
            <span>
              {match.full_name} · {match.patient_number} · {match.birth_date}
            </span>
            <Link to={`/patients/${match.id}`}>
              <Button size="sm" variant="outline">
                Ver utente existente
              </Button>
            </Link>
          </li>
        ))}
      </ul>
      <p className="mt-3 text-xs text-amber-700">
        Continuar registo está disponível — o aviso não bloqueia o formulário.
      </p>
    </div>
  );
}
