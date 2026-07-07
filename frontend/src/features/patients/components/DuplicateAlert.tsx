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
      <p className="text-sm font-semibold text-amber-900">Possíveis duplicados encontrados</p>
      <p className="mt-1 text-sm text-amber-800">
        Verifique se o paciente já está registado antes de continuar.
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
                Ver ficha
              </Button>
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
